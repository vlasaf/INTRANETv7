"""
Defines questions and answer options for the PANAS (Positive and Negative Affect Schedule).
"""

PANAS_QUESTIONS = [
    {"id": 1, "text": "Заинтересованность"},
    {"id": 2, "text": "Чувство вины"},
    {"id": 3, "text": "Раздражительность"},
    {"id": 4, "text": "Решительный"},
    {"id": 5, "text": "Чувство силы"}, # Оригинал: "Чувство **силы", убираю markdown для простоты
    {"id": 6, "text": "Страдающий"},
    {"id": 7, "text": "Испуганный"},
    {"id": 8, "text": "Настороженный"},
    {"id": 9, "text": "Внимательный"},
    {"id": 10, "text": "Гордый"},
    {"id": 11, "text": "Возбуждённый (радостно)"},
    {"id": 12, "text": "Враждебный"},
    {"id": 13, "text": "Стыдящийся"},
    {"id": 14, "text": "Взволнованный"},
    {"id": 15, "text": "Нервный"},
    {"id": 16, "text": "Грустный"},
    {"id": 17, "text": "Энтузиастичный"},
    {"id": 18, "text": "Вдохновлённый"},
    {"id": 19, "text": "Активный"},
    {"id": 20, "text": "Напуганный"}
]

PANAS_ANSWER_OPTIONS = {
    1: "1 (Почти или совсем нет)",
    2: "2 (Немного)",
    3: "3 (Умеренно)",
    4: "4 (Значительно)",
    5: "5 (Очень сильно)"
}

def get_total_panas_questions() -> int:
    return len(PANAS_QUESTIONS)

def get_panas_question_text(question_number: int) -> str:
    if 1 <= question_number <= len(PANAS_QUESTIONS):
        return PANAS_QUESTIONS[question_number - 1]["text"]
    raise ValueError(f"Invalid PANAS question number: {question_number}")

if __name__ == '__main__':
    print(f"Total PANAS questions: {get_total_panas_questions()}")
    for i in range(1, get_total_panas_questions() + 1):
        print(f"Q{i}: {get_panas_question_text(i)}")
    print(f"Answer options: {PANAS_ANSWER_OPTIONS}") 