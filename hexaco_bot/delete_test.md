# Памятка: Удаление данных теста из базы данных

## Для чего нужно
Иногда необходимо удалить данные о прохождении конкретного теста пользователем, чтобы:
- Перепройти тест заново
- Проверить обновленную логику скорера
- Исправить ошибки в ответах
- Тестировать новую функциональность

## Структура базы данных
База данных содержит следующие основные таблицы:
- `users` - основная информация о пользователях (имя, пол, PAEI, MBTI)
- `test_sessions` - сессии тестирования
- `results` - результаты тестов (все ответы хранятся в JSON формате в поле `responses`)

## Способы удаления

### 1. Через SQLite командную строку

```bash
# Открыть базу данных
sqlite3 data/hexaco_bot.db

# Посмотреть все таблицы
.tables

# Посмотреть структуру таблицы
.schema pid5bfm_responses

# Найти результаты тестов пользователя
SELECT * FROM results WHERE user_id = 456355303;

# Удалить результаты конкретного теста для пользователя
DELETE FROM results WHERE user_id = 456355303 AND test_type = 'pid5bfm';

# Проверить, что удалилось
SELECT * FROM results WHERE user_id = 456355303 AND test_type = 'pid5bfm';

# Выйти
.quit
```

### 2. Через Python скрипт

```python
import sqlite3

def delete_test_data(user_id, test_name):
    """
    Удаляет данные конкретного теста для пользователя
    
    Args:
        user_id (int): ID пользователя Telegram
        test_name (str): Название теста (hexaco, cdrisc, pid5bfm, panas, rfq, sds, self_efficacy, svs)
    """
    db_path = "data/hexaco_bot.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем, есть ли данные
        cursor.execute("SELECT COUNT(*) FROM results WHERE user_id = ? AND test_type = ?", (user_id, test_name))
        count_before = cursor.fetchone()[0]
        
        if count_before == 0:
            print(f"❌ Данные теста {test_name} для пользователя {user_id} не найдены")
            return
        
        # Удаляем данные
        cursor.execute("DELETE FROM results WHERE user_id = ? AND test_type = ?", (user_id, test_name))
        conn.commit()
        
        # Проверяем результат
        cursor.execute("SELECT COUNT(*) FROM results WHERE user_id = ? AND test_type = ?", (user_id, test_name))
        count_after = cursor.fetchone()[0]
        
        print(f"✅ Удалено {count_before} записей теста {test_name} для пользователя {user_id}")
        print(f"📊 Осталось записей: {count_after}")
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
    finally:
        conn.close()

# Пример использования
if __name__ == "__main__":
    # Удалить данные PID-5-BF+M для пользователя 456355303
    delete_test_data(456355303, "pid5bfm")
```

### 3. Через готовый скрипт

Создайте файл `delete_test_data.py`:

```python
#!/usr/bin/env python3
import sqlite3
import sys

def main():
    if len(sys.argv) != 3:
        print("Использование: python delete_test_data.py <user_id> <test_name>")
        print("Доступные тесты: hexaco, cdrisc, pid5bfm, panas, rfq, sds, self_efficacy, svs")
        sys.exit(1)
    
    user_id = int(sys.argv[1])
    test_name = sys.argv[2]
    
    valid_tests = ["hexaco", "cdrisc", "pid5bfm", "panas", "rfq", "sds", "self_efficacy", "svs"]
    if test_name not in valid_tests:
        print(f"❌ Неверное название теста. Доступные: {', '.join(valid_tests)}")
        sys.exit(1)
    
    delete_test_data(user_id, test_name)

if __name__ == "__main__":
    main()
```

Использование:
```bash
python delete_test_data.py 456355303 pid5bfm
```

## Полезные SQL запросы

### Посмотреть все тесты пользователя
```sql
-- Заменить 456355303 на нужный user_id
SELECT test_type, COUNT(*) as results_count, MAX(created_at) as last_completed
FROM results 
WHERE user_id = 456355303 
GROUP BY test_type
ORDER BY last_completed DESC;
```

### Найти user_id по username
```sql
-- Если нужно найти user_id по имени пользователя
SELECT user_id, username, first_name, last_name 
FROM users 
WHERE username LIKE '%alterneva%';
```

### Удалить все данные пользователя
```sql
-- ОСТОРОЖНО! Удаляет ВСЕ данные пользователя
DELETE FROM results WHERE user_id = 456355303;
DELETE FROM test_sessions WHERE user_id = 456355303;
-- Если нужно удалить только результаты тестов, но оставить пользователя:
-- DELETE FROM results WHERE user_id = 456355303;
```

