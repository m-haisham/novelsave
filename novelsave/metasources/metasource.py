import requests
from bs4 import BeautifulSoup
from typing import List

from ..models import MetaData


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
        response = requests.get(url)
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'lxml')
        else:
            raise Exception(f'{response.status_code}: {response.url}')
