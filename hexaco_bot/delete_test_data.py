#!/usr/bin/env python3
"""
Скрипт для удаления данных конкретного теста из базы данных
Использование: python delete_test_data.py <user_id> <test_name>
"""

import sqlite3
import sys
import os
from datetime import datetime

def delete_test_data(user_id, test_name):
    """
    Удаляет данные конкретного теста для пользователя из таблицы results
    
    Args:
        user_id (int): ID пользователя Telegram
        test_name (str): Название теста (hexaco, cdrisc, pid5bfm, panas, rfq, sds, self_efficacy, svs, urica, dweck)
    """
    db_path = "data/hexaco_bot.db"
    
    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем, существует ли таблица results
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='results'")
        if not cursor.fetchone():
            print(f"❌ Таблица results не найдена в базе данных")
            return False
        
        # Проверяем, есть ли данные для этого теста
        cursor.execute("SELECT result_id, created_at FROM results WHERE user_id = ? AND test_type = ?", (user_id, test_name))
        test_records = cursor.fetchall()
        
        if not test_records:
            print(f"❌ Данные теста {test_name} для пользователя {user_id} не найдены")
            return False
        
        # Показываем что будет удалено
        print(f"🔍 Найдено {len(test_records)} записей теста {test_name} для пользователя {user_id}:")
        for result_id, created_at in test_records:
            print(f"  📋 ID: {result_id}, Дата: {created_at}")
        
        # Подтверждение удаления
        if len(sys.argv) < 4 or sys.argv[3] != "--force":
            confirm = input("❓ Вы уверены, что хотите удалить эти данные? (y/N): ")
            if confirm.lower() not in ['y', 'yes', 'да']:
                print("❌ Операция отменена")
                return False
        
        # Удаляем данные
        cursor.execute("DELETE FROM results WHERE user_id = ? AND test_type = ?", (user_id, test_name))
        deleted_count = cursor.rowcount
        conn.commit()
        
        # Проверяем результат
        cursor.execute("SELECT COUNT(*) FROM results WHERE user_id = ? AND test_type = ?", (user_id, test_name))
        count_after = cursor.fetchone()[0]
        
        print(f"✅ Удалено {deleted_count} записей теста {test_name} для пользователя {user_id}")
        print(f"📊 Осталось записей: {count_after}")
        
        if count_after == 0:
            print(f"🎯 Теперь пользователь {user_id} может пройти тест {test_name} заново")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False
    finally:
        conn.close()

def show_user_tests(user_id):
    """Показывает все тесты пользователя"""
    db_path = "data/hexaco_bot.db"
    
    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Получаем все тесты пользователя
        cursor.execute("SELECT test_type, COUNT(*) as count, MAX(created_at) as last_date FROM results WHERE user_id = ? GROUP BY test_type ORDER BY test_type", (user_id,))
        user_tests = cursor.fetchall()
        
        if not user_tests:
            print(f"❌ Данные пользователя {user_id} не найдены")
            return
        
        print(f"\n📊 Тесты пользователя {user_id}:")
        print("-" * 60)
        print(f"{'Тест':<15} {'Записей':<8} {'Последняя дата':<20} {'Статус':<10}")
        print("-" * 60)
        
        for test_type, count, last_date in user_tests:
            status = "✅ Пройден" if count > 0 else "❌ Не пройден"
            last_date_str = last_date if last_date else "Неизвестно"
            print(f"{test_type:<15} {count:<8} {last_date_str:<20} {status:<10}")
        
        print(f"\n📈 Всего тестов: {len(user_tests)}")
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
    finally:
        conn.close()

