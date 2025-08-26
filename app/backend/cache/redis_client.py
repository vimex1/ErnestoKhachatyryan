import redis
from app.backend.config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD

# Подключение к Redis
redis_client = redis.Redis(
    host=REDIS_HOST,           # Адрес сервера Redis
    port=REDIS_PORT,           # Порт (обычно 6379)
    db=REDIS_DB,               # Номер базы данных
    #password=REDIS_PASSWORD,   # Пароль (если есть)
    decode_responses=True       # Декодинг ответов в строки
)

# Простые функции для работы с Redis
def set_value(key, value, expire=None):
    """Сохранить значение в Redis"""
    redis_client.set(key, value, ex=expire)

def get_value(key):
    """Получить значение из Redis"""
    return redis_client.get(key)

def delete_key(key):
    """Удалить ключ из Redis"""
    redis_client.delete(key)

def key_exists(key):
    """Проверить, существует ли ключ"""
    return redis_client.exists(key)

# Пример использования:
# set_value("user:123", "John Doe", expire=3600)  # Сохранить на 1 час
# user_name = get_value("user:123")               # Получить значение
# delete_key("user:123")                          # Удалить ключ
