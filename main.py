import asyncio
import re
import json
import httpx
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentTypes


def get_token():
    with open('token.txt', 'r') as file:
        token: str = file.read().strip()
    return token


logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
bot = Bot(token=get_token())
dp = Dispatcher(bot)
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
}


def format_answer(text: str):
    new_text = text[text.find('Ответ:'):]

    return new_text


def format_string(text: str):
    new_text = text.replace('\\', '')
    new_text = new_text.replace('\r\n', '')
    new_text = new_text.replace('(', '')
    new_text = new_text.replace(')', '')

    new_text = new_text.replace('degree', '°')
    new_text = new_text.replace('angle', '∠')
    new_text = new_text.replace('Ответ:', 'Ответ: ')

    return new_text


def remove_http_stuff(text: str):
    returned_text = text

    returned_text = re.sub(r'(<(/?[^>]+)>)', '', returned_text)

    return returned_text


def is_url(url: str):
    match_obj = re.compile(r"https://edu\.skysmart\.ru/student/[a-z]+", re.IGNORECASE)

    return match_obj.match(url)


def get_uuid(url: str):
    match_obj = re.search(r"([A-Za-z0-9]+(-[A-Za-z0-9]+)+)", url)

    return match_obj.group(0)


async def get_position(api_uuid: str):
    async with httpx.AsyncClient(verify=False) as client:
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

    async with httpx.AsyncClient(verify=False) as client:
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
            while not finished:
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
                    answers: list[dict] = answers_dict['Answers']
                    result = []
                    for answer in answers:
                        answer_text = format_string(str(answer['Data']))
                        result_object = {
                            'Title': answer['Title'],
                            'Data': format_answer(remove_http_stuff(answer_text))
                        }
                        result.append(result_object)
                        await bot.send_message(
                            chat_id=msg.chat.id,
                            text=f"{result_object['Title']}\n"
                                 f"{result_object['Data']}",
                            reply_to_message_id=msg.message_id
                        )


if __name__ == '__main__':
    try:
        print("Bot is running")
        executor.start_polling(dp)
    except KeyboardInterrupt:
        pass
