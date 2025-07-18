"""
Start command and basic message handlers for HEXACO bot.
"""

import logging
from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, CallbackQuery
from hexaco_bot.src.data.database import DatabaseManager
from hexaco_bot.src.session.session_manager import SessionManager
from hexaco_bot.src.scoring.hexaco_scorer import HEXACOScorer

logger = logging.getLogger(__name__)

# States
STATE_GENDER_SELECTION = 'gender_selection'
STATE_NAME_INPUT = 'name_input'
STATE_AWAIT_PAEI = 'awaiting_paei'
STATE_AWAIT_MBTI = 'awaiting_mbti'
STATE_INITIAL_SETUP_COMPLETE = 'initial_setup_complete'


# Генерируем все возможные PAEI коды
def _generate_valid_paei_codes():
    """Генерирует все возможные валидные PAEI коды."""
    valid_codes = []
    # Каждая позиция может быть либо соответствующей буквой (заглавной или строчной), либо дефисом
    for p in ['P', 'p', '-']:
        for a in ['A', 'a', '-']:
            for e in ['E', 'e', '-']:
                for i in ['I', 'i', '-']:
                    valid_codes.append(f"{p}{a}{e}{i}")
    return sorted(valid_codes)

_VALID_PAEI_CODES = _generate_valid_paei_codes()

MBTI_TYPES = [
    "Архитектор — INTJ-A / INTJ-T", "Логик — INTP-A / INTP-T",
    "Командир — ENTJ-A / ENTJ-T", "Полемист — ENTP-A / ENTP-T",
    "Заступник — INFJ-A / INFJ-T", "Посредник — INFP-A / INFP-T",
    "Протагонист — ENFJ-A / ENFJ-T", "Активист — ENFP-A / ENFP-T",
    "Логист — ISTJ-A / ISTJ-T", "Защитник — ISFJ-A / ISFJ-T",
    "Менеджер — ESTJ-A / ESTJ-T", "Консул — ESFJ-A / ESFJ-T",
    "Виртуоз — ISTP-A / ISTP-T", "Авантюрист — ISFP-A / ISFP-T",
    "Предприниматель — ESTP-A / ESTP-T", "Артист — ESFP-A / ESFP-T"
]

