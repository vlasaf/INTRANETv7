"""
Contains questions, answer options, and helper functions for the CD-RISC test.
"""

CDRISC_QUESTIONS = [
    {"id": 1, "text": "Я способен адаптироваться к происходящим изменениям."},
    {"id": 2, "text": "У меня близкие и надежные отношения с другими."},
    {"id": 3, "text": "Иногда мне помогает судьба или Бог."},
    {"id": 4, "text": "Я могу справиться со всем, что мне встречается на пути."},
    {"id": 5, "text": "Прошлые успехи придают мне уверенность."},
    {"id": 6, "text": "Я пытаюсь увидеть смешную сторону вещей, когда сталкиваюсь с проблемами."},
    {"id": 7, "text": "То, что я справляюсь со стрессом, может сделать меня сильнее."},
    {"id": 8, "text": "Я обычно восстанавливаюсь после болезней, ран или других лишений."},
    {"id": 9, "text": "Я считаю, что большинство событий происходит не без причины."},
    {"id": 10, "text": "Я стараюсь приложить все усилия, вне зависимости от ситуации."},
    {"id": 11, "text": "Я верю, что могу достичь своих целей, несмотря на препятствия."},
    {"id": 12, "text": "Я не сдаюсь даже в безнадежных ситуациях."},
    {"id": 13, "text": "Во времена стресса я знаю, где найти помощь."},
    {"id": 14, "text": "Под давлением я сохраняю концентрацию и четкость мыслей."},
    {"id": 15, "text": "Я предпочитаю руководить при решении проблем."},
    {"id": 16, "text": "Меня не просто лишить воли неудачами."},
    {"id": 17, "text": "Я рассматриваю себя, как сильную личность, способную справиться с вызовами и сложностями жизни."},
    {"id": 18, "text": "Я принимаю непопулярные или сложные решения."},
    {"id": 19, "text": "Я могу справиться с такими неприятными или болезненными ощущениями, как печаль, страх и гнев."},
    {"id": 20, "text": "Я должен действовать интуитивно."},
    {"id": 21, "text": "У меня сильное чувство цели в жизни."},
    {"id": 22, "text": "Я чувствую, что контролирую ситуацию."},
    {"id": 23, "text": "Мне нравятся вызовы."},
    {"id": 24, "text": "Я работаю для достижения целей."},
    {"id": 25, "text": "Я горжусь своими достижениями."}
]

CDRISC_ANSWER_OPTIONS = {
    1: "1 – Никогда",
    2: "2 – Изредка",
    3: "3 – Иногда",
    4: "4 – Часто",
    5: "5 – Почти всегда"
}

def get_cdrisc_question_data(question_number: int) -> dict:
    """
    Retrieves a specific CD-RISC question by its number.
    Args:
        question_number: The 1-based index of the question.
    Returns:
        A dictionary containing the question id and text.
    Raises:
        ValueError: If the question_number is out of bounds.
    """
    if 1 <= question_number <= len(CDRISC_QUESTIONS):
        return CDRISC_QUESTIONS[question_number - 1]
    raise ValueError(f"Question number {question_number} is out of range for CD-RISC test.")

def get_total_cdrisc_questions() -> int:
    """
    Returns the total number of CD-RISC questions.
    """
    return len(CDRISC_QUESTIONS)

def get_cdrisc_answer_options() -> dict:
    """
    Returns the answer options for CD-RISC questions.
    """
    return CDRISC_ANSWER_OPTIONS 