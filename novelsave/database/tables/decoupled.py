from pathlib import Path
from typing import List, TypeVar

from tinydb import TinyDB

from .multi import MultiClassTable
from ..accessors import IAccessor
from ...tools import unzip_arguments

T = TypeVar('T')


class Decoupled:
    """
    moves the data to a new database file
    database variant to be applied for when the data is highly variable
    """

    def __init__(self, path: Path, table: IAccessor):
        pass

    def __new__(cls, *args, **kwargs) -> IAccessor:
        path, table = unzip_arguments(args, kwargs, ((0, 'path'), (1, 'table')))

        # create a new database
        db = TinyDB(path / Path(f'{table.table_name}.db'))

        # get table from database
        table._table = db.table(table.table_name)
        table.decoupled = db

        return table


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
