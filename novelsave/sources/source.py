from typing import Tuple, List

import requests
from bs4 import BeautifulSoup

from ..models import Novel, Chapter

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/39.0.2171.95 Safari/537.36'}


class Source:
    base: str

    @staticmethod
    def of(url: str) -> bool:
        """
        :param url: url to test
        :return: whether the url is from this source
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
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'lxml')
        else:
            raise Exception(f'{response.status_code}: {url}')
