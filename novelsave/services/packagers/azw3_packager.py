from typing import List

from .calibre_packager import CalibrePackager


class Azw3Packager(CalibrePackager):
    def keywords(self) -> List[str]:
        return ['azw3']

    @property
    def args(self) -> List[str]:
        return []

    @property
    def ext(self) -> str:
        return '.azw3'
