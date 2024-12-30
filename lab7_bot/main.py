import telebot
import SentimentAnalysis as SA
from collections import defaultdict
import psycopg2
from psycopg2.extras import DictCursor
from config import API_TOKEN
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import io
import os

DB_CONFIG = {
    'dbname': 'tganalyzer',
    'user': 'postgres',
    'password': 'Vovandrich1337',
    'host': 'localhost',
    'port': '5432'
}

class DatabaseManager:
    def __init__(self, config):
        self.config = config
        self.init_db()

    def get_connection(self):
        return psycopg2.connect(**self.config)

    def init_db(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS user_stats (
                        user_id BIGINT PRIMARY KEY,
                        username TEXT,
                        nickname TEXT,
                        total_messages INTEGER DEFAULT 0,
                        toxic_messages INTEGER DEFAULT 0,
                        positive_messages INTEGER DEFAULT 0,
                        questions_asked INTEGER DEFAULT 0,  -- для любопытства
                        responses_to_others INTEGER DEFAULT 0,  -- для отзывчивости
                        flood_warnings INTEGER DEFAULT 0,  -- для частоты сообщений
                        rule_violations INTEGER DEFAULT 0,  -- для нарушений правил
                        last_message_time TIMESTAMP,  -- для определения флуда
                        toxicity_sum FLOAT DEFAULT 0,
                        positivity_sum FLOAT DEFAULT 0,
                        activity_score FLOAT DEFAULT 0,
                        curiosity_score FLOAT DEFAULT 0,     -- Любопытство
                        responsiveness_score FLOAT DEFAULT 0, -- Отзывчивость
                        character_type TEXT,                 -- Тип характера (токсичный/позитивный/нейтральный)
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    CREATE TABLE IF NOT EXISTS message_history (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT REFERENCES user_stats(user_id),
                        username TEXT,
                        nickname TEXT,
                        message_text TEXT,
                        is_question BOOLEAN DEFAULT FALSE,
                        is_response BOOLEAN DEFAULT FALSE,
                        toxicity_level FLOAT,
                        positivity_level FLOAT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    CREATE TABLE IF NOT EXISTS user_activity (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT REFERENCES user_stats(user_id),
                        username TEXT,
                        nickname TEXT,
                        activity_type TEXT,
                        activity_value TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
                conn.commit()

    def save_message(self, user_id, username, nickname, message_text, toxicity_level, positivity_level, is_question, is_response):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO message_history (
                        user_id, username, nickname, message_text, toxicity_level, 
                        positivity_level, is_question, is_response
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    user_id, username, nickname, message_text, 
                    toxicity_level, positivity_level, is_question, is_response
                ))
                conn.commit()

    def get_user_stats(self, user_id):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute('''
                    SELECT * FROM user_stats WHERE user_id = %s
                ''', (user_id,))
                return cur.fetchone()

    def update_user_stats(self, user_id, username, nickname, toxicity_level, is_toxic, positivity_level, is_question, is_response, is_flood, characteristics):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO user_stats (
                        user_id, username, nickname, total_messages, toxic_messages, 
                        positive_messages, questions_asked, responses_to_others, flood_warnings,
                        toxicity_sum, positivity_sum, curiosity_score, responsiveness_score,
                        character_type, last_message_time
                    )
                    VALUES (%s, %s, %s, 1, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (user_id) DO UPDATE SET
                        username = EXCLUDED.username,
                        nickname = EXCLUDED.nickname,
                        total_messages = user_stats.total_messages + 1,
                        toxic_messages = user_stats.toxic_messages + %s,
                        positive_messages = user_stats.positive_messages + %s,
                        questions_asked = user_stats.questions_asked + %s,
                        responses_to_others = user_stats.responses_to_others + %s,
                        flood_warnings = user_stats.flood_warnings + %s,
                        toxicity_sum = user_stats.toxicity_sum + %s,
                        positivity_sum = user_stats.positivity_sum + %s,
                        curiosity_score = %s,
                        responsiveness_score = %s,
                        character_type = %s,
                        last_message_time = CURRENT_TIMESTAMP
                ''', (
                    user_id, username, nickname,
                    int(is_toxic), 
                    int(positivity_level > 0.3),
                    int(is_question), 
                    int(is_response), 
                    int(is_flood),
                    toxicity_level,
                    positivity_level,
                    characteristics['curiosity_score'],
                    characteristics['responsiveness_score'],
                    characteristics['user_type'][0],  # Берем первый тип характера
                    int(is_toxic),
                    int(positivity_level > 0.3),
                    int(is_question),
                    int(is_response),
                    int(is_flood),
                    toxicity_level,
                    positivity_level,
                    characteristics['curiosity_score'],
                    characteristics['responsiveness_score'],
                    characteristics['user_type'][0]
                ))
                conn.commit()

    def get_user_message_history(self, user_id):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute('''
                    SELECT * FROM message_history 
                    WHERE user_id = %s 
                    ORDER BY created_at DESC
                ''', (user_id,))
                return cur.fetchall()

    def save_user_activity(self, user_id, username, activity_type, activity_value):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO user_activity (
                        user_id, username, activity_type, activity_value
                    )
                    VALUES (%s, %s, %s, %s)
                ''', (user_id, username, activity_type, activity_value))
                conn.commit()

def create_user_chart(characteristics):
    # Характеристики для диаграммы
    categories = ['Позитивность', 'Активность', 'Отзывчивость', 
                 'Любознательность', 'Токсичность']
    
    # Значения характеристик
    values = [
        characteristics['positivity_ratio'],
        characteristics['activity_score'],
        characteristics['responsiveness_score'],
        characteristics['curiosity_score'],
        characteristics['toxicity_level']
    ]
    
    # Количество характеристик
    N = len(categories)
    
    # Угол для каждой характеристики
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    values += values[:1]
    
    # Создаем новый рисунок
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, projection='polar')
    
    # Рисуем диаграмму
    ax.plot(angles, values, 'o-', linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    
    # Насраиваем оси
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 1)
    
    # Добавляем сетку
    ax.grid(True)
    
    # Стилизация
    ax.set_facecolor('white')
    plt.gcf().patch.set_facecolor('white')
    
    # Сохраняем в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return buf

bot = telebot.TeleBot(API_TOKEN)
analyzer = SA.MessageAnalyzer()
db = DatabaseManager(DB_CONFIG)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Проверяем, личное ли это сообщение
    if message.chat.type == 'private':
        welcome_text = (
            "👋 Привет! Я бот для анализа сообщений в группах.\n\n"
            "🔹 Чтобы начать работу:\n"
            "1. Добавьте меня в нужную группу\n"
            "2. Сделайте меня администратором\n"
            "3. Напишите /start в группе\n\n"
            "❓ Используйте /help для просмотра всех команд\n"
            "📊 Используйте /generate_profile для просмотра вашего профиля"
        )
    else:
        welcome_text = (
            "👋 Привет! Я начал анализировать сообщения в этой группе.\n\n"
            "🤖 Я буду отслеживать активность и поведение участников, "
            "анализировать тональность сообщений и формировать профили пользователей.\n\n"
            "💡 Используйте /help для просмотра доступных команд."
        )
    bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(commands=['help'])
def send_help(message):
    if message.chat.type == 'private':
        help_text = (
            "📝 Доступные команды:\n\n"
            "/start - Информация о боте\n"
            "/generate_profile - Показать ваш профиль с диаграммой\n"
            "/help - Показать это сообщение"
        )
    else:
        help_text = (
            "📝 Доступные команды:\n\n"
            "/profile - Показать ваш профиль\n"
            "/stats - Показать общую статистику\n"
            "/generate - Создать диаграмму характеристик\n"
            "/top_active - Самые активные участники\n"
            "/top_positive - Самые позитивные участники\n"
            "/report - Отчет о нарушениях"
        )
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['profile'])
def send_profile(message):
    username = message.from_user.username or message.from_user.first_name or str(message.from_user.id)
    user_id = message.from_user.id
    stats = db.get_user_stats(user_id)
    message_history = db.get_user_message_history(user_id)
    
    if not stats or stats['total_messages'] == 0:
        bot.reply_to(message, "У вас пока нет сообщений для анализа!")
        return
    
    characteristics = analyzer.analyze_user_characteristics(stats, message_history)
    
    # Вычисляем дни активности
    days_active = max(1, (datetime.now() - stats['created_at']).days)
    msgs_per_day = stats['total_messages'] / days_active
    
    profile_text = (
        f"👤 Профиль пользователя {username}:\n\n"
        f"💭 Портрет: {characteristics['user_type'][0]}\n\n"
        f"Статистика:\n"
        f"🟢 Токсичность: {characteristics['toxicity_level']:.2f}\n"
        f"😊 Позитивность: {characteristics['positivity_ratio']:.2f}\n"
        f"❓ Любопытство: {characteristics['curiosity_score']:.2f}\n"
        f"👥 Отзывчивость: {characteristics['responsiveness_score']:.2f}\n"
        f"⚡ Частота сообщений: {characteristics['flood_score']:.2f}\n\n"
        f"📅 Дней активности: {days_active}\n"
        f"📊 Среднее сообщений в день: {msgs_per_day:.1f}\n"
        f"📝 Всего сообщений: {stats['total_messages']}"
    ).encode('utf-8').decode('utf-8')
    
    bot.reply_to(message, profile_text)

@bot.message_handler(commands=['stats'])
def send_stats(message):
    username = message.from_user.username or message.from_user.first_name or str(message.from_user.id)
    user_id = message.from_user.id
    stats = db.get_user_stats(user_id)
    message_history = db.get_user_message_history(user_id)
    
    if not stats or stats['total_messages'] == 0:
        bot.reply_to(message, "У вас пока нет сообщений для анализа!")
        return
    
    characteristics = analyzer.analyze_user_characteristics(stats, message_history)
    
    response = (
        f"📊 Профиль пользователя {message.from_user.username}:\n\n"
        f"📝 Всего сообщений: {stats['total_messages']}\n"
        f"💭 Тип поьзователя: {', '.join(characteristics['user_type'])}\n\n"
        f"📈 Характеристики:\n"
        f"▫️ Активность: {characteristics['activity_score']:.2f}/1.0\n"
        f"▫️ Позитивность: {characteristics['positivity_ratio']:.2f}/1.0\n"
        f"▫️ Токсичность: {characteristics['toxicity_level']:.2f}/1.0\n"
        f"▫️ Любознательность: {characteristics['curiosity_score']:.2f}/1.0\n"
        f"▫️ Отзывчивость: {characteristics['responsiveness_score']:.2f}/1.0\n"
    ).encode('utf-8').decode('utf-8')
    
    if characteristics['flood_score'] > 0:
        response += f"⚠️ Предупреждений за флуд: {stats['flood_warnings']}\n"
    if characteristics['rule_violations_ratio'] > 0:
        response += f"🚫 Нарушений правил: {stats['rule_violations']}\n"
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['generate'])
def send_chart(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or str(message.from_user.id)
    stats = db.get_user_stats(user_id)
    message_history = db.get_user_message_history(user_id)
    
    if not stats or stats['total_messages'] == 0:
        bot.reply_to(message, "У вас пока нет со��бщений для анализа!")
        return
    
    characteristics = analyzer.analyze_user_characteristics(stats, message_history)
    
    # Создаем диаграмму
    chart = create_user_chart(characteristics)
    
    # Отправляем диаграмму без подписи
    bot.send_photo(
        message.chat.id,
        photo=chart,
        reply_to_message_id=message.message_id
    )

@bot.message_handler(commands=['generate_profile'])
def generate_profile(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or str(message.from_user.id)
    stats = db.get_user_stats(user_id)
    message_history = db.get_user_message_history(user_id)
    
    if not stats or stats['total_messages'] == 0:
        no_data_text = (
            "👋 Я пока не вижу ваших сообщений в группах.\n\n"
            "Чтобы начать анализ:\n"
            "1. Добавьте меня в группу\n"
            "2. Сделайте администратором\n"
            "3. Начните общаться в группе\n\n"
            "После этого я смогу создать ваш профиль! 📊"
        )
        bot.reply_to(message, no_data_text)
        return
    
    # Если есть данные, генерируем профиль
    characteristics = analyzer.analyze_user_characteristics(stats, message_history)
    
    # Создаем диаграмму
    chart = create_user_chart(characteristics)
    
    # Формируем текст профиля
    profile_text = (
        f"👤 Профиль пользователя {username}:\n\n"
        f"💭 Характер: {characteristics['user_type'][0]}\n\n"
        f"📊 Статистика:\n"
        f"🟢 Токсичность: {characteristics['toxicity_level']:.2f}\n"
        f"😊 Позитивность: {characteristics['positivity_ratio']:.2f}\n"
        f"❓ Любопытство: {characteristics['curiosity_score']:.2f}\n"
        f"👥 Отзывчивость: {characteristics['responsiveness_score']:.2f}\n"
        f"⚡ Частота сообщений: {characteristics['flood_score']:.2f}\n\n"
        f"📝 Всего сообщений: {stats['total_messages']}"
    ).encode('utf-8').decode('utf-8')
    
    # Отправляем диаграмму с текстом
    bot.send_photo(
        message.chat.id,
        photo=chart,
        caption=profile_text,
        reply_to_message_id=message.message_id
    )

@bot.message_handler(content_types=['text'])
def send_response(message):
    user_id = message.from_user.id
    username = message.from_user.username
    nickname = message.from_user.first_name
    
    # Получаем историю сообщений пользователя для проверки флуда
    user_history = db.get_user_message_history(user_id)
    
    # Определяем, является ли сообщние ответом
    is_reply = message.reply_to_message is not None
    
    # Анализируем сообщение
    analysis = analyzer.analyze_message(message.text, user_history)
    
    # Получаем характеристики пользователя
    stats = db.get_user_stats(user_id)
    if stats:
        characteristics = analyzer.analyze_user_characteristics(stats, user_history)
    else:
        characteristics = {
            'curiosity_score': 0.0,
            'responsiveness_score': 0.0,
            'user_type': ['нейтралный']
        }
    
    # Обновляем статистику с характеристиками пользователя
    is_toxic = analysis['toxicity'] > 0.7
    db.update_user_stats(
        user_id,
        username,
        nickname,
        analysis['toxicity'],
        is_toxic,
        analysis['positivity'],
        analysis['is_question'],
        is_reply,
        analysis['is_flood'],
        characteristics
    )
    
    # Сохраняем сообщение в историю
    db.save_message(
        user_id,
        username,
        nickname,
        message.text,
        analysis['toxicity'],
        analysis['positivity'],
        analysis['is_question'],
        is_reply
    )

print("Бот запущен и готов к работе!")
bot.polling(none_stop=True)
