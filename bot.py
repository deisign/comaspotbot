from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

import os

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Команда /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Привет! Я готов работать!")

# Настройка бота
def main():
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Добавляем обработчик команды /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
