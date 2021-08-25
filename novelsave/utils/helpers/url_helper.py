import re
from urllib.parse import urlparse

url_start_pattern = re.compile(r'^https?://')


def absolute_url(url: str, location: str):
    """convert the url into absolute"""
    path = url.lstrip('/')
    if url_start_pattern.match(url):
        return url
    elif url.startswith('/'):
        return f'{location}/{path}'
    else:
        parse_result = urlparse(location)
        base_url = f'{parse_result.scheme}://{parse_result.netloc}'
        return f'{base_url}/{path}'
