import os
import time
import json
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

try:
    from src.psychoprofile.profiler import process_single_report_file
except ImportError:
    # Fallback for when running from different directory
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    from hexaco_bot.src.psychoprofile.profiler import process_single_report_file

logger = logging.getLogger(__name__)

class ReportHandler(FileSystemEventHandler):
    """Обработчик событий для файлов user_reports."""
    
    def __init__(self, reports_dir="hexaco_bot/user_reports", profiles_dir="hexaco_bot/user_profile"):
        self.reports_dir = Path(reports_dir)
        self.profiles_dir = Path(profiles_dir)
        
        # Создаём директории, если их нет
        self.reports_dir.mkdir(exist_ok=True, parents=True)
        self.profiles_dir.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"Наблюдатель ReportHandler инициализирован. Отслеживаем: {self.reports_dir}, Профили в: {self.profiles_dir}")

    def on_created(self, event):
        """Вызывается при создании файла."""
        if event.is_directory:
            return
        
        filepath = Path(event.src_path)
        logger.debug(f"File creation event: {filepath} in {self.reports_dir}")

        # Проверяем, что это JSON-файл в нужной директории
        if filepath.suffix.lower() == '.json' and self.reports_dir.resolve() in filepath.resolve().parents:
            logger.info(f"Обнаружен новый файл отчета: {filepath}. Запускаю обработку.")
            # Используем новую функцию для обработки файла
            # Добавляем небольшую задержку перед обработкой, чтобы файл успел полностью записаться
            time.sleep(1) 
            success = process_single_report_file(filepath, self.profiles_dir)
            if success:
                logger.info(f"Файл отчета {filepath} успешно обработан.")
            else:
                logger.error(f"Ошибка при обработке файла отчета {filepath}.")
        else:
            logger.debug(f"Файл {filepath} не является JSON или не в отслеживаемой директории. Пропускаю.")


def start_watching(reports_dir="hexaco_bot/user_reports", profiles_dir="hexaco_bot/user_profile"):
    """
    Запускает наблюдение за директорией с отчетами пользователей (блокирующий вызов).
    """
    # Конфигурируем логирование, если скрипт запускается напрямую
    if __name__ == "__main__":
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    event_handler = ReportHandler(Path(reports_dir).resolve(), Path(profiles_dir).resolve())
    observer = Observer()
    
    abs_reports_dir = Path(reports_dir).resolve()
    if not abs_reports_dir.exists():
        abs_reports_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Создана директория для отчетов: {abs_reports_dir}")
    
    observer.schedule(event_handler, str(abs_reports_dir), recursive=False)
    observer.start()
    
    logger.info(f"Наблюдатель запущен. Отслеживаем директорию: {abs_reports_dir}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Наблюдение остановлено пользователем.")
    except Exception as e:
        logger.error(f"Ошибка в работе наблюдателя: {e}")
        observer.stop()
    observer.join()

def start_watching_background(reports_dir="hexaco_bot/user_reports", profiles_dir="hexaco_bot/user_profile"):
    """
    Запускает наблюдение в фоновом режиме.
    """
    abs_reports_dir = Path(reports_dir).resolve()
    abs_profiles_dir = Path(profiles_dir).resolve()

    event_handler = ReportHandler(abs_reports_dir, abs_profiles_dir)
    observer = Observer()

    if not abs_reports_dir.exists():
        abs_reports_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Создана директория для отчетов: {abs_reports_dir}")

    observer.schedule(event_handler, str(abs_reports_dir), recursive=False)
    observer.start()
    logger.info(f"Наблюдатель запущен в фоновом режиме. Отслеживаем: {abs_reports_dir}")
    return observer

if __name__ == "__main__":
    start_watching() 