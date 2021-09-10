from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List, Dict

from novelsave.core.dtos import NovelDTO, ChapterDTO, MetaDataDTO, VolumeDTO
from novelsave.core.entities.novel import Novel, Chapter, Volume, MetaData, NovelUrl


class BaseNovelService(ABC):

    @abstractmethod
    def get_all_novels(self) -> List[Novel]:
        """retrieve all the novels in the database"""

    @abstractmethod
    def get_novel_by_id(self, id_: int) -> Optional[Novel]:
        """retrieve novel by its id, assuming it exists, otherwise return none"""

    @abstractmethod
    def get_novel_by_url(self, url: str) -> Optional[Novel]:
        """retrieve novel by url, if novel doesn't exist return none"""

    @abstractmethod
    def get_primary_url(self, novel: Novel) -> str:
        """retrieve the primary url corresponding to the novel"""

    @abstractmethod
    def get_urls(self, novel) -> List[NovelUrl]:
        """retrieve all the urls of novel"""

    @abstractmethod
    def get_chapters(self, novel: Novel) -> List[Chapter]:
        """retrieve all chapters of the novel"""

    @abstractmethod
    def get_pending_chapters(self, novel: Novel, limit: int) -> List[Chapter]:
        """retrieve all pending chapters of the novel. a chapter is assumed to be pending if it has no content."""

    @abstractmethod
    def get_volumes(self, novel: Novel) -> List[Volume]:
        """retrieve all the volumes of the novel"""

    @abstractmethod
    def get_volumes_with_chapters(self, novel: Novel) -> Dict[Volume, List[Chapter]]:
        """retrieve all volumes along with their corresponding chapters that have content"""

    @abstractmethod
    def get_metadata(self, novel: Novel) -> List[MetaData]:
        """retrieve all metadata of novel"""

    @abstractmethod
    def insert_novel(self, novel_dto: NovelDTO) -> Novel:
        """insert a new novel into the database"""

    @abstractmethod
    def insert_chapters(self, novel: Novel, volume_dtos: List[VolumeDTO]):
        """insert new chapters into the database as well as their volumes"""

    @abstractmethod
    def insert_metadata(self, novel: Novel, metadata_dtos: List[MetaDataDTO]):
        """insert new metadata into the database"""

    @abstractmethod
    def set_thumbnail_asset(self, novel: Novel, r_path: Path):
        """update the cover asset path of the novel"""

    @abstractmethod
    def update_novel(self, novel: Novel, novel_dto: NovelDTO):
        """update existing novel with newer values"""

    @abstractmethod
    def update_chapters(self, novel: Novel, volume_dtos: List[VolumeDTO]):
        """update and replace existing novel chapters and their corresponding volumes"""

    @abstractmethod
    def update_metadata(self, novel: Novel, metadata_dtos: List[MetaDataDTO]):
        """update and replace existing metadata"""

    @abstractmethod
    def update_content(self, chapter_dto: ChapterDTO):
        """update an existing chapter's content"""

    @abstractmethod
    def add_url(self, novel: Novel, url: str):
        """add the specified url to the database linked to novel"""

    @abstractmethod
    def remove_url(self, novel: Novel, url: str):
        """removes the specified url from the database"""

    @abstractmethod
    def delete_content(self, novel: Novel):
        """deletes all the chapters contents"""

    @abstractmethod
    def delete_novel(self, novel: Novel):
        """delete novel including chapters and assets"""

    @abstractmethod
    def delete_volumes(self, novel: Novel):
        """delete volumes associated with novel as well as the chapters linked to them"""

    @abstractmethod
    def delete_metadata(self, novel: Novel):
        """delete all the metadata associated with novel"""