## Безопасность

⚠️ **ВАЖНО**: Всегда делайте резервную копию базы данных перед удалением:

```bash
# Создать резервную копию
cp data/hexaco_bot.db data/hexaco_bot_backup_$(date +%Y%m%d_%H%M%S).db

# Или
sqlite3 data/hexaco_bot.db ".backup data/backup_$(date +%Y%m%d_%H%M%S).db"
```

## Проверка после удаления

После удаления данных теста:
1. Запустите бота
2. Попробуйте начать удаленный тест командой `/start`
3. Убедитесь, что тест начинается с первого вопроса
4. Проверьте, что новые ответы корректно сохраняются

## Часто используемые user_id

Для удобства, основные тестовые пользователи:
- `456355303` - alterneva (Юлия Егина)
- `270754721` - JuliaRumiantseva 
- `483307981` - vadimseichas
- `325613987` - TalanTalanT
- `983726381` - vandertea
- `55216352` - romen_panteleev

## Полное удаление пользователя (сброс к началу)

Если нужно полностью удалить пользователя, чтобы он начинал с самого начала (ввод имени, пола, PAEI, MBTI), выполните следующие действия:

### 1. Через SQLite командную строку

```bash
# Открыть базу данных
sqlite3 data/hexaco_bot.db

# Полное удаление пользователя (замените 456355303 на нужный user_id)
DELETE FROM users WHERE user_id = 456355303;
DELETE FROM test_sessions WHERE user_id = 456355303;
DELETE FROM results WHERE user_id = 456355303;
DELETE FROM hexaco_responses WHERE user_id = 456355303;
DELETE FROM cdrisc_responses WHERE user_id = 456355303;
DELETE FROM pid5bfm_responses WHERE user_id = 456355303;
DELETE FROM panas_responses WHERE user_id = 456355303;
DELETE FROM rfq_responses WHERE user_id = 456355303;
DELETE FROM sds_responses WHERE user_id = 456355303;
DELETE FROM self_efficacy_responses WHERE user_id = 456355303;
DELETE FROM svs_responses WHERE user_id = 456355303;

# Проверить, что пользователь полностью удален
SELECT * FROM users WHERE user_id = 456355303;

# Выйти
.quit
```

### 2. Через Python скрипт

Создайте файл `delete_user_completely.py`:

```python
#!/usr/bin/env python3
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
```

Использование:
```bash
python delete_user_completely.py 456355303
```

### 3. Быстрый SQL скрипт для полного удаления

```sql
-- ВНИМАНИЕ: Замените 456355303 на нужный user_id
-- Этот скрипт полностью удаляет пользователя из всех таблиц

-- Сохраните информацию о пользователе перед удалением (опционально)
SELECT 'Удаляем пользователя:', user_id, username, first_name, last_name, paei_index, mbti_type 
FROM users WHERE user_id = 456355303;

-- Удаление из всех таблиц
DELETE FROM users WHERE user_id = 456355303;
DELETE FROM test_sessions WHERE user_id = 456355303;
DELETE FROM results WHERE user_id = 456355303;

-- Проверка, что пользователь полностью удален
SELECT 'Проверка удаления - должно быть 0 записей:' as check_result;
SELECT COUNT(*) as users_table FROM users WHERE user_id = 456355303;
SELECT COUNT(*) as test_sessions_table FROM test_sessions WHERE user_id = 456355303;
SELECT COUNT(*) as results_table FROM results WHERE user_id = 456355303;
```

### 4. Что происходит после полного удаления

После полного удаления пользователя:

1. **При следующем /start** пользователь начнет с самого начала:
   - Ввод имени и фамилии
   - Выбор пола
   - Ввод PAEI-индекса
   - Выбор MBTI-типа

2. **Все тесты** будут доступны для прохождения заново

3. **Файлы отчетов и профилей** будут удалены (если используется Python скрипт)

### ⚠️ Важные предупреждения

- **Всегда делайте резервную копию** перед полным удалением пользователя
- **Это действие необратимо** - восстановить данные можно только из резервной копии
- **Проверьте user_id дважды** - удаление не того пользователя может привести к потере важных данных

### Создание резервной копии перед удалением

```bash
# Создать резервную копию с временной меткой
cp data/hexaco_bot.db data/hexaco_bot_backup_before_delete_$(date +%Y%m%d_%H%M%S).db

# Или через SQLite
sqlite3 data/hexaco_bot.db ".backup data/backup_before_delete_$(date +%Y%m%d_%H%M%S).db"
``` 