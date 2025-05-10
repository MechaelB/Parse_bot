# Базовый образ с Python
FROM python:3.11-slim

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копируем зависимости
COPY requirements.txt ./

# Установим зависимости для браузеров Playwright
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libnss3-tools \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxrandr2 \
    libxss1 \
    libasound2 \
    libxshmfence1 \
    libxfixes3 \
    libxrender1 \
    libxcursor1 \
    libxi6 \
    libxtst6 \
    libcups2 \
    libexpat1 \
    libatspi2.0-0 \
    fonts-liberation \
    libdrm2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


# Установка Python-зависимостей
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install-deps
RUN playwright install

# Копируем скрипт парсера и задачи Celery
COPY parser.py tasks.py celeryconfig.py .env ./


# Указываем команду по умолчанию для запуска Celery worker
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]
