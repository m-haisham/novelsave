from abc import ABC, abstractmethod
from typing import List, Set

from novelsave.core.services.packagers import BasePackager


class BasePackagerProvider(ABC):

    @abstractmethod
    def keywords(self):
        """all keywords of the supported packagers"""

    @abstractmethod
    def packagers(self) -> Set[BasePackager]:
        """return all the packagers"""

    @abstractmethod
    def filter_packagers(self, keywords: List[str]) -> Set[BasePackager]:
        """return all packagers with the one of the specified keywords"""

