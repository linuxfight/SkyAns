import yt_dlp
import os
from pyrogram import enums
from utils.storage import save, load
from utils.download import download


storage = load()


async def on_callback_query(client, callback_query):
    data = callback_query.data.split(':')
    video_id = data[0]
    download_type = data[1]
    with yt_dlp.YoutubeDL() as ydl:
        info: dict = ydl.extract_info(
            download=False,
            url=f'https://youtu.be/{video_id}'
        )
    telegram_filename = info['title'] + '.mkv'
    if download_type == 'audio':
        telegram_filename = info['title'] + '.mp3'

    if f'{video_id}_{download_type}' in storage:
        if storage[f'{video_id}_{download_type}'] is None:
            return
        if storage[f'{video_id}_{download_type}'] != "Working":
            file = storage[f'{video_id}_{download_type}']
            if download_type == 'video':
                await client.send_chat_action(
                    chat_id=callback_query.message.chat.id,
                    action=enums.ChatAction.UPLOAD_VIDEO
                )
                await client.send_document(
                    chat_id=callback_query.message.chat.id,
                    reply_to_message_id=callback_query.message.id,
                    document=file,
                    file_name=telegram_filename
                )
            else:
                await client.send_chat_action(
                    chat_id=callback_query.message.chat.id,
                    action=enums.ChatAction.UPLOAD_AUDIO
                )
                await client.send_audio(
                    chat_id=callback_query.message.chat.id,
                    reply_to_message_id=callback_query.message.id,
                    audio=file,
                    file_name=telegram_filename
                )
            return

    try:
        if f'{video_id}_{download_type}' in storage and storage[f'{video_id}_{download_type}'] == "Working":
            await callback_query.answer(
                text="⚙ Производится скачивание, пожалуйста подождите"
            )
            return

        await callback_query.answer(
            text="⚙ Обработка запроса"
        )
    except:
        return

    storage.update({f'{video_id}_{download_type}': "Working"})

    file_path = await download(f'https://youtu.be/{video_id}', download_type)
    await client.send_chat_action(
        chat_id=callback_query.message.chat.id,
        action=enums.ChatAction.UPLOAD_DOCUMENT
    )
    file = None
    if download_type == 'video':
        await client.send_chat_action(
            chat_id=callback_query.message.chat.id,
            action=enums.ChatAction.UPLOAD_VIDEO
        )
        file = await client.send_document(
            chat_id=callback_query.message.chat.id,
            reply_to_message_id=callback_query.message.id,
            document=file_path,
            file_name=telegram_filename
        )
    else:
        await client.send_chat_action(
            chat_id=callback_query.message.chat.id,
            action=enums.ChatAction.UPLOAD_AUDIO
        )
        file = await client.send_audio(
            chat_id=callback_query.message.chat.id,
            reply_to_message_id=callback_query.message.id,
            audio=file_path,
            file_name=telegram_filename
        )
    file_id = None
    if file.document:
        file_id = file.document.file_id
    elif file.video:
        file_id = file.video.file_id
    else:
        file_id = file.audio.file_id
    storage.update({f'{video_id}_{download_type}': file_id})
    os.remove(file_path)
    await save(storage)
