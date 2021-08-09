from typing import Optional, Callable

from sqlalchemy.orm import Session

from novelsave.core.dtos import NovelDTO
from novelsave.core.entities.novel import Novel, NovelUrl
from novelsave.utils.adapters import DTOAdapter


class NovelService:

    def __init__(
            self,
            session_builder: Callable[[], Session],
            dto_adapter: DTOAdapter,
    ):
        self.session_builder = session_builder
        self.dto_adapter = dto_adapter

    def get_novel_by_id(self, id_: int) -> Novel:
        """retrieve a novel from persistence using its id"""
        with self.session_builder() as session:
            return session.get(Novel, id_)

    def get_novel_by_url(self, url: str) -> Optional[Novel]:
        """retrieve a novel from persistence using its url"""
        with self.session_builder() as session:
            return session.query(Novel).join(NovelUrl).filter(NovelUrl.url == url).first()

    def insert_novel(self, novel_dto: NovelDTO) -> Novel:
        with self.session_builder() as session:
            novel, url = self.dto_adapter.novel_from_dto(novel_dto)
            session.add(novel)
            session.flush()

            url.novel_id = novel.id
            session.add(url)

        return novel
