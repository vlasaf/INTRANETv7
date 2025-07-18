"""
HEXACO scoring algorithms and result calculations.
"""

import json
import logging
from typing import Dict, List, Tuple
from collections import defaultdict

# Используем абсолютный импорт
from hexaco_bot.src.data.hexaco_questions import HEXACO_QUESTIONS, FACTORS, get_questions_by_factor

logger = logging.getLogger(__name__)

class HEXACOScorer:
    """Calculates HEXACO personality scores from user responses."""
    
    def __init__(self):
        """Initialize scorer with factor mappings."""
        self.factor_questions = self._build_factor_mappings()
        
    def _build_factor_mappings(self) -> Dict[str, List[Tuple[int, bool]]]:
        """Build mapping of factors to their questions and reverse scoring."""
        mappings = {}
        for factor in FACTORS.keys():
            questions = get_questions_by_factor(factor)
            # Store (question_number, is_reverse_scored) tuples
            mappings[factor] = [(q_num, reverse) for q_num, _, reverse in questions]
        return mappings
    
    def calculate_scores(self, responses: Dict[int, int]) -> Dict[str, float]:
        """
        Calculate HEXACO scores from user responses.
        
        Args:
            responses: Dictionary mapping question numbers (1-100) to responses (1-5)
            
        Returns:
            Dictionary with factor scores (0.0-5.0 scale)
        """
        if len(responses) != 100:
            raise ValueError(f"Expected 100 responses, got {len(responses)}")
        
        scores = {}
        
        for factor, question_data in self.factor_questions.items():
            factor_scores = []
            
            for question_num, is_reverse in question_data:
                if question_num not in responses:
                    raise ValueError(f"Missing response for question {question_num}")
                
                raw_score = responses[question_num]
                
                # Apply reverse scoring if needed
                if is_reverse:
                    # Reverse scale: 1->5, 2->4, 3->3, 4->2, 5->1
                    adjusted_score = 6 - raw_score
                else:
                    adjusted_score = raw_score
                
                factor_scores.append(adjusted_score)
            
            # Calculate mean score for this factor
            mean_score = sum(factor_scores) / len(factor_scores)
            scores[factor] = round(mean_score, 2)
            
            logger.debug(f"Factor {factor}: {len(factor_scores)} items, mean = {mean_score:.2f}")
        
        return scores
    
    def get_score_interpretation(self, scores: Dict[str, float]) -> Dict[str, Dict[str, str]]:
        """
        Get interpretation of HEXACO scores.
        
        Returns:
            Dictionary with factor interpretations including level and description
        """
        interpretations = {}
        
        for factor, score in scores.items():
            level, description = self._interpret_score(factor, score)
            interpretations[factor] = {
                'score': score,
                'level': level,
                'description': description,
                'factor_name': FACTORS[factor]
            }
        
        return interpretations
    
    def _interpret_score(self, factor: str, score: float) -> Tuple[str, str]:
        """Interpret individual factor score."""
        
        # Define score ranges
        if score >= 4.0:
            level = "Высокий"
        elif score >= 3.0:
            level = "Средний"
        else:
            level = "Низкий"
        
        # Factor-specific descriptions
        descriptions = {
            'H': {
                'Высокий': "Вы честны, искренни, скромны и справедливы. Избегаете манипуляций и коррупции.",
                'Средний': "У вас умеренный уровень честности и смирения. Обычно поступаете справедливо.",
                'Низкий': "Вы можете быть склонны к манипуляциям, хвастовству или нечестному поведению."
            },
            'E': {
                'Высокий': "Вы эмоционально чувствительны, тревожны, нуждаетесь в эмоциональной поддержке.",
                'Средний': "У вас умеренный уровень эмоциональности. Иногда тревожитесь, но в целом стабильны.",
                'Низкий': "Вы эмоционально стабильны, спокойны, независимы и стрессоустойчивы."
            },
            'X': {
                'Высокий': "Вы общительны, активны, энергичны, оптимистичны и любите быть в центре внимания.",
                'Средний': "У вас умеренный уровень экстраверсии. Комфортно чувствуете себя в разных ситуациях.",
                'Низкий': "Вы интровертны, предпочитаете одиночество, спокойны и сдержанны."
            },
            'A': {
                'Высокий': "Вы терпеливы, миролюбивы, прощающи и готовы к сотрудничеству.",
                'Средний': "У вас умеренный уровень доброжелательности. Обычно готовы к компромиссам.",
                'Низкий': "Вы можете быть критичными, упрямыми, склонными к конфликтам."
            },
            'C': {
                'Высокий': "Вы организованы, дисциплинированы, надежны и стремитесь к совершенству.",
                'Средний': "У вас умеренный уровень добросовестности. Обычно выполняете обязательства.",
                'Низкий': "Вы можете быть неорганизованными, импульсивными, склонными к прокрастинации."
            },
            'O': {
                'Высокий': "Вы креативны, любознательны, интеллектуальны и открыты новому опыту.",
                'Средний': "У вас умеренная открытость опыту. Интересуетесь некоторыми новыми идеями.",
                'Низкий': "Вы предпочитаете традиционные подходы, практичны и консервативны."
            },
            'Alt': {
                'Высокий': "Вы альтруистичны, сочувствующи и готовы помогать другим.",
                'Средний': "У вас умеренный уровень альтруизма. Иногда помогаете другим.",
                'Низкий': "Вы больше сосредоточены на себе, менее склонны к альтруистическому поведению."
            }
        }
        
        return level, descriptions[factor][level]
    
    def format_results_message(self, scores: Dict[str, float], user_name: str) -> str:
        """Format HEXACO results as a readable message."""
        
        interpretations = self.get_score_interpretation(scores)
        
        message = f"🎯 Результаты HEXACO теста для {user_name}\n\n"
        
        # Factor order for display
        factor_order = ['H', 'E', 'X', 'A', 'C', 'O', 'Alt']
        
        for factor in factor_order:
            if factor in interpretations:
                interp = interpretations[factor]
                emoji = self._get_factor_emoji(factor)
                
                message += f"{emoji} **{interp['factor_name']}**: {interp['score']}/5.0 ({interp['level']})\n"
                message += f"   {interp['description']}\n\n"
        
        message += "📊 Интерпретация:\n"
        message += "• Высокий (4.0+): Ярко выраженная черта\n"
        message += "• Средний (3.0-3.9): Умеренная выраженность\n"
        message += "• Низкий (<3.0): Слабо выраженная черта\n\n"
        message += "💡 Помните: нет 'хороших' или 'плохих' результатов - это ваш уникальный личностный профиль!"
        
        return message
    
    def _get_factor_emoji(self, factor: str) -> str:
        """Get emoji for factor display."""
        emojis = {
            'H': '🤝',  # Honesty-Humility
            'E': '💭',  # Emotionality
            'X': '🎉',  # Extraversion
            'A': '🤗',  # Agreeableness
            'C': '📋',  # Conscientiousness
            'O': '🎨',  # Openness
            'Alt': '❤️'  # Altruism
        }
        return emojis.get(factor, '📊')
    
    def validate_responses(self, responses: Dict[int, int]) -> List[str]:
        """Validate user responses and return list of errors."""
        errors = []
        
        # Check total count
        if len(responses) != 100:
            errors.append(f"Expected 100 responses, got {len(responses)}")
        
        # Check question numbers
        for q_num in range(1, 101):
            if q_num not in responses:
                errors.append(f"Missing response for question {q_num}")
        
        # Check response values
        for q_num, response in responses.items():
            if not isinstance(response, int) or response < 1 or response > 5:
                errors.append(f"Invalid response for question {q_num}: {response} (must be 1-5)")
        
        return errors
    
    def responses_to_json(self, responses: Dict[int, int]) -> str:
        """Convert responses dictionary to JSON string."""
        return json.dumps(responses, sort_keys=True)
    
    def responses_from_json(self, json_str: str) -> Dict[int, int]:
        """Convert JSON string back to responses dictionary."""
        data = json.loads(json_str)
        # Ensure keys are integers
        return {int(k): int(v) for k, v in data.items()} 