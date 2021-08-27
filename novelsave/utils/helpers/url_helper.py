import re
from urllib.parse import urlparse

url_start_pattern = re.compile(r'^https?://')

url_pattern = re.compile(
    r'https?://(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&/=]*)')


def absolute_url(url: str, location: str):
    """Resolve the url into an absolute url

    :param url: The url to be resolved, it can start with '/', '//', '', or 'https?://'.
    :param location: Location from which the url was retrieved.
    :returns: Absolute url derived using the parameters.
    """
    path = url.lstrip('/')
    if url_start_pattern.match(url):
        return url
    elif url.startswith('/'):
        return f'{location.rstrip("/")}/{path}'

    parse_result = urlparse(location)
    if url.startswith('//'):
        return f'{parse_result.scheme}:{url}'
    else:
        base_url = f'{parse_result.scheme}://{parse_result.netloc}'
        return f'{base_url}/{path}'


def is_url(p_url: str):
    """Checks whether the the provided string is a url

    >>> is_url('http://my.site/')
    True

    >>> is_url('https://www.google.com/')
    True

    >>> is_url('https://site/page')
    False
    """
    return bool(url_pattern.fullmatch(p_url))
