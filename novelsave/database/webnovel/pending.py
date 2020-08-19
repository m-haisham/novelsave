from typing import List

from tinydb import where

from ..accessors import IAccessor


class PendingAccess(IAccessor):
    _table_name = 'pending'

    FIELD_ID = 'ID'

    def insert(self, id: int, check=True):
        """
        adds id to pending

        :param id: id of chapter
        :param check: do nothing if already exists
        :return: None
        """
        data = self._to_dict(id)
        if check:
            self.table.upsert(data, where(PendingAccess.FIELD_ID) == id)
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

    def remove(self, id):
        """
        removes id from pending

        :param id: id to remove
        :return: None
        """
        self.table.remove(where(PendingAccess.FIELD_ID) == id)

    def all(self) -> List[int]:
        """
        :return: all pending ids
        """
        return [doc[PendingAccess.FIELD_ID] for doc in self.table.all()]

    def _to_dict(self, id) -> dict:
        return {PendingAccess.FIELD_ID: id}
