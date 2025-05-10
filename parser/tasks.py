from celery import Celery
from parser import main
from telegram import Bot
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)

app = Celery('tasks',
             broker='redis://redis:6379/0',
             backend='redis://redis:6379/0')

app.conf.update(
    accept_content=['json'],
    task_serializer='json',
    result_serializer='json',
)

@app.task(name="tasks.task")
def task(file_path, user_id):
    try:
        result = main(file_path)

        bot.send_message(chat_id=user_id, text="Парсинг завершён!")

        base, _ = os.path.splitext(file_path)
        result_path = base + "_result.csv"

        if os.path.exists(result_path):
            with open(result_path, "rb") as f:
                bot.send_document(chat_id=user_id, document=f, filename=os.path.basename(result_path))
        else:
            bot.send_message(chat_id=user_id, text="Результирующий файл не найден.")

        return result

    except Exception as e:
        bot.send_message(chat_id=user_id, text=f"Произошла ошибка при парсинге: {e}")
        return str(e)
