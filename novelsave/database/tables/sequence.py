from tinydb import where
from typing import List

from ..accessors import IAccessor


class SequenceTable(IAccessor):
    FIELD_KEY = 'KEY'

    def __init__(self, db, table):
        super(SequenceTable, self).__init__(db)
        self.table_name = table

    def insert(self, id: int, check=True):
        """
        adds id to pending

        :param id: id of chapter
        :param check: do nothing if already exists
        :return: None
        """
        data = self._to_dict(id)
        if check:
            self.table.upsert(data, where(SequenceTable.FIELD_KEY) == id)
        else:
            self.table.insert(data)

    def insert_all(self, ids: List[int], check=True):
        """
        adds all the ids to pending

        more optimized for adding multiple ids

        :param ids: ids of chapters to add
        :param check: do nothing if already exists
        :return: None
        """
        if check:
            data = [self._to_dict(id) for id in ids if id not in self.all()]
        else:
            data = [self._to_dict(id) for id in ids]

        self.table.insert_multiple(data)

    def remove(self, value):
        """
        removes id from pending

        :param id: id to remove
        :return: None
        """
        self.table.remove(where(SequenceTable.FIELD_KEY) == id)

    def all(self) -> List:
        """
        :return: all pending ids
        """
        return [doc[SequenceTable.FIELD_KEY] for doc in self.table.all()]

    def _to_dict(self, value) -> dict:
        return {SequenceTable.FIELD_KEY: value}