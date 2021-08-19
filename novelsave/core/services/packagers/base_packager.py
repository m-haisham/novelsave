from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple

from novelsave.core.entities.novel import Novel


class BasePackager(ABC):

    @abstractmethod
    def keywords(self) -> Tuple[str]:
        """keywords that identify this packager. for example, output format"""

    @abstractmethod
    def package(self, novel: Novel) -> Path:
        """package the a select novel from the database into another format."""

    @abstractmethod
    def destination(self, novel: Novel) -> Path:
        """provide file or directory where the novel has been packaged to, file is preferred."""
