import aiofiles
import json
from os.path import exists


def load():
    if exists("save.json"):
        with open("save.json", 'r') as file:
            data = file.read()
        return json.loads(data)
    else:
        data = {}
        with open("save.json", 'w') as file:
            file.write(json.dumps(data))
        return load()


async def save(self):
    async with aiofiles.open("save.json", 'w') as file:
        await file.write(json.dumps(self))
