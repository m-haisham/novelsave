import re
from typing import Tuple

url_pattern = re.compile(
    r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)')

int_pattern = re.compile(r'(\d+)')


def collect_integers(s: str) -> Tuple[int]:
    return tuple(int(n) for n in int_pattern.findall(s))


def clean(s: str):
    s = s.replace(' ', ' ')

    return s


def from_float(f: float) -> str:
    return str(f).rstrip('0').rstrip('.')


def slugify(s, replace=''):
    return re.sub(r'[\\/:*"\'<>|.%$^&£?]', replace, s)


def is_url(p_url: str):
    return bool(url_pattern.fullmatch(p_url))
