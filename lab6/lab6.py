import logging
import logging.config
import time
import functools
from flask import Flask, request, jsonify
import yaml
import os
from datetime import datetime

# Создаем Flask приложение
app = Flask(__name__)

# 1. Настройка логирования с конфигурацией из файла
def setup_logging():
    # Создаем базовую директорию для логов
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Настраиваем конфигурацию логирования
    logging_config = {
        'version': 1,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'simple': {
                'format': '%(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'simple'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': 'logs/app.log',
                'maxBytes': 1024 * 1024,  # 1MB
                'backupCount': 3
            },
            'error_file': {
                'class': 'logging.FileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': 'logs/error.log'
            }
        },
        'loggers': {
            'app': {
                'level': 'DEBUG',
                'handlers': ['console', 'file', 'error_file']
            }
        }
    }
    
    # Применяем конфигурацию
    logging.config.dictConfig(logging_config)
    return logging.getLogger('app')

# 2. Декоратор для логирования времени выполнения методов
def log_execution_time(logger):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logger.debug(f'Метод {func.__name__} выполнен за {execution_time:.2f} секунд')
            return result
        return wrapper
    return decorator

# 3. Обработчик исключений
@app.errorhandler(Exception)
def handle_exception(error):
    logger.error(f'Ошибка: {str(error)}', exc_info=True)
    return jsonify({'error': str(error)}), 500

# Создаем логгер
logger = setup_logging()

# Пример эндпоинта с логированием
@app.route('/api/test', methods=['GET'])
@log_execution_time(logger)
def test_endpoint():
    logger.info(f'Получен GET запрос от {request.remote_addr}')
    
    # Симулируем разные уровни логирования
    logger.debug('Детальная отладочная информация')
    logger.info('Информационное сообщение')
    logger.warning('Предупреждение')
    
    # Симулируем ошибку для тестирования логирования ошибок
    if 'error' in request.args:
        raise Exception('Тестовая ошибка')
    
    return jsonify({'status': 'success'})

# 4. Логирование SQL-запросов (пример)
def log_sql_query(query, params=None):
    logger.debug(f'SQL Query: {query}')
    if params:
        logger.debug(f'Parameters: {params}')

# 5. Пример метода с пользовательским уровнем логирования
@app.route('/api/verbose', methods=['GET'])
@log_execution_time(logger)
def verbose_endpoint():
    logger.log(logging.INFO + 5, 'Очень подробное логирование')
    return jsonify({'status': 'verbose logging example'})

if __name__ == '__main__':
    # Логируем запуск приложения
    logger.info('Приложение запущено')
    
    try:
        app.run(debug=True, port=5000)
    except Exception as e:
        logger.critical(f'Критическая ошибка при запуске приложения: {str(e)}')
