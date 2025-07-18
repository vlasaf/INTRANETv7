"""
Main application file for HEXACO Telegram Bot.
"""

import sys
import os

# Add the project root's parent directory to sys.path to allow absolute imports like 'from hexaco_bot.config...'
# os.path.dirname(__file__) is C:\проекты\INTRANETv4\hexaco_bot\src
# os.path.join(os.path.dirname(__file__), '..') is C:\проекты\INTRANETv4\hexaco_bot
# os.path.join(os.path.dirname(__file__), '..', '..') is C:\проекты\INTRANETv4
project_grandparent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_grandparent_dir not in sys.path:
    sys.path.insert(0, project_grandparent_dir)

import logging
import threading
import time
from telebot import TeleBot
from telebot.types import Message

from hexaco_bot.config.settings import BOT_TOKEN, LOG_LEVEL, LOG_FILE
from hexaco_bot.src.data.database import DatabaseManager
from hexaco_bot.src.handlers.start_handler import (
    StartHandler, 
    STATE_GENDER_SELECTION, 
    STATE_NAME_INPUT, 
    STATE_AWAIT_PAEI, 
    STATE_AWAIT_MBTI, 
    STATE_INITIAL_SETUP_COMPLETE
)
from hexaco_bot.src.handlers.question_handler import QuestionHandler
from hexaco_bot.src.session.session_manager import SessionManager

