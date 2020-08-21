from typing import List

from tinydb import where

from ..accessors import IAccessor


class SequenceTable(IAccessor):
    def __init__(self, db, table, key='KEY'):
        super(SequenceTable, self).__init__(db)
        self.table_name = table
        self.field_key = key

    def insert(self, value: int, check=True):
        """
        adds id to pending

        :param value: id of chapter
        :param check: do nothing if already exists
        :return: None
        """
        data = self._to_dict(value)
        if check:
            self.table.upsert(data, where(self.field_key) == value)
        else:
            self.table.insert(data)

    def insert_all(self, values: List[int], check=True):
        """
        adds all the values to pending

        more optimized for adding multiple values

        :param values: ids of chapters to add
        :param check: do nothing if already exists
        :return: None
        """
        if check:
            data = [self._to_dict(id) for id in values if id not in self.all()]
        else:
            data = [self._to_dict(id) for id in values]

        self.table.insert_multiple(data)

    def remove(self, value):
        """
        removes value from pending

        :param value: value to remove
        :return: None
        """
        self.table.remove(where(self.field_key) == value)

    def all(self) -> List:
        """
        :return: all values
        """
        return [doc[self.field_key] for doc in self.table.all()]

    def _to_dict(self, value) -> dict:
        return {self.field_key: value}
