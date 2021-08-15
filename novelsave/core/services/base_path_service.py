from abc import ABC, abstractmethod
from pathlib import Path

from novelsave.core.entities.novel import Novel


class BasePathService(ABC):

    @abstractmethod
    def divide(self, r_path: Path) -> Path:
        """add additional sub folder to the parent depending on the file type"""

    @abstractmethod
    def get_novel_path(self, novel: Novel) -> Path:
        """:return novel save directory"""

    @abstractmethod
    def get_thumbnail_path(self, novel: Novel) -> Path:
        """:return novel thumbnail path"""

    @abstractmethod
    def resolve_data_path(self, r_path: Path) -> Path:
        """converts relative path to data to absolute path"""

    @abstractmethod
    def relative_to_data_dir(self, path: Path) -> Path:
        """provide the relative path segment from data directory"""
