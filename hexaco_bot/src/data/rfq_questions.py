"""
Contains questions, answer options, and helper functions for the RFQ test.
"""

RFQ_QUESTIONS = [
    {"id": 1, "text": "Обычно я добиваюсь того, чего хочу."},
    {"id": 2, "text": "Переходили ли вы в детстве границы дозволенного, делая то, что ваши родители вам запрещали?"},
    {"id": 3, "text": "Как часто завершение какого-либо дела вдохновляло вас на дальнейшее продолжение работы в этом направлении?"},
    {"id": 4, "text": "Как часто вы «играли на родительских нервах», когда были ребенком?"},
    {"id": 5, "text": "Слушались ли вы ваших родителей?"},
    {"id": 6, "text": "Как часто в детстве вы совершали поступки, которые ваши родители явно не одобряли?"},
    {"id": 7, "text": "Как часто вы преуспеваете в ваших начинаниях?"},
    {"id": 8, "text": "Я бываю неосторожен."},
    {"id": 9, "text": "Как часто при решении важной для вас задачи вам кажется, что вы справляетесь хуже, чем хотели бы?"},
    {"id": 10, "text": "Я чувствую, что двигаюсь к достижению успеха в своей жизни."},
    {"id": 11, "text": "В моей жизни мало хобби и увлечений, отвечающих моим интересам, заниматься которыми мне действительно хочется."}
]

RFQ_ANSWER_OPTIONS = {
    1: "Совершенно не согласен",
    2: "Не согласен",
    3: "Нечто среднее",
    4: "Согласен",
    5: "Совершенно согласен"
}

# Реверсивные вопросы: 2, 4, 6, 8, 9, 11
RFQ_REVERSE_ITEMS = [2, 4, 6, 8, 9, 11]

def get_rfq_question_data(question_number: int) -> dict:
    """
    Retrieves a specific RFQ question by its number.
    Args:
        question_number: The 1-based index of the question.
    Returns:
        A dictionary containing the question id and text.
    Raises:
        ValueError: If the question_number is out of bounds.
    """
    if 1 <= question_number <= len(RFQ_QUESTIONS):
        question = RFQ_QUESTIONS[question_number - 1]
        # Можно добавить флаг is_reverse, если это будет использоваться в _show_question
        # question['is_reverse'] = question_number in RFQ_REVERSE_ITEMS 
        return question
    raise ValueError(f"Question number {question_number} is out of range for RFQ test.")

def get_total_rfq_questions() -> int:
    """
    Returns the total number of RFQ questions.
    """
    return len(RFQ_QUESTIONS)

def get_rfq_answer_options() -> dict:
    """
    Returns the answer options for RFQ questions.
    """
    return RFQ_ANSWER_OPTIONS 