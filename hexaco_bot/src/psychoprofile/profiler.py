import json
import os
import logging
from pathlib import Path
import requests # Для HTTP-запросов к API ChatGPT
from typing import Optional

# Импортируем API ключ из настроек
try:
    from hexaco_bot.config.settings import CHATGPT_API_KEY
except ImportError:
    # Попытка импорта, если скрипт запускается из другого места
    # Это может быть полезно для process_existing_reports.py
    # Однако, если settings.py не может быть найден, это проблема конфигурации.
    CHATGPT_API_KEY = None
    logging.warning("Could not import CHATGPT_API_KEY from settings. Make sure it is configured.")

# Schema version from the prompt
SCHEMA_VERSION = "1.5"

# The detailed prompt for ChatGPT
CHATGPT_PROMPT_TEMPLATE = """
You are a psychology expert AI. Based on the provided psychological test results, generate a comprehensive psychoprofile in JSON format.

**Output Language Constraint: The entire JSON output, including all string values, MUST be in Russian.** Do not use any other languages.

The JSON schema you MUST strictly follow is:
{
  "schema_version": "1.5",
  "user_info": {
    "type": "object",
    "description": "User's basic info (if available).",
    "properties": {
      "user_id": {"type": "string", "description": "User ID."},
      "first_name": {"type": ["string", "null"], "description": "User's first name."},
      "username": {"type": ["string", "null"], "description": "User's username."}
    }
  },
  "profile_generated_at": {"type": "string", "format": "date-time", "description": "Profile generation timestamp."},
  "personality": {
    "type": "object",
    "description": "HEXACO based personality traits.",
    "properties": {
      "honesty_humility": {"type": "object", "properties": {"score": {"type": "number"}, "level": {"type": "string", "enum": ["low", "medium", "high"]}}, "description": "HEXACO Honesty-Humility."},
      "emotionality": {"type": "object", "properties": {"score": {"type": "number"}, "level": {"type": "string", "enum": ["low", "medium", "high"]}}, "description": "HEXACO Emotionality."},
      "extraversion": {"type": "object", "properties": {"score": {"type": "number"}, "level": {"type": "string", "enum": ["low", "medium", "high"]}}, "description": "HEXACO Extraversion."},
      "agreeableness": {"type": "object", "properties": {"score": {"type": "number"}, "level": {"type": "string", "enum": ["low", "medium", "high"]}}, "description": "HEXACO Agreeableness."},
      "conscientiousness": {"type": "object", "properties": {"score": {"type": "number"}, "level": {"type": "string", "enum": ["low", "medium", "high"]}}, "description": "HEXACO Conscientiousness."},
      "openness_to_experience": {"type": "object", "properties": {"score": {"type": "number"}, "level": {"type": "string", "enum": ["low", "medium", "high"]}}, "description": "HEXACO Openness."},
      "altruism": {"type": ["object", "null"], "properties": {"score": {"type": "number"}, "level": {"type": "string", "enum": ["low", "medium", "high"]}}, "description": "HEXACO Altruism (if available)."},
      "interpretation": {
        "type": "string",
        "description": "1 neutral, descriptive sentence on personality. Russian."
      },
      "interaction_advice": {
        "type": "string",
        "description": "1-2 specific, actionable work interaction sentences based on personality. Russian. No vague statements."
      }
    },
    "required": ["honesty_humility", "emotionality", "extraversion", "agreeableness", "conscientiousness", "openness_to_experience", "interpretation", "interaction_advice"]
  },
  "motivation": {
    "type": "object",
    "description": "Motivational aspects (SDS, Dweck, RFQ).",
    "properties": {
      "sds_autonomy": {"type": ["object", "null"], "properties": {"score": {"type": "number"}, "level": {"type": "string", "enum": ["low", "medium", "high"]}}, "description": "SDS Autonomy."},
      "sds_competence": {"type": ["object", "null"], "properties": {"score": {"type": "number"}, "level": {"type": "string", "enum": ["low", "medium", "high"]}}, "description": "SDS Competence."},
      "sds_relatedness": {"type": ["object", "null"], "properties": {"score": {"type": "number"}, "level": {"type": "string", "enum": ["low", "medium", "high"]}}, "description": "SDS Relatedness."},
      "dweck_mindset": {"type": ["object", "null"], "properties": {"score": {"type": "number"}, "type_is_growth": {"type": "boolean"}}, "description": "Dweck Mindset (growth=true)."},
      "rfq_promotion": {"type": ["object", "null"], "properties": {"score": {"type": "number"}, "level": {"type": "string", "enum": ["low", "medium", "high"]}}, "description": "RFQ Promotion focus."},
      "rfq_prevention": {"type": ["object", "null"], "properties": {"score": {"type": "number"}, "level": {"type": "string", "enum": ["low", "medium", "high"]}}, "description": "RFQ Prevention focus."},
      "interpretation": {
        "type": "string",
        "description": "1 neutral, descriptive sentence on motivation. Russian."
      },
      "interaction_advice": {
        "type": "string",
        "description": "1-2 specific, actionable work motivation/engagement sentences. Russian. No vague statements."
      }
    },
    "required": ["interpretation", "interaction_advice"]
  },
  "affect": {
    "type": "object",
    "description": "Affective states (PANAS).",
    "properties": {
      "panas_positive_affect": {"type": ["object", "null"], "properties": {"score": {"type": "number"}, "level": {"type": "string", "enum": ["low", "medium", "high"]}}, "description": "PANAS Positive Affect."},
      "panas_negative_affect": {"type": ["object", "null"], "properties": {"score": {"type": "number"}, "level": {"type": "string", "enum": ["low", "medium", "high"]}}, "description": "PANAS Negative Affect."},
      "interpretation": {
        "type": "string",
        "description": "1 neutral, descriptive sentence on affect. Russian."
      },
      "interaction_advice": {
        "type": "string",
        "description": "1-2 specific, actionable work interaction sentences considering affect. Russian. No vague statements."
      }
    },
    "required": ["interpretation", "interaction_advice"]
  },
  "values_Schwartz": {
    "type": "object",
    "description": "Personal values (Schwartz SVS), top 3.",
    "properties": {
      "dominant_values": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Top 3 dominant values (e.g., 'Самостоятельность'). Values in Russian."
      },
      "interpretation": {
        "type": "string",
        "description": "1 neutral, descriptive sentence on core values. Russian."
      },
      "interaction_advice": {
        "type": "string",
        "description": "1-2 specific, actionable work alignment sentences for values. Russian. No vague statements."
      }
    },
    "required": ["dominant_values", "interpretation", "interaction_advice"]
  },
  "resilience": {
    "type": "object",
    "description": "Resilience (CD-RISC).",
    "properties": {
      "cdrisc_score": {"type": ["number", "null"]},
      "resilience_level": {"type": ["string", "null"], "enum": ["low", "medium", "high"], "description": "Overall resilience level."},
      "interpretation": {
        "type": "string",
        "description": "1 neutral, descriptive sentence on resilience. Russian."
      },
      "interaction_advice": {
        "type": "string",
        "description": "1-2 specific, actionable work support/leverage sentences for resilience. Russian. No vague statements."
      }
    },
    "required": ["interpretation", "interaction_advice"]
  },
  "self_efficacy": {
    "type": "object",
    "description": "General self-efficacy.",
    "properties": {
      "gse_score": {"type": ["number", "null"]},
      "self_efficacy_level": {"type": ["string", "null"], "enum": ["low", "medium", "high"], "description": "Overall self-efficacy level."},
      "interpretation": {
        "type": "string",
        "description": "1 neutral, descriptive sentence on self-efficacy. Russian."
      },
      "interaction_advice": {
        "type": "string",
        "description": "1-2 specific, actionable work task/support sentences for self-efficacy. Russian. No vague statements."
      }
    },
    "required": ["interpretation", "interaction_advice"]
  },
  "change_stage": {
    "type": "object",
    "description": "Readiness for change (URICA).",
    "properties": {
      "urica_dominant_stage": {"type": ["string", "null"], "enum": ["precontemplation", "contemplation", "preparation", "action", "maintenance"], "description": "Dominant stage of change."},
      "urica_score": {"type": ["number", "null"], "description": "General readiness score (if applicable)."},
      "interpretation": {
        "type": "string",
        "description": "1 neutral, descriptive sentence on change readiness. Russian."
      },
      "interaction_advice": {
        "type": "string",
        "description": "1-2 specific, actionable work change initiative sentences. Russian. No vague statements."
      }
    },
    "required": ["interpretation", "interaction_advice"]
  },
  "summary": {
    "type": "string",
    "description": "Overall summary (4-6 sentences) integrating key findings. Conclude with 2-3 highly practical, actionable general work interaction tips (communication, collaboration, or motivation). Concrete & useful. Start with 'Психологический профиль...'. Entire summary & tips in Russian."
  }
}
Do not include any explanations, comments, or markdown formatting (like ```json) in your response. Only the raw JSON.
Input test data will be provided after 'USER_DATA_JSON:'.
USER_DATA_JSON:
"""

