import requests
from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar

from ..exceptions import ResponseException

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/39.0.2171.95 Safari/537.36'}


class Crawler:
    retry_count = 5

    def __init__(self):
        self.session = requests.Session()

        self._soup_cache = {}


    def set_cookies(self, cookies: RequestsCookieJar):
        self.session.cookies = cookies

    def soup(self, url: str) -> BeautifulSoup:
        """
        Download website html and create a bs4 object

        :param url: website to be downloaded
        :return: created bs4 object
        """
        response = self.request_get(url)
        return BeautifulSoup(response.content, 'lxml')

    def cached_soup(self, url):
        """
        either return the cache response or
        if there is no cache, download anew

        :param url: website to be downloaded
        :return: created bs4 object
        """
        try:
            # get response from cache
            response = self._soup_cache[url]
        except KeyError:
            # make a new request and cache the result
            response = self.request_get(url)
            self._soup_cache[url] = response

        return BeautifulSoup(response.content, 'lxml')

    def request_get(self, url, _tries=0):
        # limiting retry requests
        if _tries >= self.retry_count:
            return

        # request
        response = self.session.get(url, headers=header)
        if response.status_code == 200:  # ok
            return response

        # retry can take a lot of time, this is suspended until a better solution is found
        # elif response.status_code == 429:  # too many requests
        #     try:
        #         retry_timeout = float(response.headers['Retry-After']) / 1000.0
        #     except KeyError:
        #         # default timeout
        #         retry_timeout = 1
        #
        #     time.sleep(retry_timeout)
        #     return self.request_get(url, _tries + 1)

        raise ResponseException(response, f'{response.status_code}: {response.url}')
