import psycopg2

DB_CONFIG = {
    'dbname': 'tganalyzer',
    'user': 'postgres',
    'password': 'Vovandrich1337',
    'host': 'localhost',
    'port': '5432'
}

def create_database():
    conn = psycopg2.connect(
        dbname='postgres',
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host']
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'tganalyzer'")
    if not cur.fetchone():
        cur.execute('CREATE DATABASE tganalyzer')
    
    cur.close()
    conn.close()

def init_tables():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    cur.execute('''
        DROP TABLE IF EXISTS message_history CASCADE;
        DROP TABLE IF EXISTS user_activity CASCADE;
        DROP TABLE IF EXISTS user_stats CASCADE;
    ''')

    cur.execute('''
        CREATE TABLE user_stats (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            nickname TEXT,
            total_messages INTEGER DEFAULT 0,
            toxic_messages INTEGER DEFAULT 0,
            positive_messages INTEGER DEFAULT 0,
            questions_asked INTEGER DEFAULT 0,
            responses_to_others INTEGER DEFAULT 0,
            flood_warnings INTEGER DEFAULT 0,
            rule_violations INTEGER DEFAULT 0,
            last_message_time TIMESTAMP,
            toxicity_sum FLOAT DEFAULT 0,
            positivity_sum FLOAT DEFAULT 0,
            activity_score FLOAT DEFAULT 0,
            curiosity_score FLOAT DEFAULT 0,
            responsiveness_score FLOAT DEFAULT 0,
            character_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE message_history (
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
        
        CREATE TABLE user_activity (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES user_stats(user_id),
            username TEXT,
            nickname TEXT,
            activity_type TEXT,
            activity_value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    cur.execute('''
        CREATE INDEX idx_message_history_user_id ON message_history(user_id);
        CREATE INDEX idx_message_history_username ON message_history(username);
        CREATE INDEX idx_user_activity_user_id ON user_activity(user_id);
        CREATE INDEX idx_user_activity_username ON user_activity(username);
    ''')
    
    cur.execute('''
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
    ''')
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    try:
        print("Создаем базу данных...")
        create_database()
        print("База данных создана успешно!")
        
        print("Инициализируем таблицы...")
        init_tables()
        print("Таблицы созданы успешно!")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}") 