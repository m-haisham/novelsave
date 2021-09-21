from functools import lru_cache
from typing import List

from novelsave.core.entities.novel import Novel
from novelsave.core.services import BaseCalibreService, BasePathService
from .calibre_packager import CalibrePackager


class MobiPackager(CalibrePackager):

    def keywords(self) -> List[str]:
        return ['mobi']

    @property
    def args(self) -> List[str]:
        return []

    @property
    def ext(self) -> str:
        return '.mobi'
