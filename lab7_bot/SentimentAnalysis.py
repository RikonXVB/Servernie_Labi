from transformers import pipeline
import re
from datetime import datetime, timedelta

class MessageAnalyzer:
    def __init__(self):
        # Загружаем модель для анализа эмоций
        self.sentiment_analyzer = pipeline(
            "text-classification",
            model="cointegrated/rubert-tiny2-cedr-emotion-detection",
            tokenizer="cointegrated/rubert-tiny2-cedr-emotion-detection"
        )
        self.setup_patterns()

    def setup_patterns(self):
        self.question_pattern = r'\?|зачем|почему|как|что|где|когда|кто'
        self.response_pattern = r'^@|ответ|согласен|не согласен|думаю'

    def analyze_message(self, text, user_history=None):
        # Получаем эмоциональную окраску текста
        emotion = self.sentiment_analyzer(text)[0]
        
        # Маппинг эмоций на позитивность/токсичность
        emotion_mapping = {
            'joy': {'positivity': 1.0, 'toxicity': 0.0},
            'sadness': {'positivity': 0.0, 'toxicity': 0.3},
            'anger': {'positivity': 0.0, 'toxicity': 0.9},
            'surprise': {'positivity': 0.7, 'toxicity': 0.0},
            'fear': {'positivity': 0.0, 'toxicity': 0.5},
            'neutral': {'positivity': 0.3, 'toxicity': 0.0}
        }

        emotion_scores = emotion_mapping.get(emotion['label'], {'positivity': 0.0, 'toxicity': 0.0})
        
        result = {
            'toxicity': emotion_scores['toxicity'],
            'positivity': emotion_scores['positivity'],
            'is_question': bool(re.search(self.question_pattern, text.lower())),
            'is_response': bool(re.search(self.response_pattern, text.lower())),
            'is_flood': self.check_flood(user_history) if user_history else False
        }
        return result

    def analyze_user_characteristics(self, user_stats, message_history):
        total_messages = user_stats['total_messages']
        if total_messages == 0:
            return {}

        # Базовые метрики
        characteristics = {
            'activity_score': self.calculate_activity_score(user_stats, message_history),
            'positivity_ratio': user_stats['positive_messages'] / total_messages,
            'flood_score': user_stats['flood_warnings'] / total_messages,
            'rule_violations_ratio': user_stats['rule_violations'] / total_messages,
            'toxicity_level': user_stats['toxicity_sum'] / total_messages,
            'curiosity_score': user_stats['questions_asked'] / total_messages,
            'responsiveness_score': user_stats['responses_to_others'] / total_messages
        }

        # Определение характеристик пользователя
        characteristics['user_type'] = self.determine_user_type(characteristics)
        
        return characteristics

    def calculate_activity_score(self, user_stats, message_history):
        # Учитываем различные факторы активности
        messages_per_day = len(message_history) / max(1, (datetime.now() - user_stats['created_at']).days)
        
        # Считаем отзывчивость как процент ответов от общего числа сообщений
        responsiveness = user_stats['responses_to_others'] / max(1, user_stats['total_messages'])
        
        # Общая активность складывается из частоты сообщений и отзывчивости
        return (messages_per_day * 0.6 + responsiveness * 0.4)

    def determine_user_type(self, characteristics):
        user_types = []
        
        if characteristics['activity_score'] > 0.7:
            user_types.append('Активный участник')
        if characteristics['positivity_ratio'] > 0.6:
            user_types.append('Позитивный')
        # Повышаем порог для определения отзывчивости
        if characteristics['responsiveness_score'] > 0.3:  # Если больше 30% сообщений - ответы
            user_types.append('Отзывчивый')
        if characteristics['toxicity_level'] > 0.4:
            user_types.append('Токсичный')
        if characteristics['curiosity_score'] > 0.3:
            user_types.append('Любознательный')
            
        return user_types if user_types else ['Нейтральный пользователь']

    def check_flood(self, user_history, threshold=5, time_window=60):
        """Проверка на флуд: более threshold сообщений за time_window секунд"""
        if not user_history:
            return False
            
        recent_messages = [msg for msg in user_history 
                         if (datetime.now() - msg['created_at']).seconds <= time_window]
        return len(recent_messages) > threshold
