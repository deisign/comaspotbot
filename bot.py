from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timedelta
import json
import asyncio

# Получаем токены из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Должно быть https://comaspotbot-production.up.railway.app

# Настройка Spotify API с использованием Refresh Token
sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri="https://spotify-refresh-token-generator.netlify.app",
    scope="user-follow-read",
    open_browser=False
)
sp_oauth.refresh_access_token(SPOTIFY_REFRESH_TOKEN)
sp = spotipy.Spotify(auth_manager=sp_oauth)

# Telegram бот
bot = Bot(token=BOT_TOKEN)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я работаю через вебхуки!")

# Тестовая команда /test
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text="Тестовое сообщение: бот работает!")
        await update.message.reply_text("Сообщение отправлено в канал!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# Проверка новых релизов и отправка в канал
async def check_and_notify():
    try:
        # Загружаем отправленные релизы
        sent_releases = load_sent_releases()

        # Вычисляем дату 7 дней назад
        today = datetime.now()
        seven_days_ago = today - timedelta(days=7)

        # Получаем список подписанных артистов
        artists = sp.current_user_followed_artists(limit=50)["artists"]["items"]

        # Проверяем новые релизы для каждого артиста
        for artist in artists:
            artist_name = artist["name"]
            artist_id = artist["id"]

            # Получаем альбомы и синглы артиста
            albums = sp.artist_albums(artist_id, album_type="album,single", limit=5)["items"]

            for album in albums:
                release_date = album["release_date"]
                album_name = album["name"]
                album_url = album["external_urls"]["spotify"]
                album_id = album["id"]

                # Конвертируем дату релиза
                try:
                    release_date_obj = datetime.strptime(release_date, "%Y-%m-%d")
                except ValueError:
                    continue

                # Если релиз новый и ещё не отправлялся
                if seven_days_ago <= release_date_obj <= today and album_id not in sent_releases:
                    # Отправляем сообщение в Telegram
                    message = f"🎵 Новый релиз от {artist_name}!\n\n{album_name} ({release_date})\n\nСлушайте: {album_url}"
                    await bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message)

                    # Добавляем релиз в отправленные
                    sent_releases[album_id] = True

        # Сохраняем обновлённый список отправленных релизов
        save_sent_releases(sent_releases)

    except Exception as e:
        await bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=f"Ошибка: {e}")

# Загрузка информации о ранее отправленных релизах
def load_sent_releases():
    if os.path.exists("sent_releases.json"):
        with open("sent_releases.json", "r") as file:
            return json.load(file)
    return {}

# Сохранение отправленных релизов
def save_sent_releases(sent_releases):
    with open("sent_releases.json", "w") as file:
        json.dump(sent_releases, file)

# Настройка приложения
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test", test))

    # Настройка вебхуков
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8443)),
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
