from typing import Tuple, List

from webnovel import WebnovelBot
from webnovel.api import ParsedApi
from webnovel.models import Novel as WebnovelNovel
from webnovel.tools import UrlTools

from .source import Source
from ..models import Novel, Chapter


class Webnovel(Source):
    base = 'https://www.webnovel.com'
    cookie_domains = [
        '.webnovel.com',
        'www.webnovel.com',
    ]

    @staticmethod
    def of(url: str) -> bool:
        return url.startswith(Webnovel.base)

    def __init__(self):
        super(Webnovel, self).__init__()
        self.api = ParsedApi()

    def login(self, email: str, password: str):
        # init selenium bot
        webnovel = WebnovelBot(timeout=120)

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
            synopsis=wnovel.synopsis,
            thumbnail=wnovel.cover_url,
            url=url,
        )

        toc = self.api.toc(UrlTools.from_novel_url(url))
        chapters = []
        for i, title in enumerate(toc.keys()):
            for wchapter in toc[title]:
                # cant access locked chapters
                if wchapter.locked:
                    continue

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

        if wchapter.no > 0:
            title = f'{wchapter.no} {wchapter.title}'
        else:
            title = wchapter.title

        return Chapter(
            index=wchapter.id,
            title=title,
            paragraphs=wchapter.paragraphs,
            url=url,
        )

    def set_cookiejar(self, cookiejar):
        self.session.cookies = cookiejar
        self.api.session = self.session
        self.api.has_cookies = True

    def novel_folder_name(self, url):
        return f'n{UrlTools.from_novel_url(url)}'
