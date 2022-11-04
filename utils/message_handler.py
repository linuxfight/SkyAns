import re
import yt_dlp
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.get_video_id import get_video_id


def generate_keyboard(video_id):
    buttons = [[
        InlineKeyboardButton(
            text="⬇ Скачать видео 🎥",
            callback_data=video_id + ":video"
        ),
        InlineKeyboardButton(
            text="⬇ Скачать аудио 🎙",
            callback_data=video_id + ":audio"
        )]]
    return InlineKeyboardMarkup(
        buttons
    )


def is_url(url):
    match_obj = re.match(r'^((?:https?:)?//)?((?:www|m)\.)?(youtube(-nocookie)?\.com|youtu.be)(/(?:[\w\-]+\?v=|embed/|v'
                         r'/)?)([\w\-]+)(\S+)?$', url)
    if match_obj:
        return True
    return False


async def on_start_message(client, msg):
    await client.send_message(
        chat_id=msg.chat.id,
        text="Привет, я помогу тебе скачать видео с Youtube! Отправь мне ссылку и я отправлю тебе видео.",
        reply_to_message_id=msg.id
    )


async def on_link(client, msg):
    text = None
    try:
        text = msg.text.split()
    except ValueError:
        pass
    url = None
    try:
        for t in text:
            if is_url(t):
                url = t
    except ValueError:
        pass
    if not url:
        return

    with yt_dlp.YoutubeDL() as ydl:
        info: dict = ydl.extract_info(url, download=False)
    title = info.get('title', None)

    await client.send_message(
        chat_id=msg.chat.id,
        reply_to_message_id=msg.id,
        reply_markup=generate_keyboard(get_video_id(url)),
        text=f"Название: {title}\n"
             f"Ссылка: {url}\n"
    )
