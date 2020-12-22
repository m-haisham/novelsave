from typing import List

from tinydb import where

from ..accessors import IAccessor


class SetTable(IAccessor):
    def __init__(self, db, table, field1, field2):
        super(SetTable, self).__init__(db)
        self.table_name = table
        self.field1 = field1
        self.field2 = field2

    def put(self, obj: dict):
        self.table.upsert(
            obj,
            (where(self.field1) == obj[self.field1])
            & (where(self.field2) == obj[self.field2])
        )

    def all(self) -> List[dict]:
        return self.table.all()

    def remove(self, value1, value2):
        self.table.remove(
            (where(self.field1) == value1)
            & (where(self.field2) == value2)
        )
