from abc import ABC, abstractmethod
from typing import Tuple

from novelsave.core.entities.novel import Novel


class BaseCompiler(ABC):

    @abstractmethod
    def keywords(self) -> Tuple[str]:
        """keywords that identify this compiler. for example, output format"""

    @abstractmethod
    def compile(self, novel: Novel):
        """compile the a select novel from the database into another format."""
