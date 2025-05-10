import os
import shutil

# Пример функции для работы с файлами
def move_file_to_processing_directory(file_path: str, processing_directory: str):
    """
    Функция для перемещения файла в каталог обработки.
    """
    if not os.path.exists(processing_directory):
        os.makedirs(processing_directory)

    # Получаем имя файла из пути
    file_name = os.path.basename(file_path)
    target_path = os.path.join(processing_directory, file_name)

    # Перемещаем файл
    shutil.move(file_path, target_path)

    return target_path


# Пример функции для работы с данными
def extract_file_info(file_path: str):
    """
    Функция для извлечения информации из файла.
    Может быть полезно для анализа данных из файлов.
    """
    file_info = {
        'file_size': os.path.getsize(file_path),
        'file_name': os.path.basename(file_path),
        'file_extension': os.path.splitext(file_path)[-1]
    }
    return file_info
