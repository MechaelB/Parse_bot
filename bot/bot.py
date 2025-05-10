import asyncio
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from celery import Celery
from celery.result import AsyncResult

celery_app = Celery("bot", broker="redis://redis:6379/0", backend="redis://redis:6379/1")

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токен
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("Не задан токен для бота. Убедитесь, что переменная TOKEN есть в файле .env.")

app = ApplicationBuilder().token(TOKEN).build()

# Папка для сохранения файлов
FILES_DIR = "shared/uploads"
os.makedirs(FILES_DIR, exist_ok=True)  # Создаем папку, если она не существует

# Флаг, чтобы отслеживать активную сессию
active_sessions = {}

# Храним список полученных файлов для последующего выбора
received_files = {}

# Функция для отправки клавиатуры
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    active_sessions[user_id] = 'open'
    context.user_data['session_active'] = True

    keyboard = [
        ['/start', '/help'],
        ['Сказать привет', 'Сказать пока'],
        ['/stop', '/start_parser']  # Добавляем новую команду /start_parser
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('Выбери действие:', reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Я могу:\n- Поздороваться\n- Попрощаться\n\nНажми на кнопку ниже!')

# Функция для обработки сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in active_sessions and active_sessions[user_id] == 'closed':
        await update.message.reply_text('Сессия завершена. Нажмите /start для новой сессии.')
        return

    text = update.message.text.lower()
    if 'привет' in text:
        await update.message.reply_text('Привет-привет! 👋')
    elif 'пока' in text:
        await update.message.reply_text('Пока! Хорошего дня! 👋')
    else:
        await update.message.reply_text('Я не понимаю это сообщение. Попробуй нажать на кнопку!')

# Функция для завершения сессии
async def close_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    active_sessions[user_id] = 'closed'
    await update.message.reply_text('Сессия завершена. Если хочешь начать заново, нажми /start.')

# Храним файлы отдельно по каждому пользователю
received_files = {}

# # Обработка загруженного файла
# async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     file = update.message.document
#     file_name = file.file_name.lower()
#     user_id = update.message.from_user.id

#     # Проверка расширения файла
#     allowed_extensions = ['.xlsx', '.csv', '.txt']
#     if any(file_name.endswith(ext) for ext in allowed_extensions):
#         file_path = os.path.join(FILES_DIR, file_name)
#         file_object = await file.get_file()
#         await file_object.download_to_drive(file_path)

#         # Сохраняем путь к файлу отдельно для пользователя
#         if user_id not in received_files:
#             received_files[user_id] = []
#         received_files[user_id].append(file_path)

#         await update.message.reply_text(f"Файл '{file_name}' успешно получен и сохранен. Начинаю парсинг!")
#         await start_parser(update, context, file_path)
#     else:
#         await update.message.reply_text("Неподдерживаемый формат файла. Пожалуйста, отправьте .xlsx, .csv или .txt.")

# Обработка загруженного файла
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    file_name = file.file_name.lower()
    user_id = update.message.from_user.id

    # Проверка расширения файла
    allowed_extensions = ['.xlsx', '.csv', '.txt']
    if any(file_name.endswith(ext) for ext in allowed_extensions):
        # Создаем папку для пользователя, если она не существует
        user_folder = os.path.join(FILES_DIR, str(user_id))
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        # Сохраняем файл в папке пользователя
        file_path = os.path.join(user_folder, file_name)
        file_object = await file.get_file()
        await file_object.download_to_drive(file_path)

        # Сохраняем путь к файлу отдельно для пользователя
        if user_id not in received_files:
            received_files[user_id] = []
        received_files[user_id].append(file_path)

        await update.message.reply_text(f"Файл '{file_name}' успешно получен и сохранен. Начинаю парсинг!")
        await start_parser(update, context, file_path)
    else:
        await update.message.reply_text("Неподдерживаемый формат файла. Пожалуйста, отправьте .xlsx, .csv или .txt.")

# Модифицированный start_parser
async def start_parser(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str = None):
    user_id = update.message.from_user.id

    # Проверка наличия файла
    if not file_path:
        if user_id not in received_files or not received_files[user_id]:
            await update.message.reply_text("У вас нет файлов для парсинга. Сначала отправьте файл.")
            return
        
        # Если файлов много, даем пользователю выбор
        keyboard = [[file] for file in received_files[user_id]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text("Выберите файл для парсинга:", reply_markup=reply_markup)
        return

    # Имя для файла с результатом
    result_file = os.path.join(os.path.dirname(file_path).replace("uploads","results"), os.path.basename(file_path).replace('.csv', '_result.csv').replace('.xlsx', '_result.csv').replace('.txt', '_result.csv'))

    try:
        # Отправка задачи на парсинг через Celery
        #task = celery_app.send_task('tasks.task', args=[file_path])

        task = celery_app.send_task('tasks.task', args=[file_path, user_id])  # Передаём user_id
        await update.message.reply_text(f"Задача на парсинг запущена! ID задачи: {task.id}. Результат придет позже.")


        # # Ожидание завершения задачи
        # result = AsyncResult(task.id, app=celery_app)
        # while not result.ready():
        #     await asyncio.sleep(1)  # Ожидание завершения задачи

        # # Получаем результат выполнения
        # if result.status == 'SUCCESS':
        #     await update.message.reply_text("Парсер завершил работу, отправляю результат!")

        #     # Отправляем результат парсинга пользователю
        #     if os.path.exists(result_file):
        #         with open(result_file, 'rb') as f:
        #             await update.message.reply_document(f, filename=result_file)
        #     else:
        #         await update.message.reply_text("Ошибка: Результат парсинга не найден.")
        # else:
        #     await update.message.reply_text(f"Ошибка при парсинге: {result.info}")

    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка:\n{str(e)}")

    

async def main():
    # Регистрация обработчиков команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stop", close_session))  # Завершение сессии
    app.add_handler(CommandHandler("start_parser", start_parser))  # Новый обработчик для /start_parser
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))  # Обработчик для файлов

    print("Бот запущен...")

# Запуск
if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main())
        loop.run_until_complete(app.run_polling())
    except Exception as e:
        print("Ошибка : ", e)
    finally:
        loop.close()
