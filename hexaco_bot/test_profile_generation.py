import json
import os
from src.psychoprofile.profiler import generate_and_save_psychoprofile

def test_direct_generation():
    """
    Напрямую тестирует функцию генерации психопрофиля с тестовыми данными.
    """
    # Тестовый ID пользователя
    user_id = "test_user_123"
    
    # Пример данных тестов
    test_data = {
        "PAEI": {"P_score": 30, "A_score": 25, "E_score": 35, "I_score": 20},
        "MBTI-16": {"type_code": "ISTP", "assertiveness_trait": "T"},
        "HEXACO": {"H": 4.5, "E": 3.8, "X": 4.1, "A": 3.5, "C": 4.2, "O": 4.0},
        "SVS": {"values": {"Power": 3.2, "Achievement": 5.1, "Hedonism": 4.3,
                         "Stimulation": 4.8, "Self_Direction": 5.5, "Universalism": 4.2,
                         "Benevolence": 5.0, "Tradition": 3.1, "Conformity": 2.8, "Security": 4.5}},
        "URICA": {"scores": {"precontemplation": 2.1, "contemplation": 3.8, "action": 3.2, "maintenance": 2.5}},
        "Dweck Mindset": {"scores": {"intelligence_growth": 4.2, "personality_growth": 3.8,
                                   "learning_goal_acceptance": 4.5, "learning_self_assessment": 3.9}},
        "PANAS": {"positive": 38, "negative": 12},
        "Self-Efficacy": {"general": 28, "social": 24},
        "CD-RISC": {"total": 75, "persistence": 15, "stress_hardening": 18, 
                   "acceptance_of_change": 14, "control": 16, "spiritual_beliefs": 12},
        "RFQ": {"promotion": 30, "prevention": 22}
    }
    
    # Директория для тестовых профилей
    test_profiles_dir = "hexaco_bot/test_profiles"
    os.makedirs(test_profiles_dir, exist_ok=True)
    
    # Генерация профиля
    profile_path = generate_and_save_psychoprofile(
        user_id, 
        test_data, 
        profile_dir=test_profiles_dir
    )
    
    print(f"Тестовый профиль создан: {profile_path}")
    
    # Чтение и вывод созданного профиля
    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile = json.load(f)
            print("\nСодержимое психопрофиля:")
            print(json.dumps(profile, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Ошибка при чтении профиля: {e}")

def test_file_based_generation():
    """
    Тестирует генерацию психопрофиля путем создания тестового файла в user_reports.
    Это имитирует реальный сценарий, где данные поступают из файлов отчетов.
    """
    # Папки для тестов
    reports_dir = "hexaco_bot/user_reports"
    profiles_dir = "hexaco_bot/user_profile"
    
    # Создаем директории, если не существуют
    os.makedirs(reports_dir, exist_ok=True)
    os.makedirs(profiles_dir, exist_ok=True)
    
    user_id = "test_user_456"
    report_file = os.path.join(reports_dir, f"{user_id}.json")
    
    # Тестовые данные
    test_data = {
        "PAEI": {"P_score": 35, "A_score": 40, "E_score": 25, "I_score": 30},
        "MBTI-16": {"type_code": "ENFP", "assertiveness_trait": "A"},
        "HEXACO": {"H": 3.9, "E": 4.2, "X": 4.7, "A": 3.8, "C": 3.5, "O": 4.8},
        # Добавьте больше тестов по необходимости
    }
    
    # Создаем тестовый файл отчета
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    print(f"Создан тестовый файл отчета: {report_file}")
    print("Теперь запустите скрипт report_watcher.py, чтобы обнаружить этот файл и сгенерировать профиль.")
    print("Команда для запуска наблюдателя: python hexaco_bot/report_watcher.py")


if __name__ == "__main__":
    print("=== Тестирование прямой генерации психопрофиля ===")
    test_direct_generation()
    
    print("\n=== Тестирование генерации психопрофиля из файлов отчетов ===")
    test_file_based_generation()
    
    print("\nЧтобы запустить наблюдатель файловой системы, используйте команду:")
    print("python hexaco_bot/report_watcher.py") 