"""
Логика подсчета результатов для теста самодетерминации (SDS-12).
"""
from typing import Dict, Tuple

class SDSScorer:
    def __init__(self):
        # Определяем, какой ответ является "автономным" для каждого вопроса
        self.autonomous_choices = {
            1: "A", 2: "B", 3: "A", 4: "B", 5: "A", 6: "A",
            7: "B", 8: "A", 9: "B", 10: "B", 11: "A", 12: "B"
        }

    def _get_score_for_item(self, item_id: int, response_value: int) -> int:
        """Кодирует балл для одного пункта (от -2 до +2)."""
        # response_value: 1 (Только А) ... 5 (Только Б)
        # autonomous_choice: "A" или "B"
        
        is_autonomous_A = self.autonomous_choices[item_id] == "A"
        
        if is_autonomous_A:
            # Автономный выбор - А. Ответы 1, 2 - к А; 4, 5 - к Б.
            if response_value == 1: return 2  # Только А (автономный)
            if response_value == 2: return 1  # Скорее А (автономный)
            if response_value == 3: return 0  # Оба
            if response_value == 4: return -1 # Скорее Б (контролируемый)
            if response_value == 5: return -2 # Только Б (контролируемый)
        else:
            # Автономный выбор - Б. Ответы 4, 5 - к Б; 1, 2 - к А.
            if response_value == 1: return -2 # Только А (контролируемый)
            if response_value == 2: return -1 # Скорее А (контролируемый)
            if response_value == 3: return 0  # Оба
            if response_value == 4: return 1  # Скорее Б (автономный)
            if response_value == 5: return 2  # Только Б (автономный)
        return 0 # На случай непредвиденного значения

    def calculate_scores(self, responses: Dict[int, int]) -> Dict[str, float]:
        """Подсчитывает подшкалы и общий индекс SDS."""
        item_scores = {}
        for item_id, response_value in responses.items():
            if item_id in self.autonomous_choices:
                item_scores[item_id] = self._get_score_for_item(item_id, response_value)
        
        self_contact_items = [1, 2, 3, 4, 5]
        choiceful_action_items = [6, 7, 8, 9, 10, 11, 12]
        
        self_contact_score = 0
        sc_count = 0
        for item in self_contact_items:
            if item in item_scores:
                self_contact_score += item_scores[item]
                sc_count += 1
        
        choiceful_action_score = 0
        ca_count = 0
        for item in choiceful_action_items:
            if item in item_scores:
                choiceful_action_score += item_scores[item]
                ca_count += 1
                
        avg_self_contact = (self_contact_score / sc_count) if sc_count > 0 else 0
        avg_choiceful_action = (choiceful_action_score / ca_count) if ca_count > 0 else 0
        
        sds_index = (avg_self_contact + avg_choiceful_action) / 2
        
        return {
            "self_contact": round(avg_self_contact, 2),
            "choiceful_action": round(avg_choiceful_action, 2),
            "sds_index": round(sds_index, 2)
        }

    def interpret_sds_index(self, sds_index: float) -> str:
        """Интерпретирует общий индекс SDS."""
        if sds_index <= -0.5:
            return "Низкая самодетерминация (внешний контроль)"
        elif -0.4 <= sds_index <= 0.4:
            return "Смешанная мотивация"
        else: # >= 0.5
            return "Высокая самодетерминация (действую в согласии с собой)"

    def interpret_subscales(self, self_contact: float, choiceful_action: float) -> Tuple[str, str]:
        """Интерпретирует подшкалы."""
        sc_interpretation = "Нормальный Self-Contact (контакт с собой)"
        if self_contact < -0.4: # Условный порог, можно настроить
            sc_interpretation = "Низкий Self-Contact (человек «не слышит себя»)"
        elif self_contact > 0.4:
            sc_interpretation = "Высокий Self-Contact (хороший контакт с собой)"
            
        ca_interpretation = "Нормальное Choiceful Action (действие по-своему)"
        if choiceful_action < -0.4:
            ca_interpretation = "Низкое Choiceful Action («слышу, но не делаю»)"
        elif choiceful_action > 0.4:
            ca_interpretation = "Высокое Choiceful Action (активно действую по-своему)"
            
        return sc_interpretation, ca_interpretation

    def format_sds_results_message(self, scores: Dict[str, float], user_name: str) -> str:
        """Форматирует сообщение с результатами SDS."""
        sds_index_interpretation = self.interpret_sds_index(scores['sds_index'])
        sc_interp, ca_interp = self.interpret_subscales(scores['self_contact'], scores['choiceful_action'])
        
        message = f"📊 **Результаты Теста Самодетерминации (SDS) для {user_name}**\n\n"
        message += f"🔹 **Общий Индекс Самодетерминации (SDS Index): {scores['sds_index']:.2f}**\n"
        message += f"   *Интерпретация:* {sds_index_interpretation}\n\n"
        message += f"🔸 **Подшкала 'Контакт с собой' (Self-Contact): {scores['self_contact']:.2f}**\n"
        message += f"   *Интерпретация:* {sc_interp}\n\n"
        message += f"🔸 **Подшкала 'Осмысленное действие' (Choiceful Action): {scores['choiceful_action']:.2f}**\n"
        message += f"   *Интерпретация:* {ca_interp}\n\n"
        message += "💡 *Этот тест помогает понять, насколько ваши действия исходят из ваших собственных убеждений и ценностей, а не из внешнего давления.*"
        return message
    
    def responses_to_json(self, responses: Dict[int, int]) -> str:
        import json
        return json.dumps(responses) 