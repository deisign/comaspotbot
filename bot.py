from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

# Получаем токены из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # HTTPS URL для вебхука
PORT = int(os.getenv("PORT", 5000))  # Порт для Railway (по умолчанию 5000)

# Telegram бот
bot = Bot(token=BOT_TOKEN)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я работаю через вебхуки!")

# Команда /test для проверки отправки сообщений
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await bot.send_message(chat_id=update.effective_chat.id, text="Тестовое сообщение: бот работает!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# Основной запуск
def main():
    print("Starting webhook application...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test", test))

    # Настройка вебхуков
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,  # Используем порт 5000
        webhook_url=WEBHOOK_URL  # HTTPS URL для Telegram
    )

if __name__ == "__main__":
    main()
