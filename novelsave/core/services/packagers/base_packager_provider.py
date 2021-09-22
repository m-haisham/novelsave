from abc import ABC, abstractmethod
from typing import List, Set, Iterable

from novelsave.core.services.packagers import BasePackager


class BasePackagerProvider(ABC):

    @abstractmethod
    def keywords(self):
        """all keywords of the supported packagers"""

    @abstractmethod
    def packagers(self) -> Iterable[BasePackager]:
        """return all the packagers"""

    @abstractmethod
    def filter_packagers(self, keywords: Iterable[str]) -> Iterable[BasePackager]:
        """return all packagers with the one of the specified keywords

        :raises ValueError: if a keyword does not match any packagers
        """

