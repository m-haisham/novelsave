from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session, Query

from novelsave.core.entities import novel as novel_entities
from novelsave.view_models import Novel, Chapter


class NovelService(object):

    def __main__(self, session: Session):
        self.session = session

    def get_novel_by_id(self, id_: int) -> Optional[Novel]:
        """retrieve a novel from persistence using its id"""
        return self.session.get(novel_entities.Novel, id_)

    def get_novel_by_url(self, url: str) -> Optional[Novel]:
        """retrieve a novel from persistence using its url"""
        entity = self.session.query(novel_entities.NovelUrl, url=url).first()
        if entity is None:
            return None



    def upsert_novel(self, novel: Novel):
        """insert or update a novel by id"""

    def delete_novel(self, novel: Novel):
        """delete a novel by its id"""

    def save_thumbnail(self, novel: Novel, exists_ok=False) -> Path:
        """
        download and save the thumbnail image to file and return the file path

        :param novel: novel whose thumbnail to save
        :param exists_ok: return the file path without overriding
        """

    def save_chapter_content(self, chapter: Chapter) -> Path:
        """saves the chapter content into a file and updates the database to point to the file"""
