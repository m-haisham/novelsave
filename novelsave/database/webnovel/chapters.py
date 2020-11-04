from typing import List

from tinydb import where
from webnovel.models import Chapter as WebnovelChapter

from ..accessors import IAccessor
from ...models import Chapter


class ChaptersAccess(IAccessor):
    _table_name = 'chapters'

    fields = ['index', 'no', 'title', 'paragraphs', 'url']

    def insert(self, obj):
        """
        put object without checking if it already exists

        :param obj: object to be added
        :return: None
        """
        self.table.insert(self._to_dict(obj))

    def put(self, wchapter: WebnovelChapter):
        """
        put chapter with unique identifier chapter.id into database

        :param wchapter: object to be added
        :return: None
        """
        self.table.upsert(self._to_dict(wchapter), where('id') == wchapter.id)

    def put_all(self, wchapters):
        """
        put chapter with unique identifier chapter.id into database

        :param wchapters: object to be added
        :return: None
        """
        docs = [self._to_dict(c) for c in wchapters]
        self.table.insert_multiple(docs)

    def all(self) -> List[Chapter]:
        """
        :return: all chapters
        """
        return [self._from_dict(o) for o in self.table.all()]

    def get(self, id) -> WebnovelChapter:
        """
        :param id: id of chapter
        :return: chapter with corresponding id
        :raises ValueError: if more than one value corresponds to key
        """
        docs = self.table.search(where('id') == id)
        if len(docs) == 1:
            return self._from_dict(docs[0])
        else:
            raise ValueError(f'More than one value with id: {id}')

    def _to_chapter(self, wchapter: WebnovelChapter):
        return Chapter(
            no=wchapter.no,
            title=wchapter.title,
            paragraphs=wchapter.paragraphs,
            url=wchapter.url
        )

    def _to_dict(self, wchapter) -> dict:
        c = self._to_chapter(wchapter)

        return {field: getattr(c, field) for field in ChaptersAccess.fields}

    def _from_dict(self, obj) -> Chapter:
        return Chapter(**{key: value for key, value in obj.items() if key in ChaptersAccess.fields})