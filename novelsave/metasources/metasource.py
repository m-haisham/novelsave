from typing import List

import requests
from bs4 import BeautifulSoup

from ..models import MetaData

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/39.0.2171.95 Safari/537.36'}

class MetaSource:
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

    def soup(self, url):
        response = requests.get(url, headers=header)
        return BeautifulSoup(self._verify_response(response).content, 'lxml')

    def _verify_response(self, response):
        if response.status_code == 200:
            return response
        else:
            raise Exception(f'{response.status_code}: {response.url}')