logger = logging.getLogger(__name__)

def create_user_profile_directory_if_not_exists(base_path: str = "hexaco_bot/user_profile"):
    """Creates the user profile directory if it doesn't exist."""
    abs_base_path = Path(base_path).resolve()
    if not abs_base_path.exists():
        abs_base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory created: {abs_base_path}")

def format_input_for_chatgpt(user_id: str, all_user_tests_data: dict) -> str:
    """
    Formats the user ID and test data into the JSON string expected by the ChatGPT prompt.
    """
    input_payload = {
        "user_id": user_id,
        "tests": all_user_tests_data
    }
    return json.dumps(input_payload, ensure_ascii=False, indent=2)

def generate_and_save_psychoprofile(user_id: str, all_user_tests_data: dict, profile_dir: str = "hexaco_bot/user_profile") -> str | None:
    """
    Generates a psychoprofile by calling ChatGPT API and saves it to a JSON file.

    Returns:
        The file path of the saved psychoprofile JSON, or None if an error occurred.
    """
    create_user_profile_directory_if_not_exists(profile_dir)

    if not CHATGPT_API_KEY:
        logger.error("CHATGPT_API_KEY is not configured. Cannot generate psychoprofile.")
        return None

    formatted_input_json = format_input_for_chatgpt(user_id, all_user_tests_data)
    
    logger.info(f"Attempting to generate psychoprofile for user {user_id} via ChatGPT API.")
    logger.debug(f"Input data for ChatGPT for user {user_id}:\n{formatted_input_json}")

    headers = {
        "Authorization": f"Bearer {CHATGPT_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": CHATGPT_PROMPT_TEMPLATE},
            {"role": "user", "content": formatted_input_json}
        ],
        "temperature": 0.5, 
        "max_tokens": 3000, # Increased from 1800 to 3000
        "response_format": {"type": "json_object"}
    }

    logger.debug(f"Sending payload to ChatGPT: {json.dumps(payload, ensure_ascii=False)[:500]}...") # Log first 500 chars

    psychoprofile_json_string = None
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("choices") and len(response_data["choices"]) > 0:
                message_content = response_data["choices"][0].get("message", {}).get("content")
                if message_content:
                    psychoprofile_json_string = message_content
                    logger.info(f"Successfully received response from ChatGPT for user {user_id}.")
                    logger.debug(f"ChatGPT response content:\n{psychoprofile_json_string}")
                else:
                    logger.error(f"ChatGPT API response for user {user_id} is missing message content. Response: {response_data}")
            else:
                logger.error(f"ChatGPT API response for user {user_id} is missing choices or choices are empty. Response: {response_data}")
        else:
            logger.error(f"ChatGPT API request failed for user {user_id}. Status: {response.status_code}. Response: {response.text}")
            # Дополнительная информация об ошибке от OpenAI, если есть
            try:
                error_details = response.json().get("error", {}).get("message", "No specific error message from API.")
                logger.error(f"OpenAI API Error Details: {error_details}")
            except json.JSONDecodeError:
                logger.error("Could not parse error details from OpenAI API response.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during ChatGPT API request for user {user_id}: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response from ChatGPT API for user {user_id}: {e}. Response text: {response.text if 'response' in locals() else 'N/A'}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during ChatGPT API call for user {user_id}: {e}")

    if not psychoprofile_json_string:
        logger.error(f"Failed to obtain valid psychoprofile JSON string from ChatGPT for user {user_id}.")
        return None

    # Валидация JSON (простая проверка, что это валидный JSON)
    try:
        json.loads(psychoprofile_json_string) # Проверяем, что строка парсится как JSON
    except json.JSONDecodeError as e:
        logger.error(f"The string received from ChatGPT for user {user_id} is not valid JSON: {e}")
        logger.error(f"Problematic string: \n{psychoprofile_json_string}")
        # Можно попытаться "очистить" вывод ChatGPT, если он добавляет ```json ... ``` обертку
        if psychoprofile_json_string.strip().startswith("```json") and psychoprofile_json_string.strip().endswith("```"):
            logger.info("Attempting to clean JSON string by removing markdown code block markers.")
            cleaned_string = psychoprofile_json_string.strip()[7:-3].strip() # Убираем ```json и ```
            try:
                json.loads(cleaned_string)
                psychoprofile_json_string = cleaned_string
                logger.info("Successfully cleaned JSON string.")
            except json.JSONDecodeError as e2:
                logger.error(f"Cleaned string is still not valid JSON for user {user_id}: {e2}")
                logger.error(f"Cleaned string was: \n{cleaned_string}")
                return None
        else:
            return None # Если это не типичная обертка, то возвращаем ошибку

    file_name = f"{user_id}_profile.json"
    abs_profile_dir = Path(profile_dir).resolve()
    file_path = abs_profile_dir / file_name

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(psychoprofile_json_string)
        logger.info(f"Psychoprofile for user {user_id} saved to: {file_path}")
        return str(file_path)
    except IOError as e:
        logger.error(f"Could not write psychoprofile to {file_path} for user {user_id}: {e}")
        return None


