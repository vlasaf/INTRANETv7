"""
Contains the CDRISCScorer class for calculating CD-RISC test scores.
"""
import json

class CDRISCScorer:
    """Calculates scores for the CD-RISC test."""

    SUBSCALES_ITEMS = {
        "personal_competence_persistence": [10, 11, 12, 16, 17, 23, 24, 25],
        "instincts_stress_as_hardening": [6, 7, 14, 15, 18, 19, 20],
        "acceptance_of_change_support": [1, 2, 4, 5, 8, 13],
        "control": [21, 22],
        "spiritual_beliefs": [3, 9]
    }

    MIN_ANSWERS_REQUIRED = 19

    def __init__(self):
        pass

    def calculate_scores(self, responses: dict) -> dict:
        """
        Calculates CD-RISC scores based on user responses.

        Args:
            responses: A dictionary where keys are question numbers (1-25)
                       and values are the integer scores (1-5).

        Returns:
            A dictionary containing:
                - 'total_score': Sum of all responses.
                - 'classic_score': Total score - 25.
                - 'interpretation_category': Resilience category.
                - 'subscale_scores': Dictionary of scores for each subscale.
                - 'answered_questions_count': Number of answered questions.
                - 'error': Error message if calculation fails (e.g., not enough answers).
        """
        answered_questions_count = len(responses)
        if answered_questions_count < self.MIN_ANSWERS_REQUIRED:
            return {
                "error": f"Протокол недействителен. Необходимо ответить минимум на {self.MIN_ANSWERS_REQUIRED} вопросов. Вы ответили на {answered_questions_count}.",
                "answered_questions_count": answered_questions_count
            }

        total_score = sum(responses.values())
        classic_score = total_score - 25

        interpretation_category = ""
        if classic_score >= 80:
            interpretation_category = "Высокая устойчивость"
        elif 60 <= classic_score <= 79:
            interpretation_category = "Средняя устойчивость"
        else: # < 60
            interpretation_category = "Низкая устойчивость"

        subscale_scores = {}
        for scale_name, item_ids in self.SUBSCALES_ITEMS.items():
            scale_sum = 0
            answered_in_scale = 0
            for item_id in item_ids:
                if item_id in responses:
                    scale_sum += responses[item_id]
                    answered_in_scale +=1
            # Store sum for subscales as per typical CD-RISC reporting, not averages unless specified
            subscale_scores[scale_name] = scale_sum 

        return {
            "total_score": total_score,
            "classic_score": classic_score,
            "interpretation_category": interpretation_category,
            "subscale_scores": subscale_scores,
            "answered_questions_count": answered_questions_count
        }

    def responses_to_json(self, responses: dict) -> str:
        """Converts responses dictionary to a JSON string."""
        return json.dumps(responses) 