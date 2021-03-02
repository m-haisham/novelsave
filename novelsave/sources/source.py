import re
import time
from typing import Tuple, List, Iterable, Union
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, Comment
from requests.cookies import RequestsCookieJar

from ..models import Novel, Chapter
from ..tools import StringTools
from ..exceptions import ResponseException

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/39.0.2171.95 Safari/537.36'}


class Source:
    base: str
    retry_count = 5
    cookie_domains = []

    @classmethod
    def of(cls, url: str) -> bool:
        """
        :param url: url to test
        :return: whether the url is from this source
        """
        return url.startswith(cls.base)

    def __init__(self):
        # public
        self.session = requests.Session()
        self.headers = header

        # set default cookie domains
        if not self.cookie_domains:
            netloc = urlparse(self.base).netloc
            self.cookie_domains = [
                netloc,
                re.search(r'.+?(\..+)', netloc).group(1),  # remove the segment before first dot
            ]

        # private
        self._soup_cache = {}

    def login(self, email: str, password: str):
        """
        Login to the source and assign the required cookies

        :param email: email or username
        :param password: credential key
        :return: None
        """
        raise NotImplementedError

    def set_cookies(self, cookies: Union[RequestsCookieJar, Tuple[dict]]):
        """
        Replaces current cookiejar with given cookies

        :param cookies: new cookiejar
        """
        if type(cookies) == RequestsCookieJar:
            self.session.cookies = cookies
        if type(cookies) == tuple:
            # clear preexisting cookies associated with source
            for domain in self.cookie_domains:
                self.session.cookies.clear(domain=domain)

            # add the dict formatted cookies
            for cookie in cookies:
                self.session.cookies.set(**cookie)
        else:
            raise TypeError(f"Unexpected type received: {type(cookies)}; Require either 'RequestsCookieJar' or 'Tuple[dict]'")

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:
        """
        soup novel information from url

        :param url: link pointing to novel
        :return: novel, table of content (chapters with only field no, title and url), and volumes
        """
        raise NotImplementedError

    def chapter(self, url: str) -> Chapter:
        """
        soup chapter information from url

        :param url: link pointing to chapter
        :return: chapter object
        """
        raise NotImplementedError

    # ---- Helper methods ----
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
        elif response.status_code == 429:  # too many requests
            try:
                retry_timeout = float(response.headers['Retry-After']) / 1000.0
            except KeyError:
                # default timeout
                retry_timeout = 1

            time.sleep(retry_timeout)
            return self.request_get(url, _tries + 1)

        raise ResponseException(response, f'{response.status_code}: {response.url}')

    def source_folder_name(self):
        """
        :return: suitable folder name from netloc
        """
        return StringTools.slugify(urlparse(self.base).netloc, replace='_')

    def novel_folder_name(self, url):
        """
        :param url: novel url
        :return: suitable novel folder name
        """
        return StringTools.slugify(url.strip('/ ').split('/')[-1])

    # ---- Inspired from https://github.com/dipu-bd/lightnovel-crawler ----
    # ----      And almost a perfect copy of the functions below       ----

    bad_tags = [
        'noscript', 'script', 'iframe', 'form', 'hr', 'img', 'ins',
        'button', 'input', 'amp-auto-ads', 'pirate'
    ]

    blacklist_patterns = [
        r'^[\W\D]*(volume|chapter)[\W\D]+\d+[\W\D]*$',
    ]

    def is_blacklisted(self, text):
        """
        :return: whether the text is black listed
        """
        for pattern in self.blacklist_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def clean_contents(self, contents):
        if not contents:
            return contents

        contents.attrs = {}
        for element in contents.find_all(True):
            # remove comments
            if isinstance(element, Comment):
                element.extract()

            elif element.name == 'br':
                next_element = getattr(element, 'next_sibling')
                if next_element and next_element.name == 'br':
                    element.extract()

            # Remove bad tags
            elif element.name in self.bad_tags:
                element.extract()

            # Remove empty elements
            elif not element.text.strip():
                element.extract()

            # Remove blacklisted elements
            elif self.is_blacklisted(element.text):
                element.extract()

            # Remove attributes
            elif hasattr(element, 'attrs'):
                element.attrs = {}

        return contents
