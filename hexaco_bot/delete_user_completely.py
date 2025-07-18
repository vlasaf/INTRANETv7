import sqlite3
import sys
import os
from pathlib import Path

def delete_user_completely(user_id):
    """
    Полностью удаляет пользователя из всех таблиц базы данных
    и связанные файлы отчетов и профилей
    
    Args:
        user_id (int): ID пользователя Telegram
    """
    db_path = "data/hexaco_bot.db"
    
    # Таблицы для очистки (правильная структура БД)
    tables_to_clean = [
        "users",
        "test_sessions", 
        "results"
    ]
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Получаем информацию о пользователе для подтверждения
        cursor.execute("SELECT username, first_name, last_name FROM users WHERE user_id = ?", (user_id,))
        user_info = cursor.fetchone()
        
        if not user_info:
            print(f"❌ Пользователь с ID {user_id} не найден в базе данных")
            return
        
        username, first_name, last_name = user_info
        print(f"🔍 Найден пользователь: {username} ({first_name} {last_name})")
        
        # Подтверждение удаления
        confirm = input(f"⚠️  Вы уверены, что хотите ПОЛНОСТЬЮ удалить пользователя {user_id}? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Удаление отменено")
            return
        
        # Удаление из всех таблиц
        total_deleted = 0
        for table in tables_to_clean:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE user_id = ?", (user_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                cursor.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))
                print(f"✅ Удалено {count} записей из таблицы {table}")
                total_deleted += count
        
        conn.commit()
        
        # Удаление связанных файлов
        delete_user_files(user_id, username)
        
        print(f"🎉 Пользователь {user_id} полностью удален! Всего удалено записей: {total_deleted}")
        print("📝 Теперь пользователь начнет с самого начала при следующем /start")
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
    finally:
        conn.close()

def delete_user_files(user_id, username):
    """Удаляет файлы отчетов и профилей пользователя"""
    
    # Удаление файлов отчетов
    reports_dir = Path("user_reports")
    if reports_dir.exists():
        # Поиск файлов отчетов по username
        if username:
            safe_username = "".join(c if c.isalnum() else "_" for c in str(username))
            for report_file in reports_dir.glob(f"report_{safe_username}_*.json"):
                try:
                    report_file.unlink()
                    print(f"🗑️  Удален файл отчета: {report_file}")
                except Exception as e:
                    print(f"⚠️  Не удалось удалить файл отчета {report_file}: {e}")
    
    # Удаление файлов профилей
    profiles_dir = Path("user_profile")
    if profiles_dir.exists():
        profile_file = profiles_dir / f"{user_id}_profile.json"
        if profile_file.exists():
            try:
                profile_file.unlink()
                print(f"🗑️  Удален файл профиля: {profile_file}")
            except Exception as e:
                print(f"⚠️  Не удалось удалить файл профиля {profile_file}: {e}")

def main():
    if len(sys.argv) != 2:
        print("Использование: python delete_user_completely.py <user_id>")
        print("Пример: python delete_user_completely.py 456355303")
        sys.exit(1)
    
    try:
        user_id = int(sys.argv[1])
    except ValueError:
        print("❌ user_id должен быть числом")
        sys.exit(1)
    
    delete_user_completely(user_id)

if __name__ == "__main__":
    main()