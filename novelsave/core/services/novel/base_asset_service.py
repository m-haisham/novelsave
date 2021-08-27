from abc import ABC, abstractmethod
from typing import Dict, List

from novelsave.core.dtos import ChapterDTO
from novelsave.core.entities.novel import Novel, Asset


class BaseAssetService(ABC):

    @abstractmethod
    def downloaded_assets(self, novel: Novel) -> List[Asset]:
        """all assets belonging to novel that have been downloaded"""

    @abstractmethod
    def pending_assets(self, novel: Novel) -> List[Asset]:
        """assets that have not been downloaded"""

    @abstractmethod
    def update_asset_path(self, asset: Asset):
        """update the file path of the asset"""

    @abstractmethod
    def delete_assets_of_novel(self, novel: Novel):
        """delete all assets that are associated with from database"""

    @abstractmethod
    def collect_assets(self, novel: Novel, chapter: ChapterDTO) -> str:
        """collect and modify the provided the html for asset injection"""

    @abstractmethod
    def mapping_dict(self, path_mapping: Dict[int, str]):
        """create a mapping dict that can be used by inject assets"""

    @abstractmethod
    def inject_assets(self, html: str, mapping_dict: Dict[int, str]):
        """replace the placeholder links with new link to assets"""
