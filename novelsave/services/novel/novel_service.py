from pathlib import Path
from typing import Optional, Callable, List, Dict, Tuple

from loguru import logger
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from novelsave.core.dtos import NovelDTO, ChapterDTO, MetaDataDTO, VolumeDTO
from novelsave.core.entities.novel import Novel, NovelUrl, Chapter, Volume, MetaData
from novelsave.core.services import BaseNovelService
from novelsave.services import FileService
from novelsave.utils.adapters import DTOAdapter


class NovelService(BaseNovelService):

    def __init__(
            self,
            session: Session,
            dto_adapter: DTOAdapter,
            file_service: FileService,
    ):
        self.session = session
        self.dto_adapter = dto_adapter
        self.file_service = file_service

    def get_all_novels(self) -> List[Novel]:
        return self.session.execute(select(Novel)).scalars().all()

    def get_novel_by_id(self, id_: int) -> Novel:
        """retrieve a novel from persistence using its id"""
        return self.session.get(Novel, id_)

    def get_novel_by_url(self, url: str) -> Optional[Novel]:
        """retrieve a novel from persistence using its url"""
        return self.session.query(Novel).join(NovelUrl).filter(NovelUrl.url == url).first()

    def get_primary_url(self, novel: Novel) -> str:
        return novel.urls[0].url

    def get_urls(self, novel) -> List[NovelUrl]:
        return novel.urls

    def get_chapters(self, novel: Novel) -> List[Chapter]:
        return self.session.execute(
            select(Chapter).join(Volume).where(Volume.novel_id == novel.id)
        ).scalars().all()

    def get_pending_chapters(self, novel: Novel, limit: int = -1):
        stmt = select(Chapter).join(Volume).where((Chapter.content == None) & (Volume.novel_id == novel.id))
        if limit is not None and limit > 0:
            stmt = stmt.limit(limit)

        return self.session.execute(stmt).scalars().all()

    def get_volumes(self, novel: Novel) -> List[Volume]:
        return novel.volumes

    def get_volumes_with_chapters(self, novel: Novel) -> Dict[Volume, List[Chapter]]:
        volumes = self.session.execute(select(Volume).where(Volume.novel_id == novel.id)).scalars().all()

        return {
            volume: self.session.execute(
                select(Chapter).where((Chapter.content != None) & (Chapter.volume_id == volume.id))
            ).scalars().all()
            for volume in volumes
        }

    def get_metadata(self, novel: Novel) -> List[MetaData]:
        return novel.novel_metadata

    def insert_novel(self, novel_dto: NovelDTO) -> Novel:
        novel, url = self.dto_adapter.novel_from_dto(novel_dto)
        self.session.add(novel)
        self.session.flush()

        url.novel_id = novel.id
        self.session.add(url)
        self.session.commit()

        return novel

    def insert_chapters(
            self,
            novel: Novel,
            volume_dtos: List[VolumeDTO],
            previous: Dict[str, Chapter] = None
    ):
        volume_mapped_chapters = self.dto_adapter.volumes_from_dto(novel, volume_dtos)

        # add volumes
        self.session.add_all(volume_mapped_chapters.keys())
        self.session.flush()

        # add chapters
        for volume, dtos in volume_mapped_chapters.items():
            chapters = [self.dto_adapter.chapter_from_dto(volume, c) for c in dtos]

            # if we have previous chapters with content, use their content path
            if previous is not None:
                for chapter in chapters:
                    chapter.content = previous.get(chapter.url)

            self.session.add_all(chapters)

        self.session.commit()

    def insert_metadata(self, novel: Novel, metadata_dtos: List[MetaDataDTO]):
        metadata = [self.dto_adapter.metadata_from_dto(novel, c) for c in metadata_dtos]
        self.session.add_all(metadata)
        self.session.commit()

    def update_novel(self, novel: Novel, novel_dto: NovelDTO):
        self.dto_adapter.update_novel_from_dto(novel, novel_dto)
        self.session.commit()

    def set_thumbnail_asset(self, novel: Novel, r_path: Path):
        if novel.thumbnail_path == str(r_path):
            return

        novel.thumbnail_path = str(r_path)
        self.session.commit()

    def update_chapters(self, novel: Novel, volume_dtos: List[VolumeDTO]):
        volumes = self.session.execute(select(Volume).where(Volume.novel_id == novel.id)).scalars().all()
        chapters = self.get_chapters(novel)
        volume_mapped_chapters = self.dto_adapter.volumes_from_dto(novel, volume_dtos)

        indexed_volumes = {v.index: v for v in volumes}
        volumes_to_add = []
        for v in list(volume_mapped_chapters.keys()):
            try:
                existing_volume = indexed_volumes.pop(v.index)

                # update names of volumes that already exist
                if existing_volume.name != v.name:
                    logger.debug(f"Updating volume name (index={v.index}, name='{existing_volume.name}' -> '{v.name}')")
                    self.session.execute(update(Volume).where(Volume.id == existing_volume.id).values(name=v.name))

                # index exists so map the chapters into existing volume
                volume_mapped_chapters[existing_volume] = volume_mapped_chapters.pop(v)
            except KeyError:
                volumes_to_add.append(v)

        # add new volume rows that are new
        logger.debug(f"Adding newly found volumes (count={len(volumes_to_add)})")
        self.session.add_all(volumes_to_add)
        self.session.flush()

        # indexed by url which is unique across table
        indexed_chapters = {c.url: c for c in chapters}
        chapters_to_add = []

        # iterate all new chapters
        for volume, chapter_dtos in volume_mapped_chapters.items():
            for chapter_dto in chapter_dtos:
                chapter = self.dto_adapter.chapter_from_dto(volume, chapter_dto)
                try:
                    # existing chapter equivalent
                    ece = indexed_chapters.pop(chapter.url)

                    # update chapters that need to be updated
                    if ece.volume_id != volume.id \
                            or ece.index != chapter.index:
                        logger.debug(f"Updating chapter parent volume (index={ece.index} -> {chapter.index}, "
                                     f"volume_id={ece.volume_id} -> {volume.id})")
                        self.session.execute(
                            update(Chapter)
                                .where(Chapter.url == chapter.url).values(index=chapter.index, volume_id=volume.id)
                        )
                except KeyError:
                    chapters_to_add.append(chapter)

        # add all new chapters
        logger.debug(f"Adding newly found chapters (count={len(chapters_to_add)}).")
        self.session.add_all(chapters_to_add)

        # delete chapters that dont exist anymore
        logger.debug(f"Deleting chapter rows that dont exist anymore (count={len(indexed_chapters)}).")
        for old in indexed_chapters.values():
            self.session.delete(old)

        # delete volumes that dont exist anymore
        logger.debug(f"Deleting volume rows that dont exist anymore (count={len(indexed_volumes)}).")
        for old in indexed_volumes.values():
            self.session.delete(old)

        self.session.commit()

    def update_metadata(self, novel: Novel, metadata_dtos: List[MetaDataDTO]):
        current_metadata = self.get_metadata(novel)
        indexed_metadata: Dict[Tuple, MetaData] = {(data.name, data.value): data for data in current_metadata}

        metadata_to_add = []
        for dto in metadata_dtos:
            this_metadata = self.dto_adapter.metadata_from_dto(novel, dto)

            try:
                current_metadata = indexed_metadata.pop((this_metadata.name, this_metadata.value))
                if current_metadata.others != this_metadata.others:
                    current_metadata.others = this_metadata
                    logger.debug(f"Updating metadata (id={current_metadata.id}, "
                                 f"others={current_metadata.others} -> {this_metadata.others})")

            except KeyError:
                metadata_to_add.append(this_metadata)

        logger.debug(f"Adding newly found metadata (count={len(metadata_to_add)})")
        self.session.add_all(metadata_to_add)

        logger.debug(f"Deleting metadata rows that dont exist anymore (count={len(indexed_metadata)})")
        for metadata in indexed_metadata.values():
            self.session.delete(metadata)

        self.session.commit()

    def update_content(self, chapter_dto: ChapterDTO):
        stmt = update(Chapter).where(Chapter.url == chapter_dto.url).values(content=chapter_dto.content)
        self.session.execute(stmt)
        self.session.commit()

    def add_url(self, novel: Novel, url: str):
        if url in [novel_url.url for novel_url in self.get_urls(novel)]:
            raise ValueError(f"Url already exists in novel (id={novel.id}, title='{novel.title}', {url=}).")

        novel_url = NovelUrl(url=url, novel_id=novel.id)
        self.session.add(novel_url)
        self.session.commit()

    def remove_url(self, novel: Novel, url: str):
        urls = [novel_url.url for novel_url in self.get_urls(novel)]
        if len(urls) <= 1:
            raise ValueError(f"Novel has only one url (id={novel.id}, title='{novel.title}').\n"
                             f"You must add another before this may be removed.")
        if url not in urls:
            raise ValueError(f"Url not in novel (id={novel.id}, title='{novel.title}', {url=}).")

        stmt = delete(NovelUrl).where((NovelUrl.url == url) & (NovelUrl.novel_id == novel.id))
        self.session.execute(stmt)
        self.session.commit()

    def delete_content(self, novel: Novel):
        volumes = [v.id for v in self.get_volumes(novel)]
        stmt = update(Chapter).where(Chapter.volume_id.in_(volumes)).values(content=None)

        self.session.execute(stmt)
        self.session.commit()

    def delete_novel(self, novel: Novel):
        # using session.delete since we want the sqlalchemy cascade to be run
        self.session.delete(novel)
        self.session.commit()

    def delete_volumes(self, novel: Novel):
        # using session.delete since we want the sqlalchemy cascade to be run
        volumes = self.get_volumes(novel)
        for volume in volumes:
            self.session.delete(volume)

        self.session.commit()

    def delete_metadata(self, novel: Novel):
        stmt = delete(MetaData).where(MetaData.novel_id == novel.id)
        self.session.execute(stmt)
        self.session.commit()