def process_single_report_file(report_filepath: Path, profiles_base_dir: Path) -> bool:
    """
    Processes a single user report JSON file to generate a psychoprofile.
    """
    try:
        logger.info(f"Processing report file: {report_filepath}")

        if not report_filepath.exists():
            logger.warning(f"Report file {report_filepath} does not exist. Skipping.")
            return False

        user_id_from_filename = report_filepath.stem
        report_data_content = None
        try:
            with open(report_filepath, 'r', encoding='utf-8') as f:
                report_data_content = json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from report file {report_filepath}. Skipping.")
            return False
        except Exception as e:
            logger.error(f"Error reading report file {report_filepath}: {e}. Skipping.")
            return False

        if not isinstance(report_data_content, dict):
            logger.warning(f"Report file {report_filepath} does not contain a dictionary. Skipping.")
            return False
        
        # Извлекаем user_id и данные тестов из содержимого файла отчета.
        # Структура файла отчета: { "user_id": "actual_user_id", "tests": { ... } }
        # или просто { ... данные тестов ... } если user_id берется из имени файла.
        # В нашем format_input_for_chatgpt user_id передается отдельно,
        # а all_user_tests_data - это словарь с самими тестами.
        
        # Если файл отчета содержит ключ 'user_id', используем его.
        # Иначе, используем user_id из имени файла.
        actual_user_id = report_data_content.get("user_id", user_id_from_filename)
        all_tests_data = report_data_content.get("tests", report_data_content) # Если нет ключа 'tests', то весь файл - это тесты

        if not isinstance(all_tests_data, dict) or not all_tests_data:
            logger.error(f"No valid test data found in report {report_filepath} for user {actual_user_id}. Skipping.")
            return False

        # Проверка, существует ли уже профиль (опционально, чтобы не перезаписывать)
        # profile_filename = f"{actual_user_id}_profile.json"
        # profile_filepath = profiles_base_dir / profile_filename
        # if profile_filepath.exists():
        #     logger.info(f"Profile {profile_filepath} already exists for user {actual_user_id}. Skipping.")
        #     return True

        saved_profile_path = generate_and_save_psychoprofile(
            user_id=actual_user_id,
            all_user_tests_data=all_tests_data, 
            profile_dir=str(profiles_base_dir)
        )
        
        return bool(saved_profile_path)

    except Exception as e:
        logger.error(f"Unhandled error processing report file {report_filepath}: {e}")
        return False

# Example usage (can be run directly if this file is executed)
if __name__ == "__main__":
    # Настройка логирования для прямого запуска
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Running profiler.py directly for testing...")

    # Проверка наличия API ключа для теста
    if not CHATGPT_API_KEY:
        logger.error("CHATGPT_API_KEY is not set in environment. Please set it in your .env file for testing.")
        logger.error("Example .env content: CHATGPT_API_KEY=sk-YourActualOpenAIKeyHere")
    else:
        sample_user_id = "test_direct_002"
        sample_user_reports_data = {
            "PAEI": {"P_score": 30, "A_score": 25, "E_score": 35, "I_score": 20},
            "MBTI-16": {"type_code": "ISTP", "assertiveness_trait": "T"},
            "HEXACO": {"H": 4.5, "E": 3.8, "X": 4.1, "A": 3.5, "C": 4.2, "O": 4.0},
        }
        
        temp_profile_dir = Path("temp_user_profiles_real_api")
        logger.info(f"Test: Attempting to generate profile for {sample_user_id} in {temp_profile_dir}")
        
        saved_file = generate_and_save_psychoprofile(
            sample_user_id, 
            sample_user_reports_data, 
            profile_dir=str(temp_profile_dir)
        )
        
        if saved_file:
            logger.info(f"Test run complete. Profile saved to: {saved_file}")
            # try:
            #     with open(saved_file, 'r', encoding='utf-8') as f_prof:
            #         logger.info(f"Content of {saved_file}:\n{f_prof.read()}")
            # except Exception as e_read:
            #     logger.error(f"Could not read test profile: {e_read}")
        else:
            logger.error(f"Test run failed for user {sample_user_id}.")
        
        # # Clean up (optional)
        # import shutil
        # if temp_profile_dir.exists():
        #     shutil.rmtree(temp_profile_dir)
        #     logger.info(f"Cleaned up temporary directory: {temp_profile_dir}")
    logger.info("Profiler.py direct run finished.") 