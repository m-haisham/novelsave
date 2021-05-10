from pathlib import Path
from typing import List, TypeVar

from .multi import MultiClassTable
from ..template import Database

T = TypeVar('T')


class MultiClassDecoupledTable(MultiClassTable):
    """
    MultiClass database variant to be used for when the data is highly variable
    """

    def __init__(self, db, path: Path, table: str, cls: T, fields: List[str], identifier: str):
        super(MultiClassDecoupledTable, self).__init__(db, table, cls, fields, identifier)

        # create new db file
        self.file = path / Path(f'{table}.db')
        self.db = Database(self.file, should_create=True)
