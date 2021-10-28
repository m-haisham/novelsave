from typing import List

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
