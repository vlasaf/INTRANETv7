"""
Contains the PID5BFMScorer class for calculating PID-5-BF+M test scores.
"""
import json
from typing import Dict, Any

class PID5BFMScorer:
    """Calculates scores for the PID-5-BF+M test."""

    def __init__(self):
        # Матрица вопрос → фасет → домен
        self.domain_structure = {
            "Негативный_аффект": {
                "Эмоц_лабильность": [1, 19],
                "Тревожность": [7, 25], 
                "Страх_разделения": [13, 31]
            },
            "Отчуждение": {
                "Отстранение": [4, 22],
                "Anhedonia": [10, 28],
                "Избегание_близости": [16, 34]
            },
            "Антагонизм": {
                "Манипулятивность": [2, 20],
                "Лживость": [8, 26],
                "Грандиозность": [14, 32]
            },
            "Дизингибиция": {
                "Безответственность": [3, 21],
                "Импульсивность": [9, 27],
                "Отвлекаемость": [15, 33]
            },
            "Ананкастия": {
                "Перфекционизм": [6, 18],
                "Ригидность": [12, 24],
                "Одерлиность": [30, 36]
            },
            "Психотицизм": {
                "Необычные_убеждения": [5, 23],
                "Эксцентричность": [11, 29],
                "Перцепт_дисрегуляция": [17, 35]
            }
        }

    def calculate_scores(self, responses: Dict[int, int]) -> Dict[str, Any]:
        """
        Calculates PID-5-BF+M scores with domain calculations.
        """
        # Перекодировка ответов: 1-4 → 0-3
        recoded_responses = {q: response - 1 for q, response in responses.items()}
        
        # Расчет доменов
        domain_scores = {}
        
        for domain_name, facets in self.domain_structure.items():
            facet_means = []
            
            for facet_name, questions in facets.items():
                # Сумма баллов по двум вопросам фасета
                facet_sum = sum(recoded_responses.get(q, 0) for q in questions)
                # Среднее для фасета (0-3)
                facet_mean = facet_sum / 2
                facet_means.append(facet_mean)
            
            # Домен = среднее трех фасетов
            domain_mean = sum(facet_means) / len(facet_means)
            domain_scores[domain_name] = round(domain_mean, 1)
        
        total_score = sum(responses.values())
        
        result = {
            "scores": {
                "total_score": total_score,
                "answered_questions": len(responses),
                **domain_scores
            },
            "raw_responses": responses
        }
        
        return result

    def format_results_message(self, scores_data: Dict[str, Any], user_name: str) -> str:
        """Formats the results into a user-friendly message."""
        scores = scores_data.get("scores", {})
        total_score = scores.get("total_score", "N/A")
        
        message = f"👤 **Результаты теста PID-5-BF+M для {user_name}**\n\n"
        message += "🎯 **Доменные шкалы (0-3):**\n"
        
        # Добавляем интерпретацию для каждого домена
        domains = [
            "Негативный_аффект", "Отчуждение", "Антагонизм", 
            "Дизингибиция", "Ананкастия", "Психотицизм"
        ]
        
        for domain in domains:
            score = scores.get(domain, 0)
            interpretation = self._get_interpretation(score)
            message += f"• {domain.replace('_', ' ')}: {score} {interpretation}\n"
        
        message += f"\n📊 Суммарный балл: {total_score}\n"
        message += f"📝 Отвечено вопросов: {scores.get('answered_questions', 0)}/36\n\n"
        
        message += "📋 **Интерпретация уровней:**\n"
        message += "• 0-0.4: фоновый уровень\n"
        message += "• 0.5-1.4: легкая выраженность\n"
        message += "• 1.5-2.4: клинически значимо\n"
        message += "• 2.5-3.0: высокая выраженность\n"
        
        return message

    def _get_interpretation(self, score: float) -> str:
        """Возвращает интерпретацию уровня по баллу."""
        if score < 0.5:
            return "🟢"
        elif score < 1.5:
            return "🟡"
        elif score < 2.5:
            return "🟠"
        else:
            return "🔴"

    def responses_to_json(self, responses: Dict[int, int]) -> str:
        """Converts responses dictionary to a JSON string."""
        return json.dumps(responses) 