"""
Contains the RFQScorer class for calculating RFQ test scores.
"""
import json

class RFQScorer:
    """Calculates scores for the RFQ (Regulatory Focus Questionnaire) test."""

    REVERSE_ITEMS = [2, 4, 6, 8, 9, 11]

    PROMOTION_ITEMS = {
        1: False,  # Прямой
        3: False,  # Прямой
        7: False,  # Прямой
        9: True,   # Реверсивный
        10: False, # Прямой
        11: True   # Реверсивный
    }

    PREVENTION_ITEMS = {
        2: True,   # Реверсивный
        4: True,   # Реверсивный
        5: False,  # Прямой
        6: True,   # Реверсивный
        8: True    # Реверсивный
    }

    def __init__(self):
        pass

    def _reverse_score(self, score: int) -> int:
        """Reverses a score on a 1-5 scale (new = 6 - old)."""
        return 6 - score

    def calculate_scores(self, responses: dict) -> dict:
        """
        Calculates RFQ scores based on user responses.

        Args:
            responses: A dictionary where keys are question numbers (1-11)
                       and values are the integer scores (1-5).

        Returns:
            A dictionary containing:
                - 'promotion_score': Score for the Promotion Focus scale.
                - 'prevention_score': Score for the Prevention Focus scale.
                - 'error': Error message if calculation fails (e.g., not enough answers).
        """
        if len(responses) != 11: # RFQ requires all 11 answers
            return {
                "error": f"Для расчета результатов теста RFQ необходимо ответить на все 11 вопросов. Вы ответили на {len(responses)}.",
                "promotion_score": None,
                "prevention_score": None
            }

        processed_responses = {}
        for q_id, score in responses.items():
            processed_responses[q_id] = int(score) # Ensure score is int

        promotion_score = 0
        for item_id, is_reverse in self.PROMOTION_ITEMS.items():
            score = processed_responses.get(item_id)
            if score is None:
                # This should not happen if we check len(responses) == 11
                return {"error": f"Отсутствует ответ на вопрос {item_id} для шкалы Продвижения."}
            promotion_score += self._reverse_score(score) if is_reverse else score
        
        prevention_score = 0
        for item_id, is_reverse in self.PREVENTION_ITEMS.items():
            score = processed_responses.get(item_id)
            if score is None:
                # This should not happen if we check len(responses) == 11
                return {"error": f"Отсутствует ответ на вопрос {item_id} для шкалы Профилактики."}
            prevention_score += self._reverse_score(score) if is_reverse else score

        return {
            "promotion_score": promotion_score,
            "prevention_score": prevention_score
        }

    def responses_to_json(self, responses: dict) -> str:
        """Converts responses dictionary to a JSON string."""
        return json.dumps(responses) 