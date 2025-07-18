"""
Handles scoring for the PANAS (Positive and Negative Affect Schedule).
"""
import json
from typing import Dict, Any

class PanasScorer:
    """Calculates and interprets PANAS scores."""

    # Item numbers for Positive Affect (PA) and Negative Affect (NA) scales
    # Q14 ("Взволнованный") is currently excluded from PA as per initial logic.
    # It can be added if specified: self.PA_ITEMS = [1, 4, 5, 9, 10, 11, 14, 17, 18, 19]
    PA_ITEMS = [1, 4, 5, 9, 10, 11, 17, 18, 19]
    NA_ITEMS = [2, 3, 6, 7, 8, 12, 13, 15, 16, 20]

    def calculate_scores(self, responses: Dict[int, int]) -> Dict[str, Any]:
        """
        Calculates PANAS scores.
        Args:
            responses: A dictionary of question numbers (1-20) to scores (1-5).
        Returns:
            A dictionary containing scores for PA and NA scales.
        """
        if not responses or len(responses) != 20:
            return {"error": "Неполные ответы. Необходимо ответить на все 20 вопросов ШПАНА."}

        pa_score = 0
        for item_num in self.PA_ITEMS:
            pa_score += responses.get(item_num, 0)

        na_score = 0
        for item_num in self.NA_ITEMS:
            na_score += responses.get(item_num, 0)

        return {
            "scores": {
                "Позитивный аффект (ПА)": pa_score,
                "Негативный аффект (НА)": na_score
            },
            "interpretation_notes": {
                "PA_range": "9 - 45" if 14 not in self.PA_ITEMS else "10 - 50", # Recalculate if Q14 added
                "NA_range": "10 - 50"
            }
        }

    def format_panas_results_message(self, scores_data: Dict[str, Any], user_name: str) -> str:
        """
        Formats the PANAS results into a user-friendly message.
        """
        if "error" in scores_data:
            return f"Ошибка при расчете результатов теста ШПАНА: {scores_data['error']}"

        scores = scores_data.get("scores", {})
        notes = scores_data.get("interpretation_notes", {})
        pa_score = scores.get("Позитивный аффект (ПА)", 0)
        na_score = scores.get("Негативный аффект (НА)", 0)

        message = f"👤 **Результаты Шкалы позитивного и негативного аффекта (ШПАНА) для {user_name}**\n\n"
        message += "Этот опросник оценивает, насколько вы испытывали различные чувства и эмоции в течение последних нескольких недель.\n\n"
        
        message += f"• **Позитивный аффект (ПА):** {pa_score} баллов (Диапазон: {notes.get('PA_range', 'N/A')})\n"
        message += f"• **Негативный аффект (НА):** {na_score} баллов (Диапазон: {notes.get('NA_range', 'N/A')})\n\n"
        
        message += "**Интерпретация:**\n"
        message += "- **Высокие баллы по шкале Позитивного аффекта (ПА)** обычно связаны с ощущением энергичности, полного сосредоточения и радостного воодушевления.\n"
        message += "- **Высокие баллы по шкале Негативного аффекта (НА)** могут указывать на переживание дистресса, тревожности и неприятных состояний.\n"
        message += "- **Низкие баллы по ПА** могут отражать апатию, недостаток энергии или интереса.\n"
        message += "- **Низкие баллы по НА** обычно связаны с состоянием спокойствия и безмятежности.\n\n"
        message += "*Примечание: Шкалы ПА и НА относительно независимы. Человек может иметь высокие или низкие показатели по обеим шкалам одновременно.*"

        return message

    def responses_to_json(self, responses: Dict[int, int]) -> str:
        """Converts responses dictionary to a JSON string."""
        return json.dumps(responses)

if __name__ == '__main__':
    scorer = PanasScorer()
    # Mock responses (20 answers, 1-5)
    mock_responses = {
        1: 5, 2: 1, 3: 1, 4: 4, 5: 5, 6: 1, 7: 1, 8: 2, 9: 4, 10: 5,
        11: 4, 12: 1, 13: 1, 14: 3, 15: 2, 16: 1, 17: 5, 18: 4, 19: 5, 20: 1
    }
    
    calculated_scores = scorer.calculate_scores(mock_responses)
    print("\nCalculated Scores Data (PANAS):")
    print(json.dumps(calculated_scores, indent=2, ensure_ascii=False))

    if "error" not in calculated_scores:
        results_message = scorer.format_panas_results_message(calculated_scores, "Тестовый Пользователь")
        print("\nFormatted PANAS Results Message:")
        print(results_message)
    else:
        print(f"Error: {calculated_scores['error']}")

    # Test case with Q14 included in PA (hypothetical)
    # class PanasScorerQ14(PanasScorer):
    #     PA_ITEMS = [1, 4, 5, 9, 10, 11, 14, 17, 18, 19] # Add 14
    # scorer_q14 = PanasScorerQ14()
    # calculated_scores_q14 = scorer_q14.calculate_scores(mock_responses)
    # print("\nCalculated Scores Data (PANAS with Q14 in PA):")
    # print(json.dumps(calculated_scores_q14, indent=2, ensure_ascii=False))
    # results_message_q14 = scorer_q14.format_panas_results_message(calculated_scores_q14, "Тестовый Пользователь Q14")
    # print("\nFormatted PANAS Results Message (with Q14 in PA):")
    # print(results_message_q14) 