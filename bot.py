from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import os

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я готов работать!")

# Настройка приложения
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
