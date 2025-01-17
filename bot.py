from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Получаем токены из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")

# Настройка Spotify API с использованием Refresh Token
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я готов работать!")

# Команда /artists для проверки Spotify API
async def artists(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Получаем список артистов
        results = sp.current_user_followed_artists(limit=10)
        artists_list = [artist["name"] for artist in results["artists"]["items"]]
        if artists_list:
            message = "Твои артисты:\n" + "\n".join(artists_list)
        else:
            message = "У тебя пока нет подписок на артистов."
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# Настройка приложения
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("artists", artists))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
