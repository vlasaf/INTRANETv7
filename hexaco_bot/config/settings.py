"""
Application configuration settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
# Get the directory of this file and go up one level to find .env
config_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(config_dir)
dotenv_path = os.path.join(project_dir, '.env')
load_dotenv(dotenv_path)

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', './data/hexaco_bot.db')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', './logs/bot.log')

# ChatGPT API Configuration
CHATGPT_API_KEY = os.getenv('CHATGPT_API_KEY')
# Опционально: добавить проверку, что ключ есть, если он строго необходим для всех функций
# if not CHATGPT_API_KEY:
#     raise ValueError("CHATGPT_API_KEY environment variable is required for psychoprofile generation")

# Application Configuration
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 86400))  # 24 hours
MAX_CONCURRENT_USERS = int(os.getenv('MAX_CONCURRENT_USERS', 50))

# HEXACO Test Configuration
TOTAL_QUESTIONS = 100
RESPONSE_SCALE = {
    1: "Совершенно не согласен",
    2: "Немного не согласен", 
    3: "Нейтрально, нет мнения",
    4: "Немного согласен",
    5: "Совершенно согласен"
}

# Telegram Bot Settings
POLLING_INTERVAL = 1  # seconds
REQUEST_TIMEOUT = 30  # seconds 