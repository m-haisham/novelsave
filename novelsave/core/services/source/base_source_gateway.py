from abc import ABC, abstractmethod
from typing import List, Tuple

from novelsave.core import dtos


class BaseSourceGateway(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        """name of the corresponding source"""

    @property
    @abstractmethod
    def is_search_capable(self) -> bool:
        """identifies whether the source provides search capability"""

    @property
    @abstractmethod
    def is_login_capable(self) -> bool:
        """identifies whether the source provides login capability"""

    @abstractmethod
    def search(self, keyword: str) -> List[dtos.NovelDTO]:
        """search the source library for novels with keyword"""

    @abstractmethod
    def login(self, username: str, password: str):
        """login to the source website, making available services or novels which might otherwise be absent"""

    @abstractmethod
    def novel_by_url(self, url: str) -> dtos.NovelDTO:
        """scrape and parse a novel by its url"""

    @abstractmethod
    def update_chapter_content(self, chapter: dtos.ChapterDTO) -> dtos.ChapterDTO:
        """update a chapter's content by following its url"""

    @abstractmethod
    def use_cookies_from_browser(self, browser: str):
        """take the cookies from the browser and add them to following requests"""
