import asyncio
import aiofiles
import re
import json
import httpx
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentTypes


def get_token():
    with open('token.txt', 'r') as file:
        token: str = file.read().strip()
    return token


bot = Bot(token=get_token())
dp = Dispatcher(bot)
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
}


def is_url(url: str):
    match_obj = re.compile(r"https://edu\.skysmart\.ru/student/[a-z]+", re.IGNORECASE)

    return match_obj.match(url)


def get_uuid(url: str):
    match_obj = re.search(r"([A-Za-z0-9]+(-[A-Za-z0-9]+)+)", url)

    return match_obj.group(0)


async def get_position(api_uuid: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            headers=headers,
            url=f'https://amogus.somee.com/API/GetQueuePosition?uuid={api_uuid}'
        )
        while response.status_code == 429:
            await asyncio.sleep(int(response.headers['retry-after']))
            response = await client.get(
                headers=headers,
                url=f'https://amogus.somee.com/API/GetQueuePosition?uuid={api_uuid}'
            )

    return int(response.content) + 1


@dp.message_handler(commands=['start'])
async def on_start(msg: types.Message):
    await bot.send_message(
        chat_id=msg.chat.id,
        reply_to_message_id=msg.message_id,
        text="Привет, я бот для решения тестов на skysmart! "
             "Отправь мне ссылку и я пришлю тебе ответ."
    )


@dp.message_handler(content_types=ContentTypes.TEXT)
async def on_link(msg: types.Message):
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

    ready = False

    async with httpx.AsyncClient() as client: # fix this SHIT on windows
        response = await client.get(
            headers=headers,
            url=f'https://amogus.somee.com/API/LinkRedirect?link={url}',
            follow_redirects=True
        )

        api_uuid = get_uuid(str(response.url))

        finished = False

        while await get_position(api_uuid) > 0:
            pass
        else:
            while finished == False:
                try:
                    response = await client.get(
                        headers=headers,
                        url=f'https://amogus.somee.com/API/RemoveFinishedItem?uuid={api_uuid}'
                    )
                    if response.text != 'null':
                        finished = True
                except ConnectionResetError:
                    pass
            else:
                while response.content == b'null' or response.content == b'':
                    pass
                else:
                    response_dict: dict = json.loads(response.text)
                    answers_dict: dict = response_dict['SolverOutput']
                    async with aiofiles.open('answers.txt', 'w', encoding='utf8') as file:
                        await file.write(
                            str(answers_dict['Answers']).replace('\\', '').replace('\r\n', '')
                        )
                    ready = True
    while ready == False:
        pass
    else:
        await bot.send_document(
            chat_id=msg.chat.id,
            reply_to_message_id=msg.message_id,
            document=types.InputFile(
                path_or_bytesio='answers.txt',
                filename='answers.txt'
            )
        )


if __name__ == '__main__':
    try:
        print("Bot is running")
        executor.start_polling(dp)
    except KeyboardInterrupt:
        pass
