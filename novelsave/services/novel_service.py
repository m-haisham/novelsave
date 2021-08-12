from typing import Optional, Callable, List, Dict

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from novelsave.core.dtos import NovelDTO, ChapterDTO, MetaDataDTO
from novelsave.core.entities.novel import Novel, NovelUrl, Chapter, Volume, MetaData
from novelsave.services import FileService
from novelsave.utils.adapters import DTOAdapter


class NovelService:

    def __init__(
            self,
            session: Session,
            dto_adapter: DTOAdapter,
            file_service: FileService,
    ):
        self.session = session
        self.dto_adapter = dto_adapter
        self.file_service = file_service

    def get_novel_by_id(self, id_: int) -> Novel:
        """retrieve a novel from persistence using its id"""
        return self.session.get(Novel, id_)

    def get_novel_by_url(self, url: str) -> Optional[Novel]:
        """retrieve a novel from persistence using its url"""
        return self.session.query(Novel).join(NovelUrl).filter(NovelUrl.url == url).first()

    def get_url(self, novel: Novel) -> str:
        return novel.urls[0].url

    def get_all_chapters(self, novel: Novel) -> List[Chapter]:
        return self.session.execute(
            select(Chapter).join(Volume).where(Volume.novel_id == novel.id)
        ).all()

    def get_pending_chapters(self, novel: Novel, limit: int = -1):
        stmt = select(Chapter).join(Volume).where((Chapter.content == None) & (Volume.novel_id == novel.id))
        if limit > 0:
            stmt = stmt.limit(limit)

        return self.session.execute(stmt).scalars().all()

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
            chapter_dtos: List[ChapterDTO],
            previous: Dict[str, Chapter] = None
    ):
        volume_mapped_chapters = self.dto_adapter.volumes_from_chapter_dtos(novel, chapter_dtos)

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

    def update_chapters(self, novel: Novel, chapter_dtos: List[ChapterDTO]):
        stmt = select(Chapter).join(Volume).where((Chapter.content != None) & (Volume.novel_id == novel.id))
        url_mapped_chapters = {c.url: c for c in self.session.execute(stmt).all()}

        # delete current chapters
        self.session.execute(delete(Volume).where(Volume.novel_id == novel.id))
        self.session.commit()

        # insert new chapters
        self.insert_chapters(novel, chapter_dtos, url_mapped_chapters)

    def update_metadata(self, novel: Novel, metadata_dtos: List[MetaDataDTO]):
        # delete existing
        self.session.execute(delete(MetaData).where(MetaData.novel_id == novel.id))

        # add new
        self.insert_metadata(novel, metadata_dtos)

    def update_content(self, chapter_dto: ChapterDTO):
        stmt = update(Chapter).where(Chapter.url == chapter_dto.url).values(content=chapter_dto.content)
        self.session.execute(stmt)
        self.session.commit()
