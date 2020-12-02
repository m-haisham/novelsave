import re

from typing import Tuple

int_pattern = re.compile(r'(\d+)')


class StringTools:
    @staticmethod
    def collect_integers(s: str) -> Tuple[int]:
        return tuple(int(n) for n in int_pattern.findall(s))

    @staticmethod
    def clean(s: str):
        s = s.replace(' ', ' ')

        return s

    @staticmethod
    def from_float(f: float) -> str:
        return str(f).rstrip('0').rstrip('.')

    @staticmethod
    def slugify(s, replace=''):
        return re.sub(r'[\\/:*"\'<>|.%$^&£?]', replace, s)
