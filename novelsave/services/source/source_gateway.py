from typing import Tuple, List

import browser_cookie3
from loguru import logger
from novelsave_sources.sources.novel.source import Source
from requests.cookies import RequestsCookieJar

from ...core import dtos
from ...core.services.source import BaseSourceGateway
from ...exceptions import CookieBrowserNotSupportedException
from ...utils.adapters import SourceAdapter


class SourceGateway(BaseSourceGateway):
    def __init__(self, source: Source, source_adapter: SourceAdapter):
        self.source = source
        self.source_adapter = source_adapter

    @property
    def name(self) -> str:
        return getattr(self.source, 'name', type(self.source).__name__)

    @property
    def is_search_capable(self) -> bool:
        return self.source.search_viable

    @property
    def is_login_capable(self) -> bool:
        return self.source.login_viable

    def search(self, keyword: str):
        self.source.search(keyword)

    def login(self, username: str, password: str):
        self.source.login(username, password)

    def novel_by_url(self, url: str) -> dtos.NovelDTO:
        novel = self.source.novel(url)

        return self.source_adapter.novel_to_internal(novel)

    def update_chapter_content(self, chapter: dtos.ChapterDTO) -> dtos.ChapterDTO:
        source_chapter = self.source_adapter.chapter_to_external(chapter)
        self.source.chapter(source_chapter)
        self.source_adapter.chapter_content_to_internal(source_chapter, chapter)

        return chapter

    def use_cookies_from_browser(self, browser: str):
        try:
            cookies = getattr(browser_cookie3, browser)()
        except AttributeError:
            raise CookieBrowserNotSupportedException(browser)

        logger.debug(f"Extracted cookies from browser ({browser=}, count={len(cookies)})")

        cookiejar = self.where_cookies_in_domain(cookies)
        self.source.set_cookies(cookiejar)
        logger.debug(
            f"Filtered and set extracted cookies ({browser=}, source='{type(self).__name__}', count={len(cookiejar)})")

    def where_cookies_in_domain(self, cookies):
        cj = RequestsCookieJar()
        for c in cookies:
            if c.domain in self.source.cookie_domains:
                cj.set(c.name, c.values, domain=c.domain, path=c.path)

        return cj