class StartHandler:
    """Handles /start command and user registration flow."""
    
    def __init__(self, bot: TeleBot, db: DatabaseManager, session_manager: SessionManager):
        self.bot = bot
        self.db = db
        self.session_manager = session_manager

    def _safe_answer_callback_query(self, call_id: str, text: str) -> bool:
        """Безопасно отвечает на callback query, обрабатывая ошибки устаревших запросов."""
        try:
            self.bot.answer_callback_query(call_id, text)
            return True
        except Exception as e:
            # Логируем ошибку, но не пытаемся снова отвечать на callback
            logger.warning(f"Failed to answer callback query {call_id}: {e}")
            return False
    
    def handle_start_command(self, message: Message):
        """Handle /start command."""
        user_id = message.from_user.id
        username = message.from_user.username
        
        logger.info(f"Start command from user {user_id} (@{username})")
        
        # Check if user already exists
        existing_user = self.db.get_user(user_id)
        if existing_user:
            self._send_welcome_back_message(message, existing_user)
        else:
            self._send_welcome_new_user(message)
    
    def _send_welcome_new_user(self, message: Message):
        """Send welcome message to new user."""
        welcome_text = """
�� Добро пожаловать в программу комплексной оценки личности!

Эта программа поможет вам лучше понять себя через серию тестов.
Для начала нам нужно немного информации о вас.

Выберите ваш пол:
        """
        
        # Create gender selection keyboard
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(KeyboardButton("👨 Мужской"), KeyboardButton("👩 Женский"))
        
        self.bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard)
        
        # Update session state
        self.session_manager.get_or_create_session(message.from_user.id)
        self.session_manager.update_session_state(message.from_user.id, STATE_GENDER_SELECTION)
    
    def _send_welcome_back_message(self, message: Message, user_data: dict):
        """Send welcome back message to existing user."""
        name = f"{user_data['first_name']} {user_data['last_name']}"
        
        # Check if PAEI and MBTI are filled
        if not user_data.get('paei_index'):
            logger.info(f"User {message.from_user.id} exists but PAEI is missing. Requesting PAEI.")
            self.ask_paei_index(message)
            return
        if not user_data.get('mbti_type'):
            logger.info(f"User {message.from_user.id} exists but MBTI is missing. Requesting MBTI.")
            self.ask_mbti_type(message) # Assumes PAEI is present if we reach here
            return
        
        welcome_back_text = f"""
👋 С возвращением, {name}!

Вы уже предоставили всю начальную информацию.
Теперь вы можете приступить к тестам или посмотреть свои результаты.

Выберите действие:
• /start или /test - Пройти тесты (или продолжить)
• /results - Посмотреть предыдущие результаты
• /help - Получить справку
        """
        self.bot.send_message(message.chat.id, welcome_back_text)
        # Ensure session state is cleared or set to a menu state
        session = self.session_manager.get_or_create_session(message.from_user.id)
        self.session_manager.update_session_state(session.user_id, STATE_INITIAL_SETUP_COMPLETE)
    
    def handle_help_command(self, message: Message):
        """Handle /help command."""
        help_text = """
📖 Справка по HEXACO Тесту

🎯 О тесте:
HEXACO - это научно обоснованная модель личности, измеряющая 6 основных факторов.

📝 Как проходить:
1. Ответьте на все 100 вопросов честно
2. Используйте шкалу от 1 до 5:
   1 - Совершенно не согласен
   2 - Немного не согласен  
   3 - Нейтрально, нет мнения
   4 - Немного согласен
   5 - Совершенно согласен

⏱️ Время: 15-20 минут
🔄 Можно прервать и продолжить позже

📊 Результаты:
После завершения вы получите детальный анализ по всем 6 факторам.

Команды:
/start - Начать тест
/help - Эта справка
        """
        
        self.bot.send_message(message.chat.id, help_text)
    
    def handle_default_message(self, message: Message):
        """Handle all other messages based on session state."""
        user_id = message.from_user.id
        session = self.session_manager.get_session(user_id)
        
        if not session:
            # No active session, suggest starting
            # Check if user exists, if so, maybe they just need to start the PAEI/MBTI flow
            user = self.db.get_user(user_id)
            if user and (not user.get('paei_index') or not user.get('mbti_type')):
                 # This case might be rare if /start handles it, but as a fallback:
                self.bot.send_message(message.chat.id, "Кажется, вы не завершили начальную настройку. Пожалуйста, используйте команду /start.")
            else:
                self.bot.send_message(
                message.chat.id,
                "Для начала работы с ботом отправьте команду /start"
            )
            return
        
        # Handle message based on current state
        if session.state == STATE_GENDER_SELECTION:
            self._handle_gender_selection(message, session)
        elif session.state == STATE_NAME_INPUT:
            self._handle_name_input(message, session)
        elif session.state == STATE_AWAIT_PAEI:
            self._handle_paei_input(message, session)
        else:
            # Default response for states not handled here (e.g., awaiting_mbti is handled by callback)
            # or if state is something like initial_setup_complete
            if session.state not in [STATE_AWAIT_MBTI, STATE_INITIAL_SETUP_COMPLETE, None, 'start']: # None and 'start' are possible initial states
                self.bot.send_message(
                message.chat.id,
                    "Я не понимаю это сообщение. Используйте /help для получения справки или /start для возврата в меню."
            )
    
    def _handle_gender_selection(self, message: Message, session):
        """Handle gender selection."""
        text = message.text.lower()
        
        if "мужской" in text or "👨" in text:
            gender = "male"
        elif "женский" in text or "👩" in text:
            gender = "female"
        else:
            self.bot.send_message(
                message.chat.id,
                "Пожалуйста, выберите пол, используя кнопки ниже:",
                reply_markup=self._get_gender_keyboard()
            )
            return
        
        # Save gender to temp data
        self.session_manager.update_session_state(
            session.user_id, 
            STATE_NAME_INPUT, 
            {'gender': gender}
        )
        
        # Ask for name
        self.bot.send_message(
            message.chat.id,
            "Отлично! Теперь введите ваше имя и фамилию через пробел.\n\nНапример: Иван Иванов",
            reply_markup=self._get_remove_keyboard()
        )
    
    def _handle_name_input(self, message: Message, session):
        """Handle name input, then proceed to PAEI."""
        name_parts = message.text.strip().split()
        
        if len(name_parts) < 2:
            self.bot.send_message(
                message.chat.id,
                "Пожалуйста, введите имя и фамилию через пробел.\\n\\nНапример: Иван Иванов"
            )
            return
        
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:])
        
        user_id = session.user_id
        username = message.from_user.username
        gender = session.temp_data.get('gender')
        
        if self.db.create_user(user_id, username, first_name, last_name, gender):
            logger.info(f"User {user_id} created/updated with name and gender.")
            self.bot.send_message(
                message.chat.id,
                f"✅ Регистрация основных данных завершена!\nИмя: {first_name} {last_name}\nПол: {'Мужской' if gender == 'male' else 'Женский'}"
            )
            self.ask_paei_index(message) # Proceed to PAEI
            
        else:
            self.bot.send_message(
                message.chat.id,
                "❌ Произошла ошибка при сохранении ваших данных. Попробуйте еще раз или обратитесь к администратору."
            )

    def ask_paei_index(self, message: Message):
        """Ask the user for their PAEI index."""
        user_id = message.from_user.id
        logger.info(f"Asking PAEI index for user {user_id}")

        paei_prompt = """
Теперь укажите ваш PAEI-индекс.
PAEI-индекс описывает ваш стиль менеджмента по Адизесу (Producer, Administrator, Entrepreneur, Integrator).

Введите ваш индекс в виде текстовой строки. 
Буквы могут быть заглавными или строчными. Отсутствие функции обозначается дефисом (-).

Примеры допустимых форматов:
PAEI, PaEi, PAe-, P-E-, p---, ----

Пройти тест можно по ссылке: https://paei.denero.ru/

Пожалуйста, введите ваш PAEI-индекс:
        """
        self.bot.send_message(message.chat.id, paei_prompt, reply_markup=self._get_remove_keyboard())
        self.session_manager.update_session_state(user_id, STATE_AWAIT_PAEI)

    def _handle_paei_input(self, message: Message, session):
        """Handle PAEI index input from user."""
        user_id = message.from_user.id
        paei_input = message.text.strip()  # Убираем .upper() чтобы сохранить оригинальный регистр

        # Сначала проверяем прямое совпадение
        if paei_input in _VALID_PAEI_CODES:
            if self.db.update_user_paei(user_id, paei_input):
                logger.info(f"PAEI index '{paei_input}' saved for user {user_id}")
                self.bot.send_message(message.chat.id, f"✅ Ваш PAEI-индекс '{paei_input}' сохранен.")
                self.ask_mbti_type(message) # Proceed to MBTI
            else:
                logger.error(f"Failed to save PAEI index for user {user_id}")
                self.bot.send_message(message.chat.id, "❌ Произошла ошибка при сохранении вашего PAEI-индекса. Попробуйте ввести его еще раз.")
                # self.ask_paei_index(message) # Re-ask
            return

        # Попытка автоматической коррекции типичных ошибок
        corrected_input = self._try_autocorrect_paei(paei_input)
        if corrected_input and corrected_input in _VALID_PAEI_CODES:
            logger.info(f"Auto-corrected PAEI '{paei_input}' -> '{corrected_input}' for user {user_id}")
            if self.db.update_user_paei(user_id, corrected_input):
                self.bot.send_message(message.chat.id, 
                    f"✅ Ваш PAEI-индекс автоматически исправлен с '{paei_input}' на '{corrected_input}' и сохранен.")
                self.ask_mbti_type(message) # Proceed to MBTI
            else:
                logger.error(f"Failed to save corrected PAEI index for user {user_id}")
                self.bot.send_message(message.chat.id, "❌ Произошла ошибка при сохранении вашего PAEI-индекса. Попробуйте ввести его еще раз.")
            return

        # Если не удалось исправить, показываем детальную ошибку
        logger.warning(f"Invalid PAEI index '{paei_input}' from user {user_id}")
        error_details = self._analyze_paei_error(paei_input)
        invalid_paei_message = f"""
❌ Неверный формат PAEI-индекса: '{paei_input}'

{error_details}

Индекс должен состоять из 4 символов, где каждый символ - это P, A, E, I или дефис (-).
Регистр букв неважен.

Примеры: PAEI, pAe-, --EI, ----, paeI

⚠️ Внимание: Последняя буква - это I (как "Интегратор"), не L!
Бот может автоматически исправить некоторые типичные ошибки.

Пожалуйста, введите ваш PAEI-индекс еще раз:
        """
        self.bot.send_message(message.chat.id, invalid_paei_message)
        # State remains STATE_AWAIT_PAEI

    def _try_autocorrect_paei(self, paei_input: str) -> str:
        """Попытка автоматической коррекции типичных ошибок в PAEI индексе."""
        # Убираем лишние пробелы и приводим к нужной длине
        cleaned = paei_input.strip()
        
        # Типичные ошибки и их исправления
        corrections = {
            'PAEL': 'PAEI',
            'pael': 'paei',
            'PaEL': 'PaEI',
            'paEL': 'paEI',
            'PAIL': 'PAEI',
            'pail': 'paei',
        }
        
        # Прямая замена
        if cleaned in corrections:
            return corrections[cleaned]
        
        # Если длина правильная (4 символа), попробуем исправить только неверные символы
        if len(cleaned) == 4:
            corrected = []
            valid_chars = [['P', 'p', '-'], ['A', 'a', '-'], ['E', 'e', '-'], ['I', 'i', '-']]
            
            for i, char in enumerate(cleaned):
                if char in valid_chars[i]:
                    corrected.append(char)
                else:
                    # Попытка исправления на основе позиции
                    if i == 0 and char.upper() == 'P':
                        corrected.append('P' if char.isupper() else 'p')
                    elif i == 1 and char.upper() == 'A':
                        corrected.append('A' if char.isupper() else 'a')
                    elif i == 2 and char.upper() == 'E':
                        corrected.append('E' if char.isupper() else 'e')
                    elif i == 3 and char.upper() == 'I':
                        corrected.append('I' if char.isupper() else 'i')
                    elif i == 3 and char.upper() == 'L':  # L -> I (типичная ошибка)
                        corrected.append('I' if char.isupper() else 'i')
                    else:
                        return None  # Не можем исправить
            
            return ''.join(corrected)
        
        return None

    def _analyze_paei_error(self, paei_input: str) -> str:
        """Анализирует ошибку в PAEI индексе и возвращает подсказку."""
        cleaned = paei_input.strip()
        
        if len(cleaned) == 0:
            return "⚠️ Вы не ввели индекс."
        
        if len(cleaned) < 4:
            return f"⚠️ Слишком короткий индекс ({len(cleaned)} символов вместо 4)."
        
        if len(cleaned) > 4:
            return f"⚠️ Слишком длинный индекс ({len(cleaned)} символов вместо 4)."
        
        # Проверяем каждую позицию
        errors = []
        positions = ['первая (P)', 'вторая (A)', 'третья (E)', 'четвертая (I)']
        valid_chars = [['P', 'p', '-'], ['A', 'a', '-'], ['E', 'e', '-'], ['I', 'i', '-']]
        
        for i, char in enumerate(cleaned):
            if char not in valid_chars[i]:
                if i == 3 and char.upper() == 'L':
                    errors.append(f"⚠️ {positions[i]} позиция: '{char}' должно быть 'I' или 'i' (возможно, вы имели в виду 'I'?)")
                else:
                    expected = ', '.join(valid_chars[i])
                    errors.append(f"⚠️ {positions[i]} позиция: '{char}' неверный символ. Ожидается: {expected}")
        
        if errors:
            return '\n'.join(errors)
        
        return "⚠️ Неизвестная ошибка в формате."

    def ask_mbti_type(self, message: Message):
        """Ask the user for their 16Personalities type using inline buttons."""
        user_id = message.from_user.id
        logger.info(f"Asking MBTI type for user {user_id}")

        mbti_prompt = """
Отлично! Теперь укажите ваш тип личности по классификации 16Personalities (основанной на MBTI).
Пройти тест можно по ссылке: https://www.16personalities.com

Выберите ваш тип из списка ниже:
        """
        
        keyboard = InlineKeyboardMarkup(row_width=2) # 2 кнопки в ряд
        buttons = [InlineKeyboardButton(text=mbti_type, callback_data=mbti_type) for mbti_type in MBTI_TYPES]
        keyboard.add(*buttons)
        
        self.bot.send_message(message.chat.id, mbti_prompt, reply_markup=keyboard)
        self.session_manager.update_session_state(user_id, STATE_AWAIT_MBTI)

    def handle_mbti_callback(self, call: CallbackQuery, question_handler_show_test_menu_func): # call is telebot.types.CallbackQuery
        """Handles the MBTI type selection from inline keyboard."""
        user_id = call.from_user.id
        mbti_type = call.data # This is the full string like "Архитектор — INTJ-A / INTJ-T"
        
        logger.info(f"MBTI type selected by user {user_id}: {mbti_type}")

        if self.db.update_user_mbti(user_id, mbti_type):
            self._safe_answer_callback_query(call.id, f"Тип {mbti_type} сохранен.")
            self.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"✅ Ваш тип личности '{mbti_type}' успешно сохранен!\n\nСпасибо за предоставленную информацию!"
            ) # Remove keyboard by not passing reply_markup
            
            self.session_manager.update_session_state(user_id, STATE_INITIAL_SETUP_COMPLETE)
            logger.info(f"Initial setup complete for user {user_id}. Proceeding to test menu.")
            
            # Pass the CallbackQuery object itself to show_test_menu
            question_handler_show_test_menu_func(call) 
            
        else:
            logger.error(f"Failed to save MBTI type for user {user_id}")
            self._safe_answer_callback_query(call.id, "Ошибка сохранения.")
            self.bot.send_message(call.message.chat.id, "❌ Произошла ошибка при сохранении вашего типа личности. Пожалуйста, попробуйте еще раз.")
            # Potentially re-ask or direct to /start
            # self.ask_mbti_type(call.message) # This would re-send the button prompt
    
    def _get_gender_keyboard(self):
        """Get gender selection keyboard."""
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(KeyboardButton("👨 Мужской"), KeyboardButton("👩 Женский"))
        return keyboard
    
    def _get_remove_keyboard(self):
        """Get keyboard removal markup."""
        return ReplyKeyboardRemove() 