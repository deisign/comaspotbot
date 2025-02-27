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

# Настройка Spotify API
sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri="https://spotify-refresh-token-generator.netlify.app",
    scope="user-follow-read",
    open_browser=False
)
sp = spotipy.Spotify(auth_manager=sp_oauth)

# Файл для хранения отправленных релизов
SENT_RELEASES_FILE = "sent_releases.json"

# Загрузка информации о ранее отправленных релизах
def load_sent_releases():
    try:
        if os.path.exists(SENT_RELEASES_FILE):
            with open(SENT_RELEASES_FILE, "r") as file:
                return json.load(file)
    except json.JSONDecodeError:
        print("Ошибка: Некорректный формат JSON. Создаю новый файл.")
        save_sent_releases({})
    return {}

# Сохранение отправленных релизов
def save_sent_releases(sent_releases):
    with open(SENT_RELEASES_FILE, "w") as file:
        json.dump(sent_releases, file)

# Проверка новых релизов и отправка в Telegram
async def check_and_notify():
    try:
        sent_releases = load_sent_releases()
        today = datetime.now()
        seven_days_ago = today - timedelta(days=7)

        artists = sp.current_user_followed_artists(limit=50)["artists"]["items"]

        for artist in artists:
            artist_name = artist["name"]
            artist_id = artist["id"]

            albums = sp.artist_albums(artist_id, album_type="album,single", limit=5)["items"]

            for album in albums:
                release_date = album["release_date"]
                album_name = album["name"]
                album_url = album["external_urls"]["spotify"]
                album_id = album["id"]

                try:
                    release_date_obj = datetime.strptime(release_date, "%Y-%m-%d")
                except ValueError:
                    continue

                if seven_days_ago <= release_date_obj <= today and album_id not in sent_releases:
                    # Формируем сообщение
                    message = f"🎵 Новый релиз от {artist_name}!\n\n{album_name} ({release_date})\nСлушать: {album_url}"
                    
                    await bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message)

                    sent_releases[album_id] = True

        save_sent_releases(sent_releases)

    except Exception as e:
        print(f"Ошибка: {e}")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я работаю через polling!")

# Основной запуск
def main():
    print("Запуск polling...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))

    # Регулярная проверка новинок
    async def periodic_task():
        while True:
            await check_and_notify()
            await asyncio.sleep(600)  # Проверка каждые 10 минут

    loop = asyncio.get_event_loop()
    loop.create_task(periodic_task())

    application.run_polling()

if __name__ == "__main__":
    main()
