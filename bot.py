from telegram import Bot
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timedelta
import time
import json

# Получаем токены из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

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

# Имя файла для хранения уже отправленных релизов
SENT_RELEASES_FILE = "sent_releases.json"

# Загрузка информации о ранее отправленных релизах
def load_sent_releases():
    if os.path.exists(SENT_RELEASES_FILE):
        with open(SENT_RELEASES_FILE, "r") as file:
            return json.load(file)
    return {}

# Сохранение отправленных релизов
def save_sent_releases(sent_releases):
    with open(SENT_RELEASES_FILE, "w") as file:
        json.dump(sent_releases, file)

# Проверка новых релизов и отправка в канал
def check_and_notify():
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
                    bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message)

                    # Добавляем релиз в отправленные
                    sent_releases[album_id] = True

        # Сохраняем обновлённый список отправленных релизов
        save_sent_releases(sent_releases)

    except Exception as e:
        bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=f"Ошибка: {e}")

# Основной цикл
def main():
    while True:
        check_and_notify()
        time.sleep(600)  # Проверяем каждые 10 минут

if __name__ == "__main__":
    main()
