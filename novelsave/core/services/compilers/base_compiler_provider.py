from abc import ABC, abstractmethod
from typing import List, Set

from novelsave.core.services.compilers import BaseCompiler


class BaseCompilerProvider(ABC):

    @abstractmethod
    def keywords(self):
        """all keywords of the supported compilers"""

    @abstractmethod
    def compilers(self) -> Set[BaseCompiler]:
        """return all the compilers"""

    @abstractmethod
    def filter_compilers(self, keywords: List[str]) -> Set[BaseCompiler]:
        """return all compilers with the one of the specified keywords"""

