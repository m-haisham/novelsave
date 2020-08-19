from typing import Tuple, List

import requests
from bs4 import BeautifulSoup

from ..models import Novel, Chapter


class Source:

    @staticmethod
    def of(url: str) -> bool:
        """
        :param url: url to test
        :return: whether the url is from source
        """
        raise NotImplementedError

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        """
        soup novel information from url

        :param url: link pointing to novel
        :return: novel and table of content (chapters with only field no, title and url)
        """
        raise NotImplementedError

    def chapter(self, url: str) -> Chapter:
        """
        soup chapter information from url

        :param url: link pointing to chapter
        :return: chapter object
        """
        raise NotImplementedError

    def soup(self, url: str) -> BeautifulSoup:
        response = requests.get(url)
        return BeautifulSoup(response.content, 'lxml')