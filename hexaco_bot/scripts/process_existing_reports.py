import os
import sys
import logging
from pathlib import Path

# --- Path Setup ---
# Определяем путь к текущему скрипту
SCRIPT_DIR = Path(__file__).resolve().parent
# Определяем корневую директорию проекта (предполагается, что scripts/ находится внутри hexaco_bot/, а hexaco_bot/ в корне проекта)
PROJECT_ROOT = SCRIPT_DIR.parent.parent 
# Добавляем корневую директорию проекта в sys.path для корректного импорта модулей
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Теперь можно импортировать из src или hexaco_bot.src
try:
    from hexaco_bot.src.psychoprofile.profiler import process_single_report_file
except ImportError as e:
    print(f"Critical Import Error: Could not import 'process_single_report_file'. Ensure the script is in the correct location and PROJECT_ROOT is set up properly.")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"sys.path: {sys.path}")
    print(f"Error details: {e}")
    sys.exit(1)

# --- Configuration ---
REPORTS_BASE_DIR_NAME = "hexaco_bot"
REPORTS_DIR_NAME = "user_reports"
PROFILES_DIR_NAME = "user_profile"

REPORTS_DIR = PROJECT_ROOT / REPORTS_BASE_DIR_NAME / REPORTS_DIR_NAME
PROFILES_DIR = PROJECT_ROOT / REPORTS_BASE_DIR_NAME / PROFILES_DIR_NAME

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler() # Вывод в консоль
    ]
)
logger = logging.getLogger(__name__)


def process_all_existing_reports():
    """Processes all existing .json user reports to generate psychoprofiles."""
    logger.info(f"Starting processing of existing reports in: {REPORTS_DIR}")
    logger.info(f"Profiles will be saved to: {PROFILES_DIR}")

    if not REPORTS_DIR.exists() or not REPORTS_DIR.is_dir():
        logger.error(f"Reports directory {REPORTS_DIR} does not exist or is not a directory. Aborting.")
        return

    # Создаем директорию для профилей, если она не существует
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)

    processed_files = 0
    successful_processing = 0
    failed_processing = 0

    report_files = list(REPORTS_DIR.glob("*.json"))

    if not report_files:
        logger.info("No .json report files found to process.")
        return

    logger.info(f"Found {len(report_files)} .json files to process.")

    for report_filepath in report_files:
        logger.info(f"--- Processing file: {report_filepath.name} ---")
        processed_files += 1
        # Передаем абсолютный путь к директории профилей
        success = process_single_report_file(report_filepath, PROFILES_DIR) 
        if success:
            logger.info(f"Successfully processed and generated profile for: {report_filepath.name}")
            successful_processing += 1
        else:
            logger.error(f"Failed to process report file: {report_filepath.name}")
            failed_processing += 1
        logger.info("-------------------------------------")
    
    logger.info("--- Batch Processing Summary ---")
    logger.info(f"Total files found: {len(report_files)}")
    logger.info(f"Files attempted to process: {processed_files}")
    logger.info(f"Successfully processed: {successful_processing}")
    logger.info(f"Failed to process: {failed_processing}")
    logger.info("Batch processing complete.")

if __name__ == "__main__":
    process_all_existing_reports() 