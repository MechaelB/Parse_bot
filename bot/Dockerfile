# Базовый образ с Python
FROM python:3.11-slim

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копируем зависимости
COPY requirements.txt ./

# Установка Python-зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота
COPY bot.py ./

# Указываем команду по умолчанию
CMD ["python", "bot.py"]
