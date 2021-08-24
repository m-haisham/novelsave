from abc import ABC, abstractmethod
from typing import Dict, List

from novelsave.core.dtos import ChapterDTO
from novelsave.core.entities.novel import Novel, Asset


class BaseAssetService(ABC):

    @abstractmethod
    def update_asset_path(self, asset: Asset):
        """update the file path of the asset"""

    @abstractmethod
    def pending_assets(self, novel: Novel) -> List[Asset]:
        """assets that have not been downloaded"""

    @abstractmethod
    def collect_assets(self, novel: Novel, chapter: ChapterDTO) -> str:
        """collect and modify the provided the html for asset injection"""

    @abstractmethod
    def inject_assets(self, html: str, path_mapping: Dict[int, str]):
        """replace the placeholder links with new link to assets"""
