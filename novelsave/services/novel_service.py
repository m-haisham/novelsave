from typing import Optional

from sqlalchemy.orm import Session

from novelsave.view_models import Novel


class NovelService(object):

    def __main__(self, session: Session):
        self.session = session

    def get_novel_by_id(self, id_: int) -> Optional[Novel]:
        """retrieve a novel from persistence using its id"""

    def get_novel_by_url(self, url: str) -> Optional[Novel]:
        """retrieve a novel from persistence using its url"""

    def upsert_novel(self, novel: Novel):
        """insert or update a novel by id"""

    def delete_novel(self, id_: int):
        """delete a novel by its id"""
