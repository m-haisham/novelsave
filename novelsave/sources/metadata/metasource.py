from typing import List

import requests
from bs4 import BeautifulSoup

from ..crawler import Crawler
from ...models import MetaData

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/39.0.2171.95 Safari/537.36'}


class MetaSource(Crawler):
    @staticmethod
    def of(value):
        """
        :param value: value to test
        :return: whether the value is from this source
        """
        raise NotImplementedError

    def retrieve(self, url) -> List[MetaData]:
        """
        retrieves metadata from url

        :param url: metadata source
        :return: list of metadata
        """
        raise NotImplementedError