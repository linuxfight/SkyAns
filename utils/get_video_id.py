import re


def get_video_id(url: str):
    regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.'
                       r'(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})')

    match = regex.match(url)

    if not match:
        return None
    return match.group('id')
