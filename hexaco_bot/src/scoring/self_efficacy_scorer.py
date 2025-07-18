"""
Handles scoring for the Self-Efficacy Test.
"""
import json
from typing import Dict, Any

class SelfEfficacyScorer:
    """Calculates and interprets Self-Efficacy Test scores."""

    # Items to be reversed (sign changed)
    REVERSE_CODED_ITEMS = [2, 4, 5, 6, 7, 10, 11, 12, 16, 17, 18, 20, 22]
    # Q14: "Я испытываю уверенность в своих силах при решении сложных проблем." - positive, no reverse needed.

    # Items for General Self-Efficacy (GSE)
    GSE_ITEMS = list(range(1, 18))  # 1-17
    # Items for Social Self-Efficacy (SSE)
    SSE_ITEMS = list(range(18, 24)) # 18-23

    def calculate_scores(self, responses: Dict[int, int]) -> Dict[str, Any]:
        """
        Calculates Self-Efficacy scores.
        Args:
            responses: A dictionary of question numbers (1-23) to scores (-5 to +5).
        Returns:
            A dictionary containing scores for GSE and SSE scales.
        """
        if not responses or len(responses) != 23:
            return {"error": "Неполные ответы. Необходимо ответить на все 23 вопроса Теста самоэффективности."}

        processed_responses = {}
        for item_num, score in responses.items():
            if item_num in self.REVERSE_CODED_ITEMS:
                processed_responses[item_num] = -score
            else:
                processed_responses[item_num] = score
        
        gse_score = 0
        for item_num in self.GSE_ITEMS:
            gse_score += processed_responses.get(item_num, 0)
        
        sse_score = 0
        for item_num in self.SSE_ITEMS:
            sse_score += processed_responses.get(item_num, 0)

        # GSE range: 17 items * (-5 to +5) = -85 to +85
        # SSE range: 6 items * (-5 to +5) = -30 to +30
        return {
            "scores": {
                "Общая самоэффективность (ОСЭ)": gse_score,
                "Социальная самоэффективность (ССЭ)": sse_score
            },
            "interpretation_notes": {
                "GSE_range": "-85 до +85",
                "SSE_range": "-30 до +30"
            }
        }

    def format_self_efficacy_results_message(self, scores_data: Dict[str, Any], user_name: str) -> str:
        """
        Formats the Self-Efficacy Test results into a user-friendly message.
        """
        if "error" in scores_data:
            return f"Ошибка при расчете результатов Теста самоэффективности: {scores_data['error']}"

        # Экранируем специальные символы Markdown в user_name
        escaped_user_name = user_name
        for char_to_escape in ['_', '*', '`', '[', ']']:
            escaped_user_name = escaped_user_name.replace(char_to_escape, f'\\{char_to_escape}')

        scores = scores_data.get("scores", {})
        notes = scores_data.get("interpretation_notes", {})
        gse_score = scores.get("Общая самоэффективность (ОСЭ)", 0)
        sse_score = scores.get("Социальная самоэффективность (ССЭ)", 0)

        message = f"👤 **Результаты Теста самоэффективности для {escaped_user_name}**\n\n"
        message += "Этот тест оценивает вашу веру в собственные способности справляться с различными жизненными задачами и ситуациями.\n\n"
        
        message += f"• **Общая самоэффективность (ОСЭ):** {gse_score} баллов (Диапазон: {notes.get('GSE_range', 'N/A')})\n"
        message += f"• **Социальная самоэффективность (ССЭ):** {sse_score} баллов (Диапазон: {notes.get('SSE_range', 'N/A')})\n\n"
        
        message += "**Интерпретация:**\n"
        message += "- **Общая самоэффективность (ОСЭ)** отражает вашу уверенность в способности достигать целей и преодолевать трудности в широком спектре ситуаций.\n"
        message += "- **Социальная самоэффективность (ССЭ)** показывает вашу уверенность в способности устанавливать и поддерживать социальные контакты, а также эффективно взаимодействовать с другими людьми.\n"
        message += "- **Высокие значения** по обеим шкалам указывают на сильную веру в свои силы как в общих делах, так и в общении.\n"
        message += "- **Низкие значения** могут свидетельствовать о склонности к избеганию сложностей, неуверенности в себе и трудностях в социальных взаимодействиях.\n"
        message += "- **Средние значения** соответствуют типичному уровню самооценки для большинства людей.\n"

        return message

    def responses_to_json(self, responses: Dict[int, int]) -> str:
        """Converts responses dictionary to a JSON string."""
        return json.dumps(responses)

if __name__ == '__main__':
    scorer = SelfEfficacyScorer()
    # Mock responses (23 answers, -5 to +5)
    mock_responses = {
        1: 4, 2: -3, 3: 5, 4: -2, 5: -4, 6: -3, 7: -5, 8: 4, 9: 5, 10: -2,
        11: -3, 12: -4, 13: 5, 14: 4, 15: 4, 16: -3, 17: -2,
        18: -1, 19: 3, 20: -2, 21: 2, 22: -3, 23: 3 
    }
    
    calculated_scores = scorer.calculate_scores(mock_responses)
    print("\nCalculated Scores Data (Self-Efficacy):")
    print(json.dumps(calculated_scores, indent=2, ensure_ascii=False))

    if "error" not in calculated_scores:
        results_message = scorer.format_self_efficacy_results_message(calculated_scores, "Тестовый Пользователь")
        print("\nFormatted Self-Efficacy Results Message:")
        print(results_message)
    else:
        print(f"Error: {calculated_scores['error']}") 