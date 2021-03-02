from typing import Tuple, List

from bs4 import BeautifulSoup
from webnovel import WebnovelBot
from webnovel.api import ParsedApi
from webnovel.models import Novel as WebnovelNovel
from webnovel.tools import UrlTools

from .source import Source
from ..models import Novel, Chapter


class Webnovel(Source):
    base = 'https://www.webnovel.com'

    def __init__(self):
        super(Webnovel, self).__init__()
        self.api = ParsedApi()

    def login(self, email: str, password: str):
        # init and signin
        webnovel = WebnovelBot(timeout=120)
        webnovel.signin(email, password, manual=True)

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

        content = BeautifulSoup(f'<div>{"".join(wchapter.paragraphs)}</div>', 'lxml')
        self.clean_contents(content)

        return Chapter(
            index=wchapter.id,
            title=title,
            paragraphs=str(content),
            url=url,
        )

    def set_cookies(self, cookies):
        self.session.cookies = cookies
        self.api.session = self.session
        self.api.has_cookies = True

    def novel_folder_name(self, url):
        return f'n{UrlTools.from_novel_url(url)}'
