# Bot
Telegram Bot на Python с использованием Selenium и Docker
Описание
Этот проект представляет собой Telegram-бота, который использует Selenium для парсинга веб-страниц и Docker для контейнеризации приложения.

Требования
Python 3.8+
Selenium 3.141.0+
Docker 20.10.0+
Telegram Bot API
Установка
Клонировать репозиторий: git clone https://github.com/MechaelB/Bot.git
Перейти в папку проекта: cd Bot
Создать файл .env с переменными окружения:
TOKEN - токен Telegram-бота
CHROME_DRIVER_PATH - путь к исполняемому файлу ChromeDriver
Установить зависимости: pip install -r requirements.txt
Собрать Docker-образ: docker build -t bot .
Запустить Docker-контейнер: docker run -d -p 8080:8080 bot
Использование
Отправить сообщение Telegram-боту с командой /start
Бот ответит с помощью Selenium-парсинга веб-страницы
Разработка
Для разработки рекомендуется использовать IDE, такой как PyCharm или Visual Studio Code
Для отладки можно использовать Docker-compose для запуска контейнера в режиме отладки
CONTRIBUTING
Для внесения изменений в проект, пожалуйста, создайте новую ветку и отправьте pull-request
Для обсуждения изменений, пожалуйста, используйте Issues
LICENSE
Этот проект распространяется под лицензией MIT
AUTHORS
MechaelB - создатель проекта