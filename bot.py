from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Получаем токены из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")

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

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я готов работать!")

# Команда /releases для проверки новых релизов
async def releases(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Получаем список подписанных артистов
        artists = sp.current_user_followed_artists(limit=50)["artists"]["items"]
        new_releases = []

        # Проверяем новые релизы для каждого артиста
        for artist in artists:
            artist_name = artist["name"]
            artist_id = artist["id"]

            # Получаем альбомы и синглы артиста
            albums = sp.artist_albums(artist_id, album_type="album,single", limit=5)["items"]

            # Проверяем дату релиза
            for album in albums:
                release_date = album["release_date"]
                album_name = album["name"]
                album_url = album["external_urls"]["spotify"]

                # Добавляем только релизы за последние 7 дней
                if "2025-01-01" <= release_date <= "2025-01-14":  # Пример: заменить на динамическую проверку
                    new_releases.append(f"{artist_name}: {album_name} ({release_date})\n{album_url}")

        # Формируем сообщение
        if new_releases:
            message = "Новинки за последние дни:\n\n" + "\n\n".join(new_releases)
        else:
            message = "Пока новых релизов нет."

        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# Настройка приложения
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("releases", releases))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
