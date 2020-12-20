from typing import List, TypeVar

from tinydb import TinyDB

from .multi import MultiClassTable

T = TypeVar('T')


class MultiClassDecoupledTable(MultiClassTable):
    """
    MultiClass database variant to be used for when the data is highly variable
    """
    def __init__(self, db, path, table: str, cls: T, fields: List[str], identifier: str):
        super(MultiClassDecoupledTable, self).__init__(db, table, cls, fields, identifier)

        # create new db file
        self.path = path / f'{table}.db'
        self.decoupled_db = TinyDB(self.path)

        # reset table path to new file
        self._table = self.decoupled_db.table(table)
