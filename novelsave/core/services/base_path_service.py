from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

from novelsave.core.entities.novel import Novel, Asset


class BasePathService(ABC):

    @abstractmethod
    def divide(self, r_path: Path) -> Path:
        """add additional sub folder to the parent depending on the file type"""

    @abstractmethod
    def novel_save_path(self, novel: Novel) -> Path:
        """:return absolute path to novel save directory"""

    @abstractmethod
    def novel_data_path(self, novel: Novel) -> Path:
        """:return absolute path to novel data directory"""

    @abstractmethod
    def asset_path(self, novel: Novel, asset: Asset) -> Path:
        """:return absolute path to the novel specific asset"""

    @abstractmethod
    def thumbnail_path(self, novel: Novel) -> Path:
        """:return absolute path to novel thumbnail file"""

    @abstractmethod
    def resolve_data_path(self, r_path: Union[Path, str]) -> Path:
        """converts relative path to data to absolute path"""

    @abstractmethod
    def relative_to_novel_dir(self, path: Path) -> Path:
        """provide the relative path segment from novels directory"""

    @abstractmethod
    def relative_to_data_dir(self, path: Path) -> Path:
        """provide the relative path segment from data directory"""
