import re

from .source import Source


class Webnovel(Source):
    url_pattern = re.compile(r'https://www\.webnovel\.com')

    @staticmethod
    def of(url: str) -> bool:
        return bool(Webnovel.url_pattern.match(url))