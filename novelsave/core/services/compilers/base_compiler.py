from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple

from novelsave.core.entities.novel import Novel


class BaseCompiler(ABC):

    @abstractmethod
    def keywords(self) -> Tuple[str]:
        """keywords that identify this compiler. for example, output format"""

    @abstractmethod
    def compile(self, novel: Novel) -> Path:
        """compile the a select novel from the database into another format."""

    @abstractmethod
    def destination(self, novel: Novel) -> Path:
        """provide file or directory where the novel has been compiled to, file is preferred."""
