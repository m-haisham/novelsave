from abc import ABC, abstractmethod
from pathlib import Path

from novelsave.core.entities.novel import Novel


class BasePathService(ABC):

    @abstractmethod
    def get_novel_path(self, novel: Novel) -> Path:
        """:return novel save directory"""

    @abstractmethod
    def get_thumbnail_path(self, novel: Novel) -> Path:
        """:return novel thumbnail path"""

    @abstractmethod
    def relative_to_data_dir(self, path: Path) -> Path:
        """provide the relative path segment from data directory"""
