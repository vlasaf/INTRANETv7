"""
Question flow handler for HEXACO test.
Manages question presentation, response collection, and progress tracking.
"""

import logging
import json
from telebot import TeleBot
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Chat # Added Chat for dummy message
from typing import Union, Optional # Added Union and Optional
from pathlib import Path

# Используем абсолютные импорты
from hexaco_bot.src.data.database import DatabaseManager
from hexaco_bot.src.session.session_manager import SessionManager
from hexaco_bot.src.data.hexaco_questions import get_question as get_hexaco_question, get_total_questions as get_total_hexaco_questions
from hexaco_bot.src.scoring.hexaco_scorer import HEXACOScorer
# SDS Imports
from hexaco_bot.src.data.sds_questions import get_sds_question, get_total_sds_questions, SDS_ANSWER_OPTIONS
from hexaco_bot.src.scoring.sds_scorer import SDSScorer
# SVS Imports
from hexaco_bot.src.data.svs_questions import get_svs_question, get_total_svs_questions, SVS_ANSWER_OPTIONS, SVS_QUESTIONS
from hexaco_bot.src.scoring.svs_scorer import SVSScorer

# PANAS Imports
from hexaco_bot.src.data.panas_questions import get_panas_question_text, get_total_panas_questions, PANAS_ANSWER_OPTIONS
from hexaco_bot.src.scoring.panas_scorer import PanasScorer
# Self-Efficacy Imports
from hexaco_bot.src.data.self_efficacy_questions import get_self_efficacy_question_text, get_total_self_efficacy_questions, SELF_EFFICACY_ANSWER_OPTIONS
from hexaco_bot.src.scoring.self_efficacy_scorer import SelfEfficacyScorer
# CD-RISC Imports
from hexaco_bot.src.data.cdrisc_questions import get_cdrisc_question_data, get_total_cdrisc_questions, CDRISC_ANSWER_OPTIONS
from hexaco_bot.src.scoring.cdrisc_scorer import CDRISCScorer
# RFQ Imports
from hexaco_bot.src.data.rfq_questions import get_rfq_question_data, get_total_rfq_questions, RFQ_ANSWER_OPTIONS
from hexaco_bot.src.scoring.rfq_scorer import RFQScorer
# PID-5-BF+M Imports
from hexaco_bot.src.data.pid5bfm_questions import get_pid5bfm_question_data, get_total_pid5bfm_questions, PID5BFM_ANSWER_OPTIONS
from hexaco_bot.src.scoring.pid5bfm_scorer import PID5BFMScorer

import os # Added for path operations
from datetime import datetime # Added for timestamp in report filename

logger = logging.getLogger(__name__)

