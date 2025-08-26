from celery import Celery
from app.backend.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

# Создаем приложение Celery
# Celery - это система для выполнения фоновых задач
celery_app = Celery(
    "my_app",                     # Имя приложения
    broker=CELERY_BROKER_URL,     # Где брать задачи (Redis)
    backend=CELERY_RESULT_BACKEND # Где хранить результаты (Redis)
)

# Настройки Celery
celery_app.conf.update(
    task_serializer="json",       # Формат задач
    accept_content=["json"],      # Какие форматы принимаем
    result_serializer="json",     # Формат результатов
    timezone="UTC",               # Часовой пояс
    enable_utc=True,              # Использовать UTC
)

# Простая функция для проверки работы Celery
@celery_app.task
def simple_task(message):
    """Простая задача для тестирования"""
    return f"Задача выполнена: {message}"

# Пример использования:
# result = simple_task.delay("Привет!")
# print(result.get())  # Получить результат
