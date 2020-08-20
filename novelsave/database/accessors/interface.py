from typing import List

from tinydb import TinyDB, where
from tinydb.table import Document, Table


class IAccessor:
    db: TinyDB
    _table_name: str = None

    def __init__(self, db: TinyDB):
        self.db = db

        if self._table_name is None:
            self._table = None
        else:
            self._table = self.db.table(self._table_name, cache_size=None)

    def where(self, key, value) -> List[Document]:
        """
        search minified
        
        :param key: identifier
        :param value: corresponding value to key
        :return: where the key of document has value provided
        """
        return self.table.search(where(key) == value)

    def truncate(self):
        self.table.truncate()

    @property
    def table_name(self):
        return self._table_name

    @table_name.setter
    def table_name(self, name):
        self._table = self.db.table(name, cache_size=None)
        self._table_name = name

    @property
    def table(self) -> Table:
        return self._table
