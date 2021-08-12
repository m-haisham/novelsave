import re
from typing import Tuple


class StringHelper:

    url_pattern = re.compile(
        r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)')

    int_pattern = re.compile(r'(\d+)')

    def collect_integers(self, s: str) -> Tuple[int]:
        return tuple(int(n) for n in self.int_pattern.findall(s))

    def clean(self, s: str):
        s = s.replace(' ', ' ')

        return s

    def from_float(self, f: float) -> str:
        return str(f).rstrip('0').rstrip('.')

    def slugify(self, s, replace=''):
        return re.sub(r'[\\/:*"\'<>|.%$^&£?]', replace, s)

    def is_url(self, p_url: str):
        return bool(self.int_pattern.fullmatch(p_url))
