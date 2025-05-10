from celery import Celery
from proxy_utils import move_file_to_processing_directory, extract_file_info
import logging

# Инициализация приложения Celery
app = Celery('proxy_worker', broker='pyamqp://guest@localhost//')  # Укажите свой брокер сообщений

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Пример задачи, которая будет обрабатывать файлы
@app.task
def process_file(file_path: str):
    """
    Задача Celery для обработки файла.
    """
    logger.info(f"Начинаю обработку файла: {file_path}")

    # Перемещение файла в каталог обработки
    processing_directory = 'shared/uploads/processing'
    target_path = move_file_to_processing_directory(file_path, processing_directory)
    logger.info(f"Файл перемещен в каталог обработки: {target_path}")

    # Извлечение информации о файле
    file_info = extract_file_info(target_path)
    logger.info(f"Информация о файле: {file_info}")

    # Можно добавить дополнительную обработку данных из файла

    # Возвращаем результат
    return file_info


if __name__ == '__main__':
    # Запуск рабочего процесса Celery
    app.start()
