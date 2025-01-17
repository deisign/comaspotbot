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
