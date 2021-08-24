from abc import ABC, abstractmethod
from typing import Dict

from novelsave.core.dtos import ChapterDTO
from novelsave.core.entities.novel import Novel


class BaseAssetService(ABC):

    @abstractmethod
    def collect_assets(self, novel: Novel, chapter: ChapterDTO) -> str:
        """collect and modify the provided the html for asset injection"""

    @abstractmethod
    def inject_assets(self, html: str, path_mapping: Dict[int, str]):
        """replace the placeholder links with new link to assets"""