# Import report watcher for psychoprofile generation
# from hexaco_bot.src.psychoprofile.report_watcher import start_watching_background  # ВРЕМЕННО ОТКЛЮЧЕНО

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class HEXACOBot:
    """Main HEXACO Telegram Bot class."""
    
    def __init__(self):
        """Initialize bot with handlers and database."""
        self.bot = TeleBot(BOT_TOKEN)
        self.db = DatabaseManager()
        self.session_manager = SessionManager(self.db)
        self.start_handler = StartHandler(self.bot, self.db, self.session_manager)
        self.question_handler = QuestionHandler(self.bot, self.db, self.session_manager)
        
        # Initialize database
        if not self.db.initialize_database():
            logger.error("Failed to initialize database")
            sys.exit(1)
        
        # Start file system watcher in background thread
        self._start_file_watcher()
        
        # Register handlers
        self._register_handlers()
        
        logger.info("HEXACO Bot initialized successfully")
    
    def _safe_answer_callback_query(self, call_id: str, text: str = "") -> bool:
        """Безопасно отвечает на callback query, обрабатывая ошибки устаревших запросов."""
        try:
            self.bot.answer_callback_query(call_id, text)
            return True
        except Exception as e:
            # Логируем ошибку, но не пытаемся снова отвечать на callback
            logger.warning(f"Failed to answer callback query {call_id}: {e}")
            return False
    
    def _start_file_watcher(self):
        """Start the file system watcher for automatic psychoprofile generation."""
        try:
            # Start watcher in daemon thread so it stops when main program stops
            watcher_thread = threading.Thread(
                target=self._run_file_watcher,
                daemon=True
            )
            watcher_thread.start()
            logger.info("File system watcher started successfully")
        except Exception as e:
            logger.error(f"Failed to start file system watcher: {e}")
    
    def _run_file_watcher(self):
        """Run the file system watcher."""
        try:
            # ВРЕМЕННО ОТКЛЮЧЕНО: Автоматическое создание профилей при появлении новых отчетов
            # Use absolute paths to ensure they work from any working directory
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # Go up to project root
            reports_dir = os.path.join(base_dir, "hexaco_bot", "user_reports")
            profiles_dir = os.path.join(base_dir, "hexaco_bot", "user_profile")
            
            # self.file_observer = start_watching_background(reports_dir, profiles_dir)
            logger.info(f"File watcher is temporarily disabled. Reports dir: {reports_dir}, Profiles dir: {profiles_dir}")
        except Exception as e:
            logger.error(f"Error in file watcher: {e}")
    
    def _register_handlers(self):
        """Register all bot message handlers."""
        
        # Start command handler
        @self.bot.message_handler(commands=['start'])
        def handle_start(message: Message):
            user_id = message.from_user.id
            user_data = self.db.get_user(user_id)
            session = self.session_manager.get_or_create_session(user_id)

            if user_data:
                # Existing user
                if not user_data.get('paei_index'):
                    logger.info(f"User {user_id} exists, starting PAEI input.")
                    self.start_handler.ask_paei_index(message)
                elif not user_data.get('mbti_type'):
                    logger.info(f"User {user_id} has PAEI, starting MBTI input.")
                    self.start_handler.ask_mbti_type(message)
                else:
                    logger.info(f"User {user_id} has PAEI and MBTI, showing test menu.")
                    # Ensure state is appropriate for showing menu, e.g. initial_setup_complete
                    self.session_manager.update_session_state(user_id, STATE_INITIAL_SETUP_COMPLETE)
                    self.question_handler.show_test_menu(message)
            else:
                # New user - registration flow handled by StartHandler
                logger.info(f"New user {user_id}, starting registration flow.")
                self.start_handler.handle_start_command(message)
        
        # Test command handler
        @self.bot.message_handler(commands=['test'])
        def handle_test(message: Message):
            self.question_handler.start_test_for_user(message)
        
        # Results command handler
        @self.bot.message_handler(commands=['results'])
        def handle_results(message: Message):
            user_id = message.from_user.id
            results = self.db.get_user_results(user_id)
            
            if not results:
                self.bot.send_message(
                    message.chat.id,
                    "❌ У вас пока нет результатов тестов. Пройдите тест командой /test"
                )
                return
            
            # Show latest result
            latest_result = results[0]
            from hexaco_bot.src.scoring.hexaco_scorer import HEXACOScorer
            scorer = HEXACOScorer()
            
            scores = {
                'H': latest_result['honesty_humility'],
                'E': latest_result['emotionality'],
                'X': latest_result['extraversion'],
                'A': latest_result['agreeableness'],
                'C': latest_result['conscientiousness'],
                'O': latest_result['openness'],
                'Alt': latest_result['altruism']
            }
            
            user_data = self.db.get_user(user_id)
            user_name = f"{user_data['first_name']} {user_data['last_name']}"
            
            results_message = scorer.format_results_message(scores, user_name)
            results_message += f"\n\n📅 Дата прохождения: {latest_result['created_at']}"
            results_message += f"\n📊 Всего тестов: {len(results)}"
            
            self.bot.send_message(message.chat.id, results_message, parse_mode='Markdown')
        
        # Help command handler
        @self.bot.message_handler(commands=['help'])
        def handle_help(message: Message):
            help_text = """
📖 **Справка по HEXACO Боту**

🤖 **Доступные команды:**
/start - Начать работу (регистрация или главное меню)
/test - Пройти HEXACO тест
/results - Посмотреть последние результаты
/help - Эта справка

🎯 **О тесте HEXACO:**
Научно обоснованная модель личности, измеряющая 6 основных факторов:

🤝 **Честность-Смирение** - честность, искренность, скромность
💭 **Эмоциональность** - тревожность, чувствительность, зависимость
🎉 **Экстраверсия** - общительность, энергичность, позитивность
🤗 **Доброжелательность** - терпение, прощение, мягкость
📋 **Добросовестность** - организованность, дисциплина, осторожность
🎨 **Открытость опыту** - креативность, любознательность, нетрадиционность

➕ **Альтруизм** - готовность помогать другим

📝 **Как проходить:**
• 100 вопросов, ~15-20 минут
• Шкала от 1 до 5 (не согласен → согласен)
• Отвечайте честно и спонтанно
• Прогресс автоматически сохраняется

💡 **Помните:** нет правильных или неправильных ответов!
            """
            
            self.bot.send_message(message.chat.id, help_text, parse_mode='Markdown')
        
        # Default message handler
        @self.bot.message_handler(func=lambda message: True)
        def handle_message(message: Message):
            user_id = message.from_user.id
            session = self.session_manager.get_session(user_id)
            
            if session:
                # Let StartHandler manage its states first (gender, name, paei)
                # MBTI is callback, so not handled by default message handler
                if session.state in [STATE_GENDER_SELECTION, 
                                     STATE_NAME_INPUT, 
                                     STATE_AWAIT_PAEI]:
                    self.start_handler.handle_default_message(message)
                # Check if a test is active (QuestionHandler might set a specific state like 'testing')
                elif self.question_handler.is_test_active(user_id): 
                    # User is in a test, all answers are expected via callbacks.
                    # Remind them to use buttons if they send text.
                    self.bot.send_message(message.chat.id, 
                                          "Пожалуйста, используйте кнопки для ответа на вопросы теста. "
                                          "Если вы хотите прервать тест, это пока не поддерживается напрямую, "
                                          "но вы можете попробовать команду /start, чтобы вернуться в главное меню (текущий прогресс этого теста может быть сброшен).")
                else:
                    # Default response if no specific handler took over
                    self.bot.send_message(
                        message.chat.id,
                        "Я не понимаю это сообщение.\n\n"
                        "Доступные команды:\n"
                        "/start - Главное меню/Начать\n"
                        "/results - Мои результаты\n"
                        "/help - Подробная справка"
                    )
            else:
                # No session, user is likely new or session expired
                self.bot.send_message(message.chat.id, "Пожалуйста, начните с команды /start")
        
        # Callback query handler for MBTI buttons
        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callback_query(call):  # call is telebot.types.CallbackQuery
            user_id = call.from_user.id
            session = self.session_manager.get_session(user_id)
            
            if session and session.state == STATE_AWAIT_MBTI:
                self.start_handler.handle_mbti_callback(call, self.question_handler.show_test_menu)
            else:
                # It's good practice to answer all callbacks, even if not handled
                self._safe_answer_callback_query(call.id)
                logger.debug(f"Unhandled callback query for user {user_id}, state: {session.state if session else 'No session'}")
        
        logger.info("Bot handlers registered")
    
    def run(self):
        """Start bot polling."""
        try:
            logger.info("Starting HEXACO Bot...")
            self.bot.infinity_polling(none_stop=True)
        except Exception as e:
            logger.error(f"Bot polling error: {e}")
            raise

def main():
    """Main entry point."""
    try:
        bot = HEXACOBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 