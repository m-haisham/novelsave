import re

from typing import Tuple

int_pattern = re.compile(r'(\d+)')


class StringTools:
    @staticmethod
    def startswith(s: str, w: str) -> bool:
        return s[:len(w)] == w

    @staticmethod
    def collect_integers(s: str) -> Tuple[int]:
        return tuple(int(n) for n in int_pattern.findall(s))
