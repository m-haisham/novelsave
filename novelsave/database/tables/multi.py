from typing import List

from tinydb import where

from ..accessors import IAccessor
from ...models import Chapter


class MultiClassTable(IAccessor):
    def __init__(self, db, table: str, cls, fields: List[str], identifier: str):
        super(MultiClassTable, self).__init__(db)
        self.table_name = table

        # error checks
        if identifier not in fields:
            raise ValueError("'identifier' must be a field")
        if not fields:
            raise ValueError("'fields' must not be empty")

        self.cls = cls
        self.fields = fields
        self.identifier = identifier

    def insert(self, obj):
        """
        put object without checking if it already exists

        :param obj: object to be added
        :return: None
        """
        self.table.insert(self._to_dict(obj))

    def put(self, obj):
        """
        put object with unique identifier chapter.id into database

        :param obj: object to be added
        :return: None
        """
        self.table.upsert(self._to_dict(obj), where(self.identifier) == getattr(obj, self.identifier))

    def put_all(self, objs: List):
        """
        put obj with unique identifier into database

        :param objs: object to be added
        :return: None
        """
        docs = [self._to_dict(c) for c in objs]
        self.table.insert_multiple(docs)

    def all(self) -> List:
        """
        :return: all objects
        """
        return [self._from_dict(o) for o in self.table.all()]

    def get(self, id) -> Chapter:
        """
        :param id: unique identifier
        :return: chapter with corresponding id
        :raises ValueError: if more than one value corresponds to key
        """
        docs = self.table.search(where('id') == id)
        if len(docs) == 1:
            return self._from_dict(docs[0])
        else:
            raise ValueError(f'More than one value with id: {id}')

    def remove(self, value):
        """
        removes value from pending

        :param value: value to remove
        :return: None
        """
        self.table.remove(where(self.identifier) == value)

    def _to_dict(self, obj) -> dict:
        return {field: getattr(obj, field) for field in self.fields}

    def _from_dict(self, doc) -> Chapter:
        return self.cls(**{key: value for key, value in doc.items() if key in self.fields})
