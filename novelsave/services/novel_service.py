from typing import Optional, Callable, List

from sqlalchemy.orm import Session

from novelsave.core.dtos import NovelDTO, ChapterDTO, MetaDataDTO
from novelsave.core.entities.novel import Novel, NovelUrl
from novelsave.utils.adapters import DTOAdapter


class NovelService:

    def __init__(
            self,
            session: Session,
            dto_adapter: DTOAdapter,
    ):
        self.session = session
        self.dto_adapter = dto_adapter

    def get_novel_by_id(self, id_: int) -> Novel:
        """retrieve a novel from persistence using its id"""
        return self.session.get(Novel, id_)

    def get_novel_by_url(self, url: str) -> Optional[Novel]:
        """retrieve a novel from persistence using its url"""
        return self.session.query(Novel).join(NovelUrl).filter(NovelUrl.url == url).first()

    def insert_novel(self, novel_dto: NovelDTO) -> Novel:
        novel, url = self.dto_adapter.novel_from_dto(novel_dto)
        self.session.add(novel)
        self.session.flush()

        url.novel_id = novel.id
        self.session.add(url)
        self.session.commit()

        return novel

    def insert_chapters(self, novel: Novel, chapter_dtos: List[ChapterDTO]):
        volume_mapped_chapters = self.dto_adapter.volumes_from_chapter_dtos(novel, chapter_dtos)

        # add volumes
        self.session.add_all(volume_mapped_chapters.keys())
        self.session.flush()

        # add chapters
        for volume, dtos in volume_mapped_chapters.items():
            chapters = [self.dto_adapter.chapter_from_dto(volume, c) for c in dtos]
            self.session.add_all(chapters)

        self.session.commit()

    def insert_metadata(self, novel: Novel, metadata_dtos: List[MetaDataDTO]):
        metadata = [self.dto_adapter.metadata_from_dto(novel, c) for c in metadata_dtos]
        self.session.add_all(metadata)
        self.session.commit()
