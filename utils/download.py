import asyncio
from utils.get_video_id import get_video_id
from os.path import exists


async def download(video_url, download_type):
    video_id = get_video_id(video_url)
    output_filename = video_id + '.mkv'
    command = f'yt-dlp --merge-output-format mkv -o "{output_filename}" {video_url} --quiet'

    if download_type == "audio":
        output_filename = video_id + '.mp3'
        command = f'yt-dlp -f "ba" -x --audio-format mp3 -o "{output_filename}" {video_url} --quiet'

    process = await asyncio.create_subprocess_shell(
        command
    )

    await process.communicate()

    while process.returncode != 0:
        pass
    else:
        while not exists(output_filename):
            pass
        else:
            return output_filename