def show_test_details(user_id, test_name):
    """Показывает детали конкретного теста"""
    db_path = "data/hexaco_bot.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT result_id, created_at, scores_json FROM results WHERE user_id = ? AND test_type = ?", (user_id, test_name))
        records = cursor.fetchall()
        
        if not records:
            print(f"❌ Данные теста {test_name} для пользователя {user_id} не найдены")
            return
        
        print(f"\n🔍 Детали теста {test_name} для пользователя {user_id}:")
        print("-" * 60)
        
        for result_id, created_at, scores_json in records:
            print(f"📋 ID записи: {result_id}")
            print(f"📅 Дата создания: {created_at}")
            if scores_json:
                print(f"📊 Есть данные скоров: {len(scores_json)} символов")
            else:
                print(f"📊 Данные скоров: отсутствуют")
            print("-" * 30)
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
    finally:
        conn.close()

def backup_database():
    """Создает резервную копию базы данных"""
    db_path = "data/hexaco_bot.db"
    
    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"data/hexaco_bot_backup_{timestamp}.db"
    
    try:
        conn = sqlite3.connect(db_path)
        backup_conn = sqlite3.connect(backup_path)
        conn.backup(backup_conn)
        backup_conn.close()
        conn.close()
        
        print(f"✅ Резервная копия создана: {backup_path}")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка создания резервной копии: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("🔧 Скрипт для удаления данных теста из базы данных")
        print("\nИспользование:")
        print("  python delete_test_data.py <user_id> <test_name> [--force]")
        print("  python delete_test_data.py --show <user_id>")
        print("  python delete_test_data.py --details <user_id> <test_name>")
        print("  python delete_test_data.py --backup")
        print("\nДоступные тесты:")
        print("  hexaco, cdrisc, pid5bfm, panas, rfq, sds, self_efficacy, svs, urica, dweck")
        print("\nПримеры:")
        print("  python delete_test_data.py 456355303 pid5bfm")
        print("  python delete_test_data.py --show 456355303")
        print("  python delete_test_data.py --details 456355303 pid5bfm")
        print("  python delete_test_data.py --backup")
        sys.exit(1)
    
    # Показать тесты пользователя
    if sys.argv[1] == "--show":
        if len(sys.argv) < 3:
            print("❌ Укажите user_id")
            sys.exit(1)
        try:
            user_id = int(sys.argv[2])
            show_user_tests(user_id)
        except ValueError:
            print("❌ user_id должен быть числом")
            sys.exit(1)
        return
    
    # Показать детали теста
    if sys.argv[1] == "--details":
        if len(sys.argv) < 4:
            print("❌ Укажите user_id и test_name")
            sys.exit(1)
        try:
            user_id = int(sys.argv[2])
            test_name = sys.argv[3].lower()
            show_test_details(user_id, test_name)
        except ValueError:
            print("❌ user_id должен быть числом")
            sys.exit(1)
        return
    
    # Создать резервную копию
    if sys.argv[1] == "--backup":
        backup_database()
        return
    
    # Удалить данные теста
    if len(sys.argv) < 3:
        print("❌ Укажите user_id и test_name")
        sys.exit(1)
    
    try:
        user_id = int(sys.argv[1])
    except ValueError:
        print("❌ user_id должен быть числом")
        sys.exit(1)
    
    test_name = sys.argv[2].lower()
    
    valid_tests = ["hexaco", "cdrisc", "pid5bfm", "panas", "rfq", "sds", "self_efficacy", "svs", "urica", "dweck"]
    if test_name not in valid_tests:
        print(f"❌ Неверное название теста. Доступные: {', '.join(valid_tests)}")
        sys.exit(1)
    
    # Предложить создать резервную копию
    if len(sys.argv) < 4 or sys.argv[3] != "--force":
        backup_choice = input("💾 Создать резервную копию базы данных перед удалением? (Y/n): ")
        if backup_choice.lower() not in ['n', 'no', 'нет']:
            backup_database()
    
    success = delete_test_data(user_id, test_name)
    
    if success:
        print(f"\n🎯 Готово! Пользователь {user_id} может пройти тест {test_name} заново")
    else:
        print(f"\n❌ Не удалось удалить данные теста {test_name}")

if __name__ == "__main__":
    main() 