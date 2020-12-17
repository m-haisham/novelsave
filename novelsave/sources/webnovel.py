import re

from typing import Tuple, List

from .source import Source

from webnovel.bot import BASE_URL
from webnovel import WebnovelBot
from webnovel.api import ParsedApi
from webnovel.models import Novel as WebnovelNovel
from webnovel.tools import UrlTools

from ..models import Novel, Chapter


class Webnovel(Source):
    base = 'https://www.webnovel.com'
    url_pattern = re.compile(r'https://www\.webnovel\.com')

    @staticmethod
    def of(url: str) -> bool:
        return bool(Webnovel.url_pattern.match(url))

    def __init__(self):
        super(Webnovel, self).__init__()
        self.api = ParsedApi()

    def login(self, email: str, password: str):
        # init selenium bot
        webnovel = WebnovelBot(timeout=120)
        webnovel.driver.get(BASE_URL)

        # signin
        webnovel.signin(email, password)

        # recreate api
        self.api = webnovel.create_api()

    def novel(self, url: str) -> Tuple[Novel, List[Chapter]]:

        wnovel = WebnovelNovel.from_url(
            # reformatting url so that id retraction works
            UrlTools.to_novel_url(UrlTools.from_novel_url(url))
        )
        novel = Novel(
            title=wnovel.title,
            author=wnovel.author,
            thumbnail=wnovel.cover_url,
            url=url,
        )

        toc = self.api.toc(UrlTools.from_novel_url(url))
        chapters = []
        for i, title in enumerate(toc.keys()):
            for wchapter in toc[title]:

                # translate from Webnovel.Chapter to Chapter
                chapter = Chapter(
                    index=wchapter.id,
                    title=wchapter.title,
                    volume=(i, title),
                    url=wchapter.url,
                )

                chapters.append(chapter)

        return novel, chapters

    def chapter(self, url: str) -> Chapter:
        wchapter = self.api.chapter(*UrlTools.from_chapter_url(url))
        return Chapter(
            index=wchapter.id,
            title=wchapter.title,
            paragraphs=wchapter.paragraphs,
            url=url,
        )

    def novel_folder_name(self, url):
        return f'n{UrlTools.from_novel_url(url)}'