class QuestionHandler:
    """Handles all test question flows and response collection."""
    
    def __init__(self, bot: TeleBot, db: DatabaseManager, session_manager: SessionManager):
        self.bot = bot
        self.db = db
        self.session_manager = session_manager
        self.hexaco_scorer = HEXACOScorer()
        self.sds_scorer = SDSScorer()
        self.svs_scorer = SVSScorer()
        self.panas_scorer = PanasScorer()
        self.self_efficacy_scorer = SelfEfficacyScorer()
        self.cdrisc_scorer = CDRISCScorer()
        self.rfq_scorer = RFQScorer()
        self.pid5bfm_scorer = PID5BFMScorer()
        
        # Register callback handlers
        self._register_callbacks()
    
    def is_test_active(self, user_id: int) -> bool:
        """Check if the user is currently in a test-taking state."""
        session = self.session_manager.get_session(user_id)
        return session is not None and session.state == 'testing'
    
    def _register_callbacks(self):
        """Register callback query handlers."""
        
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('answer_'))
        def handle_answer_callback(call: CallbackQuery):
            self._handle_answer_callback(call)
        
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('nav_'))
        def handle_navigation_callback(call: CallbackQuery):
            self._handle_navigation_callback(call)
        
        @self.bot.callback_query_handler(func=lambda call: call.data == 'start_hexaco_test')
        def handle_start_hexaco_test_callback(call: CallbackQuery):
            self._handle_start_hexaco_test_callback(call)
        
        @self.bot.callback_query_handler(func=lambda call: call.data == 'view_results')
        def handle_view_results_callback(call: CallbackQuery):
            self._handle_view_results_callback(call)
        
        @self.bot.callback_query_handler(func=lambda call: call.data == 'start_sds_test')
        def handle_start_sds_test_callback(call: CallbackQuery):
            self._handle_start_sds_test_callback(call)
        
        @self.bot.callback_query_handler(func=lambda call: call.data == 'start_svs_test')
        def handle_start_svs_test_callback(call: CallbackQuery):
            self._handle_start_svs_test_callback(call)
        
        @self.bot.callback_query_handler(func=lambda call: call.data == 'start_panas_test')
        def handle_start_panas_test_callback(call: CallbackQuery):
            self._handle_start_panas_test_callback(call)
        
        @self.bot.callback_query_handler(func=lambda call: call.data == 'start_self_efficacy_test')
        def handle_start_self_efficacy_test_callback(call: CallbackQuery):
            self._handle_start_self_efficacy_test_callback(call)
        
        @self.bot.callback_query_handler(func=lambda call: call.data == 'start_cdrisc_test')
        def handle_start_cdrisc_test_callback(call: CallbackQuery):
            self._handle_start_cdrisc_test_callback(call)
        
        @self.bot.callback_query_handler(func=lambda call: call.data == 'start_rfq_test')
        def handle_start_rfq_test_callback(call: CallbackQuery):
            self._handle_start_rfq_test_callback(call)

        @self.bot.callback_query_handler(func=lambda call: call.data == 'start_pid5bfm_test')
        def handle_start_pid5bfm_test_callback(call: CallbackQuery):
            self._handle_start_pid5bfm_test_callback(call)
        
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('select_test_'))
        def handle_select_test_callback(call: CallbackQuery):
            self._handle_select_test_callback(call)

        @self.bot.callback_query_handler(func=lambda call: call.data == 'select_initial_test')
        def handle_select_initial_test_callback(call: CallbackQuery):
            self._handle_select_initial_test_callback(call)
    
    def _start_test_flow(self, chat_id: int, user_id: int, user_first_name: str):
        """Core logic to start or select a test for a user."""
        user_data = self.db.get_user(user_id)
        if not user_data:
            self.bot.send_message(chat_id, "❌ Ошибка: пользователь не найден для начала теста. Пожалуйста, зарегистрируйтесь через /start.")
            return

        session = self.session_manager.get_or_create_session(user_id)

        username_for_file = user_data.get('username', f"user_{user_id}")
        safe_username_prefix = "".join(c if c.isalnum() else "_" for c in str(username_for_file))
        report_file_prefix_to_check = f"report_{safe_username_prefix}_"
        
        current_script_path = Path(__file__).resolve()
        hexaco_bot_root = current_script_path.parent.parent.parent 
        user_reports_dir_absolute = hexaco_bot_root / "user_reports"
        user_profile_dir_absolute = hexaco_bot_root / "user_profile" # Определяем директорию для user_profile
        
        logger.info(f"_start_test_flow: Checking for user report files for user {user_id} (username: {username_for_file}) in {user_reports_dir_absolute} with prefix '{report_file_prefix_to_check}'.")
        
        initial_report_exists = False
        latest_report_path_str: Optional[str] = None # Для хранения пути к самому свежему user_report

        if user_reports_dir_absolute.exists() and user_reports_dir_absolute.is_dir():
            found_reports = []
            for f_name in os.listdir(user_reports_dir_absolute):
                if f_name.startswith(report_file_prefix_to_check) and f_name.endswith(".json"):
                    found_reports.append(user_reports_dir_absolute / f_name)
            
            if found_reports:
                initial_report_exists = True
                # Сортируем по времени модификации, чтобы взять самый свежий
                found_reports.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                latest_report_path_str = str(found_reports[0])
                logger.info(f"_start_test_flow: Found matching report file(s). Latest: {latest_report_path_str}")
        else:
            logger.warning(f"_start_test_flow: User reports directory {user_reports_dir_absolute} does not exist or is not a directory.")

        logger.info(f"_start_test_flow: Result of initial_report_exists check: {initial_report_exists}")

        # Получаем точную информацию о пройденных тестах из базы данных
        completed_tests_from_db = self.db.get_completed_tests_for_user(user_id)
        logger.info(f"_start_test_flow: Completed tests from DB for user {user_id}: {completed_tests_from_db}")
        
        # Обновляем сессию на основе реальных данных из БД
        for test_key, is_completed in completed_tests_from_db.items():
            session.test_completed[test_key] = is_completed
        
        logger.info(f"_start_test_flow: User {user_id} session.test_completed AFTER DB check: {session.test_completed}")
        
        available_tests = []
        if not session.test_completed.get('hexaco', False): available_tests.append(("HEXACO Личностный Тест", "hexaco"))
        if not session.test_completed.get('sds', False): available_tests.append(("Тест Самодетерминации (SDS)", "sds"))
        if not session.test_completed.get('svs', False): available_tests.append(("Тест Ценностей Шварца (SVS)", "svs"))
        if not session.test_completed.get('panas', False): available_tests.append(("Шкала Позитивного и Негативного Аффекта (ШПАНА)", "panas"))
        if not session.test_completed.get('self_efficacy', False): available_tests.append(("Тест Самоэффективности (General Self-Efficacy Scale)", "self_efficacy"))
        if not session.test_completed.get('cdrisc', False): available_tests.append(("Тест Устойчивости (CD-RISC)", "cdrisc"))
        if not session.test_completed.get('rfq', False): available_tests.append(("Тест Диагностика фокуса регуляции (RFQ)", "rfq"))
        if not session.test_completed.get('pid5bfm', False): available_tests.append(("Опросник личности PID-5-BF+M", "pid5bfm"))

        logger.info(f"_start_test_flow: User {user_id} available_tests after filtering: {available_tests}")

        if not available_tests: # Все тесты пройдены (или были пройдены)
            self.bot.send_message(chat_id, "🎉 Вы уже прошли все доступные тесты! Скоро здесь появятся новые.")
            
            path_to_user_report_for_processing: Optional[str] = None

            if not initial_report_exists:
                logger.info(f"_start_test_flow: Generating user report for user {user_id} as it did not exist initially.")
                path_to_user_report_for_processing = self._generate_user_report(user_id) # Эта функция теперь возвращает путь
                if path_to_user_report_for_processing:
                    logger.info(f"_start_test_flow: Newly generated user report: {path_to_user_report_for_processing}")
                else:
                    logger.error(f"_start_test_flow: Failed to generate new user report for user {user_id}.")
            else:
                path_to_user_report_for_processing = latest_report_path_str # Используем найденный ранее самый свежий
                logger.info(f"_start_test_flow: Using existing user report: {path_to_user_report_for_processing}")

            # Теперь проверяем user_profile
            user_profile_filename = f"{user_id}_profile.json" # Имя файла user_profile
            user_profile_filepath = user_profile_dir_absolute / user_profile_filename

            logger.info(f"_start_test_flow: Checking for user profile: {user_profile_filepath}")
            if user_profile_filepath.exists():
                logger.info(f"_start_test_flow: User profile for user {user_id} already exists at {user_profile_filepath}.")
            else:
                logger.info(f"_start_test_flow: User profile for user {user_id} does NOT exist. Attempting to generate.")
                if path_to_user_report_for_processing:
                    try:
                        with open(path_to_user_report_for_processing, 'r', encoding='utf-8') as f_report:
                            report_content = json.load(f_report)
                        
                        all_user_tests_data = report_content.get("tests")
                        
                        # ВРЕМЕННО ОТКЛЮЧЕНО: Интерпретация данных пользователя с помощью AI
                        # Важно: user_id для profiler.py должен быть строкой, если имя файла так формируется
                        # В нашем случае generate_and_save_psychoprofile ожидает user_id как он есть (может быть int)
                        # но для имени файла он его приводит к строке. Передадим user_id как есть.
                        # Убедимся, что psychoprofile.profiler импортирован
                        # from hexaco_bot.src.psychoprofile.profiler import generate_and_save_psychoprofile
                        
                        if all_user_tests_data:
                            logger.info(f"_start_test_flow: AI profile generation is temporarily disabled for user {user_id}")
                            # logger.info(f"_start_test_flow: Calling generate_and_save_psychoprofile for user {user_id} using report {path_to_user_report_for_processing}")
                            # saved_profile_path = generate_and_save_psychoprofile(
                            #     user_id=str(user_id), # Функция ожидает str для формирования имени файла
                            #     all_user_tests_data=all_user_tests_data,
                            #     profile_dir=str(user_profile_dir_absolute)
                            # )
                            # if saved_profile_path:
                            #     logger.info(f"_start_test_flow: Psychoprofile successfully generated: {saved_profile_path}")
                            # else:
                            #     logger.error(f"_start_test_flow: Psychoprofile generation failed for user {user_id}.")
                        else:
                            logger.error(f"_start_test_flow: 'tests' key not found or data is invalid in report {path_to_user_report_for_processing}.")
                    except FileNotFoundError:
                        logger.error(f"_start_test_flow: User report file {path_to_user_report_for_processing} not found when trying to generate profile.")
                    except json.JSONDecodeError:
                        logger.error(f"_start_test_flow: Error decoding JSON from user report {path_to_user_report_for_processing}.")
                    except Exception as e:
                        logger.error(f"_start_test_flow: Unexpected error processing report/generating profile for user {user_id}: {e}", exc_info=True)
                else:
                    logger.error(f"_start_test_flow: No user report path available for user {user_id}, cannot generate profile.")
            
            self.show_overall_results_menu(chat_id, user_id)
            return

        if len(available_tests) == 1:
            test_name, test_type = available_tests[0]
            self._initiate_test_flow(chat_id, user_id, user_first_name, test_type)
        else:
            keyboard = InlineKeyboardMarkup()
            for test_name, test_type_code in available_tests:
                keyboard.add(InlineKeyboardButton(f"🚀 Начать: {test_name}", callback_data=f"select_test_{test_type_code}"))
            self.bot.send_message(chat_id, "👇 Выберите тест, который хотите пройти:", reply_markup=keyboard)

    def start_test_for_user(self, message: Message):
        """Handles the /test command by initiating the test flow."""
        user_id = message.from_user.id
        user_data = self.db.get_user(user_id)
        if not user_data:
            self.bot.send_message(message.chat.id, "❌ Сначала нужно зарегистрироваться! Отправьте /start для регистрации.")
            return

        self._start_test_flow(message.chat.id, user_id, user_data['first_name'])

    def _initiate_test_flow(self, chat_id: int, user_id: int, user_first_name: str, test_type: str):
        """Sets up session for the selected test and sends its intro."""
        session = self.session_manager.get_or_create_session(user_id)
        session.current_test_type = test_type
        session.current_question = 1 
        if test_type not in session.responses: 
            session.responses[test_type] = {}
        self.session_manager.update_session_state(user_id, 'testing') # General testing state

        if test_type == 'hexaco':
            self._send_hexaco_intro(chat_id, user_first_name)
        elif test_type == 'sds':
            self._send_sds_intro(chat_id, user_first_name)
        elif test_type == 'svs':
            self._send_svs_intro(chat_id, user_first_name)
        elif test_type == 'panas':
            self._send_panas_intro(chat_id, user_first_name)
        elif test_type == 'self_efficacy':
            self._send_self_efficacy_intro(chat_id, user_first_name)
        elif test_type == 'cdrisc':
            self._send_cdrisc_intro(chat_id, user_first_name)
        elif test_type == 'rfq':
            self._send_rfq_intro(chat_id, user_first_name)
        elif test_type == 'pid5bfm':
            self._send_pid5bfm_intro(chat_id, user_first_name)
        else:
            logger.error(f"Attempted to initiate unknown test type: {test_type} for user {user_id}")
            self.bot.send_message(chat_id, "❌ Ошибка: неизвестный тип теста.")

    def _handle_select_test_callback(self, call: CallbackQuery):
        """Handles the callback when a user selects a specific test to start."""
        user_id = call.from_user.id
        user_data = self.db.get_user(user_id)
        if not user_data:
            self._safe_answer_callback_query(call.id, "❌ Сначала зарегистрируйтесь /start")
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            return
        
        selected_test_type = call.data.replace("select_test_", "")

        # Delete the selection message
        try:
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            logger.warning(f"Could not delete test selection message: {e}")

        self._initiate_test_flow(call.message.chat.id, user_id, user_data['first_name'], selected_test_type)

    def _handle_select_initial_test_callback(self, call: CallbackQuery):
        """Handles the callback from the 'Пройти тест' button in the initial menu."""
        try:
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            logger.warning(f"Could not delete initial test menu message: {e}")
        
        actual_user_id = call.from_user.id
        chat_id = call.message.chat.id

        user_data = self.db.get_user(actual_user_id)
        if not user_data:
            # This case should ideally not happen if show_test_menu did its job
            self.bot.send_message(chat_id, "❌ Ошибка: пользователь не найден. Пожалуйста, попробуйте /start снова.")
            self._safe_answer_callback_query(call.id, "")
            return
        
        self._start_test_flow(chat_id, actual_user_id, user_data['first_name'])
        self._safe_answer_callback_query(call.id, "") # Acknowledge callback

    def _send_hexaco_intro(self, chat_id: int, user_first_name: str):
        intro_text = f"""
🎯 **HEXACO Личностный Тест**

Привет, {user_first_name}! Готовы начать тест HEXACO?

📝 **Инструкция:**
• Тест состоит из {get_total_hexaco_questions()} вопросов
• Отвечайте честно, как вы обычно себя ведете
• Используйте шкалу от 1 до 5:

1️⃣ Совершенно не согласен
2️⃣ Немного не согласен  
3️⃣ Нейтрально, нет мнения
4️⃣ Немного согласен
5️⃣ Совершенно согласен

⏱️ Ориентировочное время: 15-20 минут
💾 Прогресс автоматически сохраняется

Готовы начать?
        """
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🚀 Начать тест HEXACO", callback_data="start_hexaco_test"))
        self.bot.send_message(chat_id, intro_text, reply_markup=keyboard, parse_mode='Markdown')

    def _send_sds_intro(self, chat_id: int, user_first_name: str):
        intro_text = f"""
🌟 **Тест Самодетерминации (SDS)**

Привет, {user_first_name}! Теперь давайте пройдем тест на самодетерминацию.

📝 **Инструкция:**
• Тест состоит из {get_total_sds_questions()} вопросов.
• Каждый вопрос представляет собой два утверждения: А и Б.
• Выберите, какое утверждение для вас более верно, используя шкалу:

1️⃣ Верно только А
2️⃣ Верно скорее А
3️⃣ Оба утверждение отчасти важны
4️⃣ Верно скорее Б
5️⃣ Верно только Б

⏱️ Ориентировочное время: 5-7 минут
💾 Прогресс автоматически сохраняется

Готовы начать?
        """
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🚀 Начать тест SDS", callback_data="start_sds_test"))
        self.bot.send_message(chat_id, intro_text, reply_markup=keyboard, parse_mode='Markdown')

    def _send_svs_intro(self, chat_id: int, user_first_name: str):
        intro_text_main = f"""
🌟 **Тест Ценностей Шварца (SVS)**

Привет, {user_first_name}! Давайте исследуем ваши жизненные ценности.

📝 **Инструкция:**
• Тест состоит из {get_total_svs_questions()} ценностных утверждений.
• Оцените важность каждой ценности как руководящего принципа ВАШЕЙ жизни.
• Используйте шкалу от -1 до 7:

  -1️⃣ Противоположно моим принципам
   0️⃣ Совершенно не важна
   3️⃣ Важна
   6️⃣ Очень важна
   7️⃣ Высшая значимость (таких не более двух)

💡 **Важно:**
Ниже будет представлен полный список ценностей. Перед тем как нажать "Начать тест", пожалуйста, сделайте следующее:
1. Просмотрите весь список.
2. Выберите одну ценность, которая является для вас **самой важной**. Запомните ее – позже вы оцените ее отметкой «7».
3. Выберите одну ценность, которая **наиболее противоречит вашим принципам**. Запомните, что ей должна быть поставлена отметка «−1». Если такой нет, выберите наименее важную для вас и оцените ее «0» или, если она все же имеет минимальную значимость, то «1» (но у нас нет кнопки 1, так что ориентируйтесь на 0).

Это поможет вам точнее откалибровать свои ответы в ходе теста.

⏱️ Ориентировочное время на сам тест: 10-15 минут.
💾 Прогресс автоматически сохраняется.
        """
        self.bot.send_message(chat_id, intro_text_main, parse_mode='Markdown')

        # Send the list of all SVS values
        svs_values_list_message = "**Список ценностей для предварительного ознакомления:**\n\n"
        for i, q_data in enumerate(SVS_QUESTIONS):
            svs_values_list_message += f"{q_data['id']}. {q_data['text']}\n"
            # Split into multiple messages if too long for Telegram
            if (i + 1) % 20 == 0 or (i + 1) == len(SVS_QUESTIONS):
                try:
                    self.bot.send_message(chat_id, svs_values_list_message, parse_mode='Markdown')
                    if (i + 1) != len(SVS_QUESTIONS): # Reset for next chunk unless it's the last one
                         svs_values_list_message = ""
                except Exception as e:
                    logger.error(f"Error sending SVS values chunk: {e}")
                    self.bot.send_message(chat_id, "Ошибка при отображении списка ценностей.")
                    return # Stop if we can't send the list
        
        # Send the start button after the list
        start_keyboard = InlineKeyboardMarkup()
        start_keyboard.add(InlineKeyboardButton("🚀 Начать тест SVS", callback_data="start_svs_test"))
        self.bot.send_message(chat_id, "Когда будете готовы, нажмите кнопку ниже, чтобы начать сам тест.", reply_markup=start_keyboard)



    def _send_panas_intro(self, chat_id: int, user_first_name: str):
        intro_text = f"""
🎭 **Шкала позитивного и негативного аффекта (ШПАНА)**

Привет, {user_first_name}! Этот тест поможет вам понять, как вы чувствуете себя в течение прошедших нескольких недель.

📝 **Инструкция:**
• Тест состоит из {get_total_panas_questions()} утверждений.
• Оцените, насколько сильно вы чувствовали себя так в течение прошедших нескольких недель, используя шкалой от 1 до 5:

1️⃣ Почти или совсем нет
2️⃣ Немного
3️⃣ Умеренно
4️⃣ Значительно
5️⃣ Очень сильно

⏱️ Ориентировочное время: 3-5 минут.
💾 Прогресс автоматически сохраняется.

Готовы начать?
        """
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🚀 Начать тест ШПАНА", callback_data="start_panas_test"))
        self.bot.send_message(chat_id, intro_text, reply_markup=keyboard, parse_mode='Markdown')

    def _send_self_efficacy_intro(self, chat_id: int, user_first_name: str):
        intro_text = f"""
🎯 **Тест самоэффективности (Дж. Маддукс, М. Шеер)**

Привет, {user_first_name}!

Этот опросник состоит из ряда утверждений, касающихся Вашего поведения в различных жизненных ситуациях.

📝 **Инструкция:**
Оцените, насколько каждое утверждение описывает вас в обычной жизни, по шкале от –5 (совсем не про меня) до +5 (полностью про меня). Отвечайте быстро, полагаясь на первое впечатление.

• Тест состоит из {get_total_self_efficacy_questions()} утверждений.
• Если абсолютно согласны, отметьте значение «+5», если абсолютно не согласны – значение «–5».
• В зависимости от степени своего согласия или несогласия с утверждениями используйте для ответа промежуточные оценки шкалы.

Шкала ответов:
-5️⃣ Совсем не про меня
-4️⃣ ...
-3️⃣ ...
-2️⃣ ...
-1️⃣ ...
+1️⃣ ...
+2️⃣ ...
+3️⃣ ...
+4️⃣ ...
+5️⃣ Полностью про меня

⏱️ Ориентировочное время: 5-7 минут.
💾 Прогресс автоматически сохраняется.

Готовы начать?
        """
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🚀 Начать Тест самоэффективности", callback_data="start_self_efficacy_test"))
        self.bot.send_message(chat_id, intro_text, reply_markup=keyboard, parse_mode='Markdown')

    def _send_cdrisc_intro(self, chat_id: int, user_first_name: str):
        intro_text = f"""
 Resilience Test (CD-RISC)

Привет, {user_first_name}! Этот тест поможет оценить вашу жизнестойкость.

📝 **Инструкция:**
• Тест состоит из {get_total_cdrisc_questions()} утверждений.
• Оценивайте каждое утверждение, основываясь на том, как вы себя чувствовали и вели в **течение последних 2 недель**.
• Используйте шкалу от 1 до 5:

  1️⃣ Никогда
  2️⃣ Изредка
  3️⃣ Иногда
  4️⃣ Часто
  5️⃣ Почти всегда

⏱️ Ориентировочное время: 5-7 минут.
💾 Прогресс автоматически сохраняется.

Готовы начать?
        """
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🚀 Начать Тест Устойчивости (CD-RISC)", callback_data="start_cdrisc_test"))
        self.bot.send_message(chat_id, intro_text, reply_markup=keyboard, parse_mode='Markdown')

    def _send_rfq_intro(self, chat_id: int, user_first_name: str):
        intro_text = f"""
🎯 **Тест Диагностика фокуса регуляции (RFQ)**

Привет, {user_first_name}! Этот тест поможет определить ваш преобладающий мотивационный фокус.

📝 **Инструкция:**
• Тест состоит из {get_total_rfq_questions()} утверждений.
• Пожалуйста, оцените, насколько каждое утверждение соответствует вам.
• Используйте шкалу от 1 до 5:

  1️⃣ Совершенно не согласен
  2️⃣ Не согласен
  3️⃣ Нечто среднее
  4️⃣ Согласен
  5️⃣ Совершенно согласен

⏱️ Ориентировочное время: 3-5 минут.
💾 Прогресс автоматически сохраняется.

Готовы начать?
        """
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🚀 Начать тест RFQ", callback_data="start_rfq_test"))
        self.bot.send_message(chat_id, intro_text, reply_markup=keyboard, parse_mode='Markdown')

    def _send_pid5bfm_intro(self, chat_id: int, user_first_name: str):
        intro_text = f"""
📝 **Опросник личности PID-5-BF+M**

Привет, {user_first_name}! Этот тест предназначен для оценки черт личности.

**Инструкция:**
• Тест состоит из {get_total_pid5bfm_questions()} утверждений.
• Пожалуйста, оцените, насколько каждое утверждение верно для вас.
• Используйте шкалу от 1 до 4:

  1️⃣ Совершенно неверно или часто неверно
  2️⃣ Иногда или в некоторой степени неверно
  3️⃣ Иногда или в некоторой степени верно
  4️⃣ Совершенно верно или часто верно

⏱️ Ориентировочное время: 7-10 минут.
💾 Прогресс автоматически сохраняется.
        """
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🚀 Начать тест PID-5-BF+M", callback_data="start_pid5bfm_test"))
        self.bot.send_message(chat_id, intro_text, reply_markup=keyboard, parse_mode='Markdown')

    def _handle_start_hexaco_test_callback(self, call: CallbackQuery):
        """Handle start HEXACO test button callback."""
        user_id = call.from_user.id
        user_data = self.db.get_user(user_id)
        if not user_data:
            self._safe_answer_callback_query(call.id, "❌ Сначала зарегистрируйтесь /start")
            return
        
        session = self.session_manager.get_or_create_session(user_id)
        if not session:
            self._safe_answer_callback_query(call.id, "❌ Ошибка создания сессии")
            return
        
        session.current_test_type = 'hexaco'
        session.current_question = 1
        session.responses['hexaco'] = {}
        self.session_manager.update_session_state(user_id, 'testing')
        
        self._safe_answer_callback_query(call.id, "🚀 Тест HEXACO начинается!")
        # Delete the intro message
        if call.message:
            try:
                self.bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception as e:
                logger.warning(f"Could not delete intro message {call.message.message_id} for HEXACO: {e}")
        self._show_question(call.message.chat.id, user_id, 1, 'hexaco')

    def _handle_start_sds_test_callback(self, call: CallbackQuery):
        """Handle start SDS test button callback."""
        user_id = call.from_user.id
        user_data = self.db.get_user(user_id)
        if not user_data:
            self._safe_answer_callback_query(call.id, "❌ Сначала зарегистрируйтесь /start")
            return

        session = self.session_manager.get_or_create_session(user_id)
        if not session:
            self._safe_answer_callback_query(call.id, "❌ Ошибка создания сессии")
            return

        session.current_test_type = 'sds'
        session.current_question = 1
        session.responses['sds'] = {}
        self.session_manager.update_session_state(user_id, 'testing')

        self._safe_answer_callback_query(call.id, "🚀 Тест SDS начинается!")
        # Delete the intro message
        if call.message:
            try:
                self.bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception as e:
                logger.warning(f"Could not delete intro message {call.message.message_id} for SDS: {e}")
        self._show_question(call.message.chat.id, user_id, 1, 'sds')
    
    def _handle_start_svs_test_callback(self, call: CallbackQuery):
        """Handle start SVS test button callback."""
        user_id = call.from_user.id
        user_data = self.db.get_user(user_id)
        if not user_data:
            self._safe_answer_callback_query(call.id, "❌ Сначала зарегистрируйтесь /start")
            return

        session = self.session_manager.get_or_create_session(user_id)
        if not session:
            self._safe_answer_callback_query(call.id, "❌ Ошибка создания сессии")
            return

        session.current_test_type = 'svs'
        session.current_question = 1
        session.responses['svs'] = {}
        self.session_manager.update_session_state(user_id, 'testing')

        self._safe_answer_callback_query(call.id, "🚀 Тест SVS начинается!")
        # Delete the intro message
        if call.message:
            try:
                self.bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception as e:
                logger.warning(f"Could not delete intro message {call.message.message_id} for SVS: {e}")
        self._show_question(call.message.chat.id, user_id, 1, 'svs')
    


    def _handle_start_panas_test_callback(self, call: CallbackQuery):
        """Handle start PANAS test button callback."""
        user_id = call.from_user.id
        user_data = self.db.get_user(user_id)
        if not user_data:
            self._safe_answer_callback_query(call.id, "❌ Сначала зарегистрируйтесь /start")
            return
        session = self.session_manager.get_or_create_session(user_id)
        if not session:
            self._safe_answer_callback_query(call.id, "❌ Ошибка создания сессии")
            return
        session.current_test_type = 'panas'
        session.current_question = 1
        session.responses['panas'] = {}
        self.session_manager.update_session_state(user_id, 'testing')
        self._safe_answer_callback_query(call.id, "🚀 Тест ШПАНА начинается!")
        if call.message:
            try:
                self.bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception as e:
                logger.warning(f"Could not delete intro message {call.message.message_id} for PANAS: {e}")
        self._show_question(call.message.chat.id, user_id, 1, 'panas')

    def _handle_start_self_efficacy_test_callback(self, call: CallbackQuery):
        """Handle start Self-Efficacy test button callback."""
        user_id = call.from_user.id
        user_data = self.db.get_user(user_id)
        if not user_data:
            self._safe_answer_callback_query(call.id, "❌ Сначала зарегистрируйтесь /start")
            return
        session = self.session_manager.get_or_create_session(user_id)
        if not session:
            self._safe_answer_callback_query(call.id, "❌ Ошибка создания сессии")
            return
        session.current_test_type = 'self_efficacy'
        session.current_question = 1
        session.responses['self_efficacy'] = {}
        self.session_manager.update_session_state(user_id, 'testing')
        self._safe_answer_callback_query(call.id, "🚀 Тест самоэффективности начинается!")
        if call.message:
            try:
                self.bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception as e:
                logger.warning(f"Could not delete intro message {call.message.message_id} for Self-Efficacy: {e}")
        self._show_question(call.message.chat.id, user_id, 1, 'self_efficacy')

    def _handle_start_cdrisc_test_callback(self, call: CallbackQuery):
        """Handle start CD-RISC test button callback."""
        user_id = call.from_user.id
        user_data = self.db.get_user(user_id)
        if not user_data:
            self._safe_answer_callback_query(call.id, "❌ Сначала зарегистрируйтесь /start")
            return
        session = self.session_manager.get_or_create_session(user_id)
        if not session:
            self._safe_answer_callback_query(call.id, "❌ Ошибка создания сессии")
            return
        session.current_test_type = 'cdrisc'
        session.current_question = 1
        session.responses['cdrisc'] = {}
        self.session_manager.update_session_state(user_id, 'testing')
        self._safe_answer_callback_query(call.id, "🚀 Тест Устойчивости (CD-RISC) начинается!")
        if call.message:
            try:
                self.bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception as e:
                logger.warning(f"Could not delete intro message {call.message.message_id} for CD-RISC: {e}")
        self._show_question(call.message.chat.id, user_id, 1, 'cdrisc')

    def _handle_start_rfq_test_callback(self, call: CallbackQuery):
        """Handle start RFQ test button callback."""
        user_id = call.from_user.id
        user_data = self.db.get_user(user_id)
        if not user_data:
            self._safe_answer_callback_query(call.id, "❌ Сначала зарегистрируйтесь /start")
            return
        session = self.session_manager.get_or_create_session(user_id)
        if not session:
            self._safe_answer_callback_query(call.id, "❌ Ошибка создания сессии")
            return
        session.current_test_type = 'rfq'
        session.current_question = 1
        session.responses['rfq'] = {}
        self.session_manager.update_session_state(user_id, 'testing')
        self._safe_answer_callback_query(call.id, "🚀 Тест RFQ начинается!")
        if call.message:
            try:
                self.bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception as e:
                logger.warning(f"Could not delete intro message {call.message.message_id} for RFQ: {e}")
        self._show_question(call.message.chat.id, user_id, 1, 'rfq')

    def _handle_start_pid5bfm_test_callback(self, call: CallbackQuery):
        """Handle start PID-5-BF+M test button callback."""
        user_id = call.from_user.id
        user_data = self.db.get_user(user_id)
        if not user_data:
            self._safe_answer_callback_query(call.id, "❌ Сначала зарегистрируйтесь /start")
            return
        session = self.session_manager.get_or_create_session(user_id)
        if not session:
            self._safe_answer_callback_query(call.id, "❌ Ошибка создания сессии")
            return
        session.current_test_type = 'pid5bfm'
        session.current_question = 1
        session.responses['pid5bfm'] = {}
        self.session_manager.update_session_state(user_id, 'testing')
        self._safe_answer_callback_query(call.id, "🚀 Тест PID-5-BF+M начинается!")
        if call.message:
            try:
                self.bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception as e:
                logger.warning(f"Could not delete intro message {call.message.message_id} for PID-5-BF+M: {e}")
        self._show_question(call.message.chat.id, user_id, 1, 'pid5bfm')

    def _show_question(self, chat_id: int, user_id: int, question_num: int, test_type: str):
        """Display a question for the specified test type."""
        session = self.session_manager.get_session(user_id)
        if not session or session.current_test_type != test_type:
            logger.warning(f"Session issue or test type mismatch for user {user_id}. Expected {test_type}, got {session.current_test_type if session else 'None'}.") 
            # Attempt to restart the flow by redirecting to the main menu for the user
            # This requires a Message object. We can create a dummy one if we don't have a direct context.
            # However, a better approach might be to guide the user to use /start or /test.
            self.bot.send_message(chat_id, "Возникла ошибка с вашей сессией. Пожалуйста, попробуйте /start, чтобы вернуться в меню.")
            # dummy_message = Message(message_id=0, from_user=None, date=0, chat=Chat(id=chat_id, type='private'), content_type='text', options={}, json_string="") # from_user should be the actual user if possible
            # self.show_test_menu(dummy_message) # This call might be problematic without proper user context
            return

        try:
            message_text = ""
            keyboard = InlineKeyboardMarkup(row_width=1)
            total_questions_for_test = 0

            if test_type == 'hexaco':
                question_data, factor, is_reverse = get_hexaco_question(question_num)
                total_questions_for_test = get_total_hexaco_questions()
                progress_percent = ((question_num - 1) / total_questions_for_test) * 100
                progress_bar = self._create_progress_bar(progress_percent)
                message_text = f"📊 **HEXACO: Вопрос {question_num} из {total_questions_for_test}**\n{progress_bar} {progress_percent:.0f}%\n\n❓ **{question_data}**\n\nВыберите наиболее подходящий ответ:"
                response_options = [
                    ("1️⃣ Совершенно не согласен", 1),
                    ("2️⃣ Немного не согласен", 2),
                    ("3️⃣ Нейтрально, нет мнения", 3),
                    ("4️⃣ Немного согласен", 4),
                    ("5️⃣ Совершенно согласен", 5)
                ]
                for text, value in response_options:
                    keyboard.add(InlineKeyboardButton(text, callback_data=f"answer_{test_type}_{question_num}_{value}"))
            
            elif test_type == 'sds':
                question_data = get_sds_question(question_num)
                total_questions_for_test = get_total_sds_questions()
                progress_percent = ((question_num - 1) / total_questions_for_test) * 100
                progress_bar = self._create_progress_bar(progress_percent)
                message_text = f"⚖️ **SDS: Вопрос {question_num} из {total_questions_for_test}**\n{progress_bar} {progress_percent:.0f}%\n\n**А.** {question_data['A']}\n**Б.** {question_data['B']}\n\nВыберите, какое утверждение для вас более верно:"
                for value, text in SDS_ANSWER_OPTIONS.items():
                    keyboard.add(InlineKeyboardButton(text, callback_data=f"answer_{test_type}_{question_num}_{value}"))

            elif test_type == 'svs':
                total_questions = get_total_svs_questions()
                question_data = get_svs_question(question_num)
                question_text = question_data['text']
                answer_options = SVS_ANSWER_OPTIONS
                title = f"💎 SVS: Ценность {question_num} из {total_questions}"
                progress_percent = ((question_num -1) / total_questions) * 100
                progress_bar = self._create_progress_bar(progress_percent)
                message_text = f"{title}\n{progress_bar} {progress_percent:.0f}%\n\n❓ **{question_text}**\n\nОцените важность этой ценности для вас:"
                keyboard = InlineKeyboardMarkup(row_width=1)
                for value, text in answer_options.items():
                    keyboard.add(InlineKeyboardButton(text, callback_data=f"answer_{test_type}_{question_num}_{value}"))



            elif test_type == 'panas':
                question_text = get_panas_question_text(question_num)
                total_questions_for_test = get_total_panas_questions()
                progress_percent = ((question_num -1) / total_questions_for_test) * 100
                progress_bar = self._create_progress_bar(progress_percent)
                message_text = f"🎭 **ШПАНА: Утверждение {question_num} из {total_questions_for_test}**\n{progress_bar} {progress_percent:.0f}%\n\n❓ **{question_text}**\n\nВ какой мере вы чувствовали себя так в течение прошедших нескольких недель:"
                keyboard = InlineKeyboardMarkup(row_width=1)
                for value, text in PANAS_ANSWER_OPTIONS.items():
                    keyboard.add(InlineKeyboardButton(text, callback_data=f"answer_{test_type}_{question_num}_{value}"))

            elif test_type == 'self_efficacy':
                question_text = get_self_efficacy_question_text(question_num)
                total_questions_for_test = get_total_self_efficacy_questions()
                progress_percent = ((question_num -1) / total_questions_for_test) * 100
                progress_bar = self._create_progress_bar(progress_percent)
                message_text = f"🎯 **Тест самоэффективности: Вопрос {question_num} из {total_questions_for_test}**\n{progress_bar} {progress_percent:.0f}%\n\n❓ **{question_text}**\n\nОцените, насколько это утверждение описывает вас:"
                keyboard = InlineKeyboardMarkup(row_width=5)
                buttons_row1 = []
                buttons_row2 = []
                sorted_options = sorted(SELF_EFFICACY_ANSWER_OPTIONS.items())
                for i, (value, text) in enumerate(sorted_options):
                    button = InlineKeyboardButton(text, callback_data=f"answer_{test_type}_{question_num}_{value}")
                    if i < 5:
                        buttons_row1.append(button)
                    else:
                        buttons_row2.append(button)
                keyboard.row(*buttons_row1)
                keyboard.row(*buttons_row2)
            
            elif test_type == 'cdrisc':
                question_data = get_cdrisc_question_data(question_num)
                question_text = question_data['text']
                total_questions_for_test = get_total_cdrisc_questions()
                progress_percent = ((question_num -1) / total_questions_for_test) * 100
                progress_bar = self._create_progress_bar(progress_percent)
                message_text = f"🛡️ **CD-RISC: Утверждение {question_num} из {total_questions_for_test}**\n{progress_bar} {progress_percent:.0f}%\n\n❓ **{question_text}**\n\nКак часто это было верно для вас за последние 2 недели?"
                keyboard = InlineKeyboardMarkup(row_width=1) # Or 3 for a more compact layout if preferred
                
                # Sort options by key to ensure order if not already guaranteed
                # buttons_row = []
                for value, text in sorted(CDRISC_ANSWER_OPTIONS.items()):
                    keyboard.add(InlineKeyboardButton(text, callback_data=f"answer_{test_type}_{question_num}_{value}"))
                    # Example for 3 buttons per row:
                    # buttons_row.append(InlineKeyboardButton(text, callback_data=f"answer_{test_type}_{question_num}_{value}"))
                    # if len(buttons_row) == 3:
                    #    keyboard.row(*buttons_row)
                    #    buttons_row = []
                # if buttons_row: # Add any remaining buttons
                #    keyboard.row(*buttons_row)
            
            elif test_type == 'rfq':
                question_data = get_rfq_question_data(question_num)
                question_text = question_data['text']
                total_questions_for_test = get_total_rfq_questions()
                progress_percent = ((question_num -1) / total_questions_for_test) * 100
                progress_bar = self._create_progress_bar(progress_percent)
                message_text = f"🎯 **RFQ: Утверждение {question_num} из {total_questions_for_test}**\n{progress_bar} {progress_percent:.0f}%\n\n❓ **{question_text}**\n\nВыберите ваш ответ:"
                keyboard = InlineKeyboardMarkup(row_width=1)
                for value, text in sorted(RFQ_ANSWER_OPTIONS.items()):
                    keyboard.add(InlineKeyboardButton(text, callback_data=f"answer_{test_type}_{question_num}_{value}"))

            elif test_type == 'pid5bfm':
                question_data = get_pid5bfm_question_data(question_num)
                question_text = question_data['text']
                total_questions_for_test = get_total_pid5bfm_questions()
                progress_percent = ((question_num - 1) / total_questions_for_test) * 100
                progress_bar = self._create_progress_bar(progress_percent)
                message_text = f"📝 **PID-5-BF+M: Вопрос {question_num} из {total_questions_for_test}**\n{progress_bar} {progress_percent:.0f}%\n\n❓ **{question_text}**\n\nВыберите наиболее подходящий ответ:"
                keyboard = InlineKeyboardMarkup(row_width=1)
                for value, text in PID5BFM_ANSWER_OPTIONS.items():
                    keyboard.add(InlineKeyboardButton(text, callback_data=f"answer_{test_type}_{question_num}_{value}"))
            
            self.bot.send_message(chat_id, message_text, reply_markup=keyboard, parse_mode='Markdown')
            
        except ValueError as e:
            logger.error(f"Error showing question {question_num} for test {test_type}: {e}")
            self.bot.send_message(chat_id, "❌ Ошибка при загрузке вопроса. Попробуйте еще раз.")
    
    def _safe_answer_callback_query(self, call_id: str, text: str) -> bool:
        """Безопасно отвечает на callback query, обрабатывая ошибки устаревших запросов."""
        try:
            self.bot.answer_callback_query(call_id, text)
            return True
        except Exception as e:
            # Логируем ошибку, но не пытаемся снова отвечать на callback
            logger.warning(f"Failed to answer callback query {call_id}: {e}")
            return False

    def _handle_answer_callback(self, call: CallbackQuery):
        """Handle answer selection callback for any test."""
        try:
            parts = call.data.split('_')
            if len(parts) < 4: # Ожидаем минимум answer_test_q_value
                logger.error(f"Invalid callback data format: {call.data}")
                self._safe_answer_callback_query(call.id, "❌ Ошибка формата данных ответа.")
                return

            response_value_str = parts[-1]
            question_num_str = parts[-2]
            # Первый элемент 'answer', последний 'value', предпоследний 'question_num'
            # Все, что между 'answer' и 'question_num' - это test_type
            test_type = '_'.join(parts[1:-2]) 

            question_num = int(question_num_str)
            response_value = int(response_value_str)
            
            user_id = call.from_user.id
            session = self.session_manager.get_session(user_id)
            
            if not session or session.current_test_type != test_type:
                self._safe_answer_callback_query(call.id, "⚠️ Ошибка сессии или типа теста. Попробуйте /test.")
                logger.warning(f"Session/test type mismatch in answer CB. User: {user_id}, Expected: {test_type}, Got: {session.current_test_type if session else 'None'}")
                return

            if call.message:
                 try:
                    self.bot.delete_message(call.message.chat.id, call.message.message_id)
                 except Exception as e:
                    logger.warning(f"Could not delete message {call.message.message_id} for user {user_id}: {e}")

            response_saved = self.session_manager.save_response(user_id, test_type, question_num, response_value)

            if not response_saved:
                logger.error(f"Failed to save response for user {user_id}, test {test_type}, Q {question_num}")
                self._safe_answer_callback_query(call.id, "❌ Ошибка сохранения ответа.")
                self._show_question(call.message.chat.id, user_id, question_num, test_type)
                return
            
            self._safe_answer_callback_query(call.id, f"Ответ на вопрос {question_num} ({test_type.upper()}) принят!")
            
            current_total_questions = 0
            if test_type == 'hexaco': current_total_questions = get_total_hexaco_questions()
            elif test_type == 'sds': current_total_questions = get_total_sds_questions()
            elif test_type == 'svs': current_total_questions = get_total_svs_questions()
            elif test_type == 'panas': current_total_questions = get_total_panas_questions()
            elif test_type == 'self_efficacy': current_total_questions = get_total_self_efficacy_questions()
            elif test_type == 'cdrisc': current_total_questions = get_total_cdrisc_questions()
            elif test_type == 'rfq': current_total_questions = get_total_rfq_questions()
            elif test_type == 'pid5bfm': current_total_questions = get_total_pid5bfm_questions()

            if session.current_question <= current_total_questions:
                self._show_question(call.message.chat.id, user_id, session.current_question, test_type)
            else:
                self._complete_test_part(call.message.chat.id, user_id, test_type)
                
        except (IndexError, ValueError) as e:
            logger.error(f"Error handling answer callback: {e}. Data: {call.data}")
            self._safe_answer_callback_query(call.id, "❌ Ошибка обработки ответа.")
        except Exception as e: # Generic exception handler
            logger.error(f"Unexpected error in _handle_answer_callback: {e}")
            self._safe_answer_callback_query(call.id, "❌ Произошла непредвиденная ошибка.")
    
    def _handle_navigation_callback(self, call: CallbackQuery):
        """Handle navigation button (prev/next/skip) callbacks."""
        # This function is now largely redundant as navigation buttons are removed.
        # We can keep it minimal or remove it if no other navigation is planned.
        try:
            parts = call.data.split('_')
            action = parts[1]
            current_question_num = int(parts[2])
            user_id = call.from_user.id

            self._safe_answer_callback_query(call.id, "Навигационные кнопки были удалены.")
            logger.info(f"Navigation callback {call.data} received but buttons are disabled.")

        except (IndexError, ValueError) as e:
            logger.error(f"Error handling navigation callback: {e}. Data: {call.data}")
            self._safe_answer_callback_query(call.id, "❌ Ошибка навигации.")
        except Exception as e:
            logger.error(f"Unexpected error in _handle_navigation_callback: {e}")
            self._safe_answer_callback_query(call.id, "❌ Произошла непредвиденная ошибка.")
    
    def _complete_test_part(self, chat_id: int, user_id: int, test_type: str):
        """Finalize a specific test part, calculate scores, and decide next step."""
        session = self.session_manager.get_session(user_id)
        if not session or session.current_test_type != test_type:
            logger.error(f"Session error or test type mismatch during _complete_test_part for user {user_id}. Expected {test_type}, session has {session.current_test_type if session else 'None'}.")
            self.bot.send_message(chat_id, "❌ Ошибка сессии при завершении теста. Пожалуйста, попробуйте команду /test снова.")
            return
        
        responses_for_test = session.responses.get(test_type, {})
        user_data = self.db.get_user(user_id)
        user_name = f"{user_data['first_name']} {user_data['last_name']}"
        results_message_text = ""
        scores_for_db = {}
        
        try:
            if test_type == 'hexaco':
                if len(responses_for_test) < get_total_hexaco_questions():
                    # Handle incomplete test - this logic might need refinement for multi-test flow
                    self.bot.send_message(chat_id, f"❌ Тест HEXACO не завершен. Пожалуйста, ответьте на все вопросы.")
                    # self._show_question(chat_id, user_id, session.current_question, 'hexaco') # Or find first unanswered
                    return
                scores = self.hexaco_scorer.calculate_scores(responses_for_test)
                results_message_text = self.hexaco_scorer.format_results_message(scores, user_name)
                db_scores = { # Ad-hoc conversion for HEXACO
                    'honesty_humility': scores.get('H', 0.0), 'emotionality': scores.get('E', 0.0),
                    'extraversion': scores.get('X', 0.0), 'agreeableness': scores.get('A', 0.0),
                    'conscientiousness': scores.get('C', 0.0), 'openness': scores.get('O', 0.0),
                    'altruism': scores.get('Alt', 0.0)
                }
                responses_json = self.hexaco_scorer.responses_to_json(responses_for_test)
                self.db.save_test_result(session.session_id, user_id, 'hexaco', db_scores, responses_json)

            elif test_type == 'sds':
                if len(responses_for_test) < get_total_sds_questions():
                    self.bot.send_message(chat_id, f"❌ Тест SDS не завершен. Пожалуйста, ответьте на все вопросы.")
                    return
                scores = self.sds_scorer.calculate_scores(responses_for_test)
                results_message_text = self.sds_scorer.format_sds_results_message(scores, user_name)
                # For SDS, scores dict from scorer is already good for DB (self_contact, choiceful_action, sds_index)
                db_scores = scores 
                responses_json = self.sds_scorer.responses_to_json(responses_for_test)
                self.db.save_test_result(session.session_id, user_id, 'sds', db_scores, responses_json)

            elif test_type == 'svs':
                if len(responses_for_test) < get_total_svs_questions():
                    self.bot.send_message(chat_id, f"❌ Тест SVS не завершен. Пожалуйста, ответьте на все вопросы.")
                    return
                try:
                    scores = self.svs_scorer.calculate_scores(responses_for_test)
                    if scores:
                        # Добавляем user_name в заголовок
                        formatted_lines = [f"📊 **Результаты Теста Ценностей Шварца (SVS) для {user_name}** 📊"]
                        
                        formatted_lines.append(f"\nСредний сырой балл: {scores['mean_raw_score']:.2f}")
                        
                        formatted_lines.append("\n**Основные ценности (ипсатированные средние баллы):**")
                        if 'sorted_value_types' in scores:
                            for value_type, score_val in scores['sorted_value_types']: # Используем score_val во избежание конфликта
                                formatted_lines.append(f"  • {value_type}: {score_val:.2f}")
                        else:
                            for value_type, score_val in scores.get('value_type_scores', {}).items():
                                formatted_lines.append(f"  • {value_type}: {score_val:.2f}")

                        formatted_lines.append("\n**Кластеры ценностей:**")
                        for cluster_name, cluster_score_val in scores.get('cluster_scores', {}).items(): # Используем cluster_score_val
                            clean_cluster_name = cluster_name.replace('-', ' ')
                            formatted_lines.append(f"  • {clean_cluster_name}: {cluster_score_val:.2f}")

                        formatted_lines.append("\n**Интерпретация:**")
                        if scores.get('sorted_value_types'):
                            top_values = [item[0] for item in scores['sorted_value_types'][:3]]
                            bottom_values = [item[0] for item in scores['sorted_value_types'][-3:]]
                            formatted_lines.append(f"  💡 *Вы особенно цените:* {', '.join(top_values)}.")
                            formatted_lines.append(f"  ⚖️ *Менее значимы для вас или вы готовы ими поступиться:* {', '.join(bottom_values)}.")
                        
                        results_message_text = "\n".join(formatted_lines)

                        # Добавлено сохранение результатов SVS в базу данных
                        db_scores_svs = scores # Сохраняем весь словарь результатов от скорера
                        responses_json_svs = json.dumps(responses_for_test) # Сериализуем ответы в JSON
                        self.db.save_test_result(session.session_id, user_id, 'svs', db_scores_svs, responses_json_svs)

                    else:
                        results_message_text = "Не удалось рассчитать SVS результаты (scores object is None)."
                except Exception as e:
                    logger.error(f"Error calculating or formatting SVS scores for user {user_id}: {e}", exc_info=True)
                    results_message_text = f"❌ Произошла ошибка при обработке результатов SVS: {e}"
            elif test_type == 'urica':
                if len(responses_for_test) < get_total_urica_questions():
                    self.bot.send_message(chat_id, f"❌ Тест URICA не завершен. Пожалуйста, ответьте на все вопросы.")
                    return
                scores_data = self.urica_scorer.calculate_scores(responses_for_test)
                if "error" in scores_data:
                    self.bot.send_message(chat_id, f"❌ {scores_data['error']}")
                    return 
                
                if scores_data:
                    results_message_text = f"📊 **Результаты Теста Стадий Изменений (URICA) для {user_name}** 📊\n\n"
                    results_message_text += "**Средние баллы по шкалам:**\n"
                    for scale, score in scores_data.get("scale_scores", {}).items():
                        if isinstance(score, (int, float)):
                            results_message_text += f"  • {scale.replace('_', ' ').title()}: {score:.2f}\n"
                        else:
                            results_message_text += f"  • {scale.replace('_', ' ').title()}: N/A\n"
                    
                    rci_value = scores_data.get('readiness_to_change_index')
                    rci_display = "N/A"
                    if isinstance(rci_value, (int, float)):
                        rci_display = f"{rci_value:.2f}"
                    
                    results_message_text += f"\n**Индекс Готовности к Изменениям (RCI):** {rci_display}\n"
                    results_message_text += f"**Определенная Стадия Изменений:** {scores_data.get('determined_stage', 'N/A')}\n"

                    # Сохранение результатов URICA в базу данных
                    db_scores_urica = scores_data # Сохраняем весь словарь результатов
                    responses_json_urica = json.dumps(responses_for_test) # Сериализуем ответы
                    self.db.save_test_result(session.session_id, user_id, 'urica', db_scores_urica, responses_json_urica)
                else:
                    results_message_text = "Не удалось рассчитать URICA результаты (scores_data is None)."
            elif test_type == 'dweck':
                if len(responses_for_test) < get_total_dweck_questions():
                    self.bot.send_message(chat_id, f"❌ Тест Двека не завершен. Пожалуйста, ответьте на все вопросы.")
                    return
                scores_data = self.dweck_scorer.calculate_scores(responses_for_test)
                if "error" in scores_data:
                    self.bot.send_message(chat_id, f"❌ {scores_data['error']}")
                    return 
                
                if scores_data and "scores" in scores_data:
                    dweck_scores = scores_data["scores"]
                    results_message_text = f"🧠 **Результаты Опросника Имплицитных Теорий (Двек) для {user_name}** 🧠\n\n"
                    
                    scale_names_display = {
                        "intelligence_growth_score": "Принятие теории наращиваемого интеллекта",
                        "personality_enrichable_score": "Принятие теории обогащаемой личности",
                        "learning_goals_acceptance_score": "Принятие целей обучения",
                        "learning_self_assessment_score": "Самооценка обучения"
                    }
                    
                    for scale_key, display_name in scale_names_display.items():
                        score = dweck_scores.get(scale_key)
                        if isinstance(score, (int, float)):
                            results_message_text += f"  • **{display_name}:** {score:.2f}\n"
                        else:
                            results_message_text += f"  • **{display_name}:** N/A\n"
                    results_message_text += "\n**Общая направленность (пример интерпретации):**\n"
                    results_message_text += "  (Более подробная интерпретация может быть добавлена здесь на основе специфических порогов).\n"
                else:
                    results_message_text = "Не удалось рассчитать результаты теста Двека (отсутствуют 'scores' в данных)."

                db_scores_dweck = scores_data.get("scores", {}) 
                responses_json_dweck = json.dumps(responses_for_test) 
                self.db.save_test_result(session.session_id, user_id, 'dweck', db_scores_dweck, responses_json_dweck)

            elif test_type == 'panas':
                if len(responses_for_test) < get_total_panas_questions():
                    self.bot.send_message(chat_id, f"❌ Тест ШПАНА не завершен. Пожалуйста, ответьте на все вопросы.")
                    return
                scores_data = self.panas_scorer.calculate_scores(responses_for_test)
                if "error" in scores_data:
                    self.bot.send_message(chat_id, f"❌ {scores_data['error']}")
                    return
                results_message_text = self.panas_scorer.format_panas_results_message(scores_data, user_name)
                db_scores = scores_data.get("scores", {})
                responses_json = self.panas_scorer.responses_to_json(responses_for_test)
                self.db.save_test_result(session.session_id, user_id, 'panas', db_scores, responses_json)

            elif test_type == 'self_efficacy':
                if len(responses_for_test) < get_total_self_efficacy_questions():
                    self.bot.send_message(chat_id, f"❌ Тест самоэффективности не завершен. Пожалуйста, ответьте на все вопросы.")
                    return
                scores_data = self.self_efficacy_scorer.calculate_scores(responses_for_test)
                if "error" in scores_data:
                    self.bot.send_message(chat_id, f"❌ {scores_data['error']}")
                    return
                results_message_text = self.self_efficacy_scorer.format_self_efficacy_results_message(scores_data, user_name)
                db_scores = scores_data.get("scores", {})
                responses_json = self.self_efficacy_scorer.responses_to_json(responses_for_test)
                self.db.save_test_result(session.session_id, user_id, 'self_efficacy', db_scores, responses_json)

            elif test_type == 'cdrisc':
                if len(responses_for_test) < self.cdrisc_scorer.MIN_ANSWERS_REQUIRED: # Use scorer's constant
                    self.bot.send_message(chat_id, f"❌ Тест CD-RISC не завершен. Пожалуйста, ответьте как минимум на {self.cdrisc_scorer.MIN_ANSWERS_REQUIRED} вопросов.")
                    return
                scores_data = self.cdrisc_scorer.calculate_scores(responses_for_test)
                if "error" in scores_data:
                    self.bot.send_message(chat_id, f"❌ {scores_data['error']}")
                    return
                
                if scores_data:
                    results_message_text = f"🛡️ **Результаты Теста Устойчивости (CD-RISC) для {user_name}** 🛡️\n\n"
                    results_message_text += f"Количество отвеченных вопросов: {scores_data.get('answered_questions_count', 'N/A')}\n"
                    results_message_text += f"Общий балл: {scores_data.get('total_score', 'N/A')}\n"
                    results_message_text += f"Классический балл (0-100): {scores_data.get('classic_score', 'N/A')}\n"
                    results_message_text += f"**Интерпретация:** {scores_data.get('interpretation_category', 'N/A')}\n\n"
                    
                    results_message_text += "**Баллы по подшкалам:**\n"
                    subscale_names_display = {
                        "personal_competence_persistence": "Личная компетентность / настойчивость",
                        "instincts_stress_as_hardening": "Инстинкты / стресс как «закалка»",
                        "acceptance_of_change_support": "Принятие перемен / поддержка",
                        "control": "Контроль",
                        "spiritual_beliefs": "Духовные убеждения"
                    }
                    for scale_key, display_name in subscale_names_display.items():
                        score = scores_data.get("subscale_scores", {}).get(scale_key)
                        display_score = score if score is not None else "N/A"
                        results_message_text += f"  • {display_name}: {display_score}\n"
                    
                    results_message_text += "\n*Примечание: Если выборка небольшая, рекомендуется опираться на общий балл, так как факторная структура CD-RISC может быть нестабильна.*"

                    db_scores_cdrisc = {
                        "total_score": scores_data.get('total_score'),
                        "classic_score": scores_data.get('classic_score'),
                        "interpretation_category": scores_data.get('interpretation_category'),
                        "subscale_personal_competence_persistence": scores_data.get("subscale_scores", {}).get("personal_competence_persistence"),
                        "subscale_instincts_stress_as_hardening": scores_data.get("subscale_scores", {}).get("instincts_stress_as_hardening"),
                        "subscale_acceptance_of_change_support": scores_data.get("subscale_scores", {}).get("acceptance_of_change_support"),
                        "subscale_control": scores_data.get("subscale_scores", {}).get("control"),
                        "subscale_spiritual_beliefs": scores_data.get("subscale_scores", {}).get("spiritual_beliefs"),
                        "answered_questions_count": scores_data.get('answered_questions_count')
                    }
                    responses_json_cdrisc = self.cdrisc_scorer.responses_to_json(responses_for_test)
                    self.db.save_test_result(session.session_id, user_id, 'cdrisc', db_scores_cdrisc, responses_json_cdrisc)
                else:
                    results_message_text = "Не удалось рассчитать результаты теста CD-RISC."

            elif test_type == 'rfq':
                if len(responses_for_test) < get_total_rfq_questions(): # RFQ requires all questions
                    self.bot.send_message(chat_id, f"❌ Тест RFQ не завершен. Пожалуйста, ответьте на все {get_total_rfq_questions()} вопросов.")
                    return
                scores_data = self.rfq_scorer.calculate_scores(responses_for_test)
                if "error" in scores_data and scores_data["error"]:
                    self.bot.send_message(chat_id, f"❌ {scores_data['error']}")
                    return
                
                if scores_data:
                    promotion_score = scores_data.get('promotion_score')
                    prevention_score = scores_data.get('prevention_score')
                    results_message_text = f"🎯 **Результаты Теста Диагностика фокуса регуляции (RFQ) для {user_name}** 🎯\n\n"
                    results_message_text += f"**Фокус Продвижения:** {promotion_score if promotion_score is not None else 'N/A'}\n"
                    results_message_text += f"*(Диапазон: 6-30. Среднее: 21.3 ± 4.3)*\n\n"
                    results_message_text += f"**Фокус Профилактики:** {prevention_score if prevention_score is not None else 'N/A'}\n"
                    results_message_text += f"*(Диапазон: 5-25. Среднее: 16.6 ± 3.8)*\n\n"
                    
                    results_message_text += "**Краткая интерпретация:**\n"
                    if promotion_score is not None and prevention_score is not None:
                        if promotion_score > 21.3 + 4.3: # M + 1 SD
                            results_message_text += "- У вас выраженный фокус на Продвижение: ориентация на выгоду, достижения, рост, вы обычно готовы к риску для достижения своих целей.\n"
                        elif promotion_score < 21.3 - 4.3: # M - 1 SD
                            results_message_text += "- У вас слабо выраженный фокус на Продвижение.\n"
                        else:
                            results_message_text += "- Ваш фокус на Продвижение находится в среднем диапазоне.\n"
                        
                        if prevention_score > 16.6 + 3.8: # M + 1 SD
                            results_message_text += "- У вас выраженный фокус на Профилактику: ориентация на безопасность, избегание неудач, точность и контроль.\n"
                        elif prevention_score < 16.6 - 3.8: # M - 1 SD
                            results_message_text += "- У вас слабо выраженный фокус на Профилактику.\n"
                        else:
                            results_message_text += "- Ваш фокус на Профилактику находится в среднем диапазоне.\n"
                    else:
                        results_message_text += "Интерпретация невозможна из-за ошибки в расчетах.\n"
                    
                    db_scores_rfq = {
                        "promotion_score": promotion_score,
                        "prevention_score": prevention_score
                    }
                    responses_json_rfq = self.rfq_scorer.responses_to_json(responses_for_test)
                    self.db.save_test_result(session.session_id, user_id, 'rfq', db_scores_rfq, responses_json_rfq)
                else:
                    results_message_text = "Не удалось рассчитать результаты теста RFQ."

            elif test_type == 'pid5bfm':
                if len(responses_for_test) < get_total_pid5bfm_questions():
                    self.bot.send_message(chat_id, f"❌ Тест PID-5-BF+M не завершен. Пожалуйста, ответьте на все {get_total_pid5bfm_questions()} вопросов.")
                    return
                scores_data = self.pid5bfm_scorer.calculate_scores(responses_for_test)
                if scores_data:
                    results_message_text = self.pid5bfm_scorer.format_results_message(scores_data, user_name)
                    db_scores_pid5bfm = scores_data.get("scores", {})
                    responses_json_pid5bfm = self.pid5bfm_scorer.responses_to_json(responses_for_test)
                    self.db.save_test_result(session.session_id, user_id, 'pid5bfm', db_scores_pid5bfm, responses_json_pid5bfm)
                else:
                    results_message_text = "Не удалось рассчитать результаты теста PID-5-BF+M."
            
            # Mark this part as completed in session
            self.session_manager.complete_test_part(user_id, test_type)
            logger.info(f"_complete_test_part: User {user_id} session.test_completed after update for {test_type}: {session.test_completed}")
            
            # Send results for the completed test part
            # Экранируем подчеркивание в названии теста для корректного Markdown
            escaped_test_type_upper = test_type.upper().replace('_', '\\_')
            self.bot.send_message(chat_id, f"🎉 **Тест {escaped_test_type_upper} завершен!**\n\n{results_message_text}", parse_mode='Markdown')
            logger.info(f"Test part {test_type} completed for user {user_id}")

            # Offer next test or finalize
            self._offer_next_test(chat_id, user_id)

        except Exception as e:
            logger.error(f"Error completing test part {test_type} for user {user_id}: {e}")
            self.bot.send_message(chat_id, f"❌ Ошибка при расчете результатов для теста {test_type.upper()}.")

    def _offer_next_test(self, chat_id: int, user_id: int):
        """Offers the next available test to the user or concludes."""
        # Проверяем, остались ли еще непройденные тесты
        completed_tests_from_db = self.db.get_completed_tests_for_user(user_id)
        
        available_tests = []
        if not completed_tests_from_db.get('hexaco', False): available_tests.append(("HEXACO Личностный Тест", "hexaco"))
        if not completed_tests_from_db.get('sds', False): available_tests.append(("Тест Самодетерминации (SDS)", "sds"))
        if not completed_tests_from_db.get('svs', False): available_tests.append(("Тест Ценностей Шварца (SVS)", "svs"))
        if not completed_tests_from_db.get('panas', False): available_tests.append(("Шкала Позитивного и Негативного Аффекта (ШПАНА)", "panas"))
        if not completed_tests_from_db.get('self_efficacy', False): available_tests.append(("Тест Самоэффективности (General Self-Efficacy Scale)", "self_efficacy"))
        if not completed_tests_from_db.get('cdrisc', False): available_tests.append(("Тест Устойчивости (CD-RISC)", "cdrisc"))
        if not completed_tests_from_db.get('rfq', False): available_tests.append(("Тест Диагностика фокуса регуляции (RFQ)", "rfq"))
        if not completed_tests_from_db.get('pid5bfm', False): available_tests.append(("Опросник личности PID-5-BF+M", "pid5bfm"))
        
        if not available_tests:
            # Все тесты завершены! Генерируем обновленный отчет
            logger.info(f"_offer_next_test: All tests completed for user {user_id}. Generating updated report.")
            self.bot.send_message(chat_id, "🎉 Поздравляем! Вы завершили все доступные тесты!")
            
            # Генерируем новый отчет с обновленными данными
            updated_report_path = self._generate_user_report(user_id)
            if updated_report_path:
                logger.info(f"_offer_next_test: Updated report generated: {updated_report_path}")
                
                # Проверяем и генерируем обновленный профиль
                from pathlib import Path
                current_script_path = Path(__file__).resolve()
                hexaco_bot_root = current_script_path.parent.parent.parent 
                user_profile_dir_absolute = hexaco_bot_root / "user_profile"
                user_profile_filename = f"{user_id}_profile.json"
                user_profile_filepath = user_profile_dir_absolute / user_profile_filename
                
                try:
                    with open(updated_report_path, 'r', encoding='utf-8') as f_report:
                        report_content = json.load(f_report)
                    
                    all_user_tests_data = report_content.get("tests")
                    
                    if all_user_tests_data:
                        # ВРЕМЕННО ОТКЛЮЧЕНО: Интерпретация данных пользователя с помощью AI
                        # from hexaco_bot.src.psychoprofile.profiler import generate_and_save_psychoprofile
                        logger.info(f"_offer_next_test: AI profile generation is temporarily disabled for user {user_id}")
                        # logger.info(f"_offer_next_test: Generating updated psychoprofile for user {user_id}")
                        # saved_profile_path = generate_and_save_psychoprofile(
                        #     user_id=str(user_id),
                        #     all_user_tests_data=all_user_tests_data,
                        #     profile_dir=str(user_profile_dir_absolute)
                        # )
                        # if saved_profile_path:
                        #     logger.info(f"_offer_next_test: Updated psychoprofile generated: {saved_profile_path}")
                        # else:
                        #     logger.error(f"_offer_next_test: Failed to generate updated psychoprofile for user {user_id}")
                    else:
                        logger.error(f"_offer_next_test: No test data found in updated report for user {user_id}")
                        
                except Exception as e:
                    logger.error(f"_offer_next_test: Error processing updated report for user {user_id}: {e}")
                
                self.bot.send_message(chat_id, "📊 Ваш обновленный отчет готов! Подробный просмотр всех результатов доступен в меню.")
            else:
                logger.error(f"_offer_next_test: Failed to generate updated report for user {user_id}")
                self.bot.send_message(chat_id, "⚠️ Возникла проблема при создании обновленного отчета.")
            
            # Устанавливаем флаг завершения всех тестов
            self.db.set_overall_completion_status(user_id)
            
        else:
            # Еще есть непройденные тесты
            self.bot.send_message(chat_id, "Вы можете начать следующий тест командой /test или посмотреть результаты.")
        
        self.session_manager.update_session_state(user_id, 'menu') 

    def show_overall_results_menu(self, chat_id: int, user_id: int):
        """Placeholder: Shows a menu to view results of all completed tests."""
        # This needs to be implemented: fetch all test results for the user and present them.
        # For now, just acknowledge.
        # We could try to get all results and send a summary if any.
        all_results_info = []
        hexaco_res = self.db.get_user_test_results(user_id, 'hexaco')
        if hexaco_res:
            all_results_info.append(f"HEXACO (пройдено {len(hexaco_res)} раз)")
        sds_res = self.db.get_user_test_results(user_id, 'sds')
        if sds_res:
            all_results_info.append(f"SDS (пройдено {len(sds_res)} раз)")
        svs_res = self.db.get_user_test_results(user_id, 'svs')
        if svs_res:
            all_results_info.append(f"SVS (пройдено {len(svs_res)} раз)")
        urica_res = self.db.get_user_test_results(user_id, 'urica')
        if urica_res:
            all_results_info.append(f"URICA (пройдено {len(urica_res)} раз)")
        dweck_res = self.db.get_user_test_results(user_id, 'dweck')
        if dweck_res:
            all_results_info.append(f"Двек (пройдено {len(dweck_res)} раз)")
        panas_res = self.db.get_user_test_results(user_id, 'panas')
        if panas_res:
            all_results_info.append(f"ШПАНА (пройдено {len(panas_res)} раз)")
        self_efficacy_res = self.db.get_user_test_results(user_id, 'self_efficacy')
        if self_efficacy_res:
            all_results_info.append(f"Самоэффективность (пройдено {len(self_efficacy_res)} раз)")
        cdrisc_res = self.db.get_user_test_results(user_id, 'cdrisc')
        if cdrisc_res:
            all_results_info.append(f"Тест Устойчивости CD-RISC (пройдено {len(cdrisc_res)} раз)")
        rfq_res = self.db.get_user_test_results(user_id, 'rfq')
        if rfq_res:
            all_results_info.append(f"Тест RFQ (пройдено {len(rfq_res)} раз)")
        pid5bfm_res = self.db.get_user_test_results(user_id, 'pid5bfm')
        if pid5bfm_res:
            all_results_info.append(f"Опросник личности PID-5-BF+M (пройдено {len(pid5bfm_res)} раз)")

        if not all_results_info:
            self.bot.send_message(chat_id, "Вы еще не завершили ни одного теста. Используйте /test или кнопку в меню /start, чтобы начать.")
        else:
            self.bot.send_message(chat_id, "Вы завершили следующие тесты:\n- " + "\n- ".join(all_results_info) + "\n\nПодробный просмотр всех результатов будет доступен здесь позже.")
    
    def _handle_view_results_callback(self, call: CallbackQuery):
        """Handle view results callback."""
        user_id = call.from_user.id
        
        # Get latest results
        results = self.db.get_user_results(user_id)
        if not results:
            self._safe_answer_callback_query(call.id, "❌ Результаты не найдены")
            return
        
        latest_result = results[0]  # Most recent
        
        # Reconstruct scores from database
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
        
        results_message = self.hexaco_scorer.format_results_message(scores, user_name)
        results_message += f"\n\n📅 Дата прохождения: {latest_result['created_at']}"
        
        self._safe_answer_callback_query(call.id, "📊 Показываю результаты")
        self.bot.send_message(call.message.chat.id, results_message, parse_mode='Markdown')
    
    def _create_progress_bar(self, percent: float, length: int = 10) -> str:
        """Create text progress bar."""
        filled = int(length * percent / 100)
        bar = '█' * filled + '░' * (length - filled)
        return f"[{bar}]"
    
    def show_test_menu(self, context: Union[Message, CallbackQuery]):
        """Show test menu with options for registered user, adaptable for Message or CallbackQuery context."""
        user_id = None
        chat_id = None
        user_first_name = None # Will be fetched from user_data

        if isinstance(context, CallbackQuery):
            call = context
            user_id = call.from_user.id
            chat_id = call.message.chat.id
            logger.info(f"show_test_menu called for user_id: {user_id} via CallbackQuery from chat_id: {chat_id}")
        elif isinstance(context, Message):
            message = context
            user_id = message.from_user.id
            chat_id = message.chat.id
            logger.info(f"show_test_menu called for user_id: {user_id} via Message from chat_id: {chat_id}")
        else:
            logger.error(f"show_test_menu called with invalid context type: {type(context)}")
            # Cannot send a message if chat_id is unknown
            return

        user_data = self.db.get_user(user_id)
        logger.info(f"show_test_menu: user_data from DB for user_id {user_id}: {user_data}")
        
        if not user_data:
            logger.error(f"show_test_menu: user_data is None for user_id {user_id}. Sending registration prompt.")
            self.bot.send_message(chat_id, "❌ Сначала нужно зарегистрироваться! Отправьте /start для регистрации.")
            return
        
        user_first_name = user_data.get('first_name', 'Пользователь') # Default if not found

        # If PAEI or MBTI are missing, direct to StartHandler flow first.
        if not user_data.get('paei_index') or not user_data.get('mbti_type'):
            logger.warning(f"show_test_menu: User {user_id} is missing PAEI or MBTI. PAEI: {user_data.get('paei_index')}, MBTI: {user_data.get('mbti_type')}")
            self.bot.send_message(chat_id, 
                                  "Пожалуйста, завершите начальную настройку, предоставив PAEI-индекс и MBTI-тип. "
                                  "Команда /start поможет вам в этом.")
            return

        self._start_test_flow(chat_id, user_id, user_first_name)

    def _generate_user_report(self, user_id: int) -> Optional[str]: # Изменен тип возвращаемого значения
        """Generate and send a JSON report of all user data and test results.
        Returns the path to the generated report file on success, None otherwise.
        """
        logger.info(f"Generating comprehensive report for user {user_id}")
        
        report_data = self.db.get_user_data_for_report(user_id)
        
        if not report_data:
            logger.error(f"Could not retrieve data for report for user {user_id}")
            try:
                self.bot.send_message(user_id, "❌ Не удалось создать отчет: данные пользователя не найдены.")
            except Exception as e:
                logger.error(f"Failed to send report error to user {user_id}: {e}")
            return None # Возвращаем None при ошибке

        final_report_content = report_data

        # Используем Path для работы с путями
        current_script_path = Path(__file__).resolve()
        hexaco_bot_root = current_script_path.parent.parent.parent 
        reports_dir_path = hexaco_bot_root / "user_reports"

        if not reports_dir_path.exists():
            reports_dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {reports_dir_path}")

        username = report_data.get('username', f"user_{user_id}")
        safe_username = "".join(c if c.isalnum() else "_" for c in str(username))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Имя файла без пути
        report_file_basename = f"report_{safe_username}_{timestamp}.json"
        # Полный путь к файлу
        report_filepath = reports_dir_path / report_file_basename

        try:
            with open(report_filepath, 'w', encoding='utf-8') as f:
                json.dump(final_report_content, f, ensure_ascii=False, indent=4)
            logger.info(f"User report for {user_id} generated and saved to {report_filepath}")
            
            with open(report_filepath, 'rb') as f_rb:
                self.bot.send_document(user_id, f_rb, caption=f"📊 Ваш полный отчет, {report_data.get('first_name', '')}.")
            
            return str(report_filepath) # Возвращаем путь к файлу

        except IOError as e:
            logger.error(f"IOError writing report for user {user_id} to {report_filepath}: {e}")
            try:
                self.bot.send_message(user_id, "❌ Ошибка при сохранении файла отчета.")
            except Exception as send_e:
                logger.error(f"Failed to send report IO error to user {user_id}: {send_e}")
            return None # Возвращаем None при ошибке
        except Exception as e:
            logger.error(f"Unexpected error generating report for user {user_id}: {e}")
            try:
                self.bot.send_message(user_id, "❌ Произошла непредвиденная ошибка при создании отчета.")
            except Exception as send_e:
                logger.error(f"Failed to send report generation error to user {user_id}: {send_e}")
            return None # Возвращаем None при ошибке