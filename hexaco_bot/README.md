# HEXACO Telegram Bot

Telegram бот для проведения HEXACO личностного теста для внутренних сотрудников компании.

## Описание

Этот бот реализует полный HEXACO-PI-R тест с 100 вопросами и предоставляет детальную оценку личности по 6 основным факторам:
- Честность-Смирение (Honesty-Humility)
- Эмоциональность (Emotionality)  
- Экстраверсия (Extraversion)
- Доброжелательность (Agreeableness)
- Добросовестность (Conscientiousness)
- Открытость опыту (Openness)
- Альтруизм (Altruism)

## Требования

- Python 3.7+
- Windows 10+
- Токен Telegram бота

## Установка

1. Клонируйте проект:
```bash
git clone <repository-url>
cd hexaco_bot
```

2. Создайте виртуальное окружение:
```bash
python -m venv hexaco_bot_env
hexaco_bot_env\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте переменные окружения:
   - Скопируйте `env_example.txt` в `.env`
   - Добавьте ваш токен Telegram бота

5. Запустите бота:
```bash
python src/main.py
```

## Использование

1. Найдите бота в Telegram
2. Отправьте команду `/start`
3. Выберите пол (Мужской/Женский)
4. Введите имя и фамилию
5. Пройдите тест из 100 вопросов
6. Получите результаты HEXACO оценки

## Архитектура

- `src/handlers/` - Обработчики Telegram сообщений
- `src/session/` - Управление сессиями пользователей
- `src/scoring/` - Расчет HEXACO баллов
- `src/data/` - Работа с базой данных
- `src/utils/` - Вспомогательные утилиты
- `data/` - База данных SQLite
- `logs/` - Файлы логов
- `config/` - Конфигурационные файлы

## Разработка

Для разработки установите дополнительные зависимости:
```bash
pip install pytest pytest-cov
```

Запуск тестов:
```bash
pytest tests/
```

## Лицензия

Внутренний проект компании. 