from typing import List

from .template import Table


class SetTable(Table):
    def __init__(self, db, table, fields):
        super(SetTable, self).__init__(db, table, lambda: [])

        self.fields = fields

    def put(self, obj: dict):
        # test object for needed fields
        for field in self.fields:
            obj[field]

        data = self.data

        for i, item in enumerate(data):
            if all([obj[field] == item[field] for field in self.fields]):
                del data[i]

        data.append(obj)
        self.save()

    def all(self) -> List[dict]:
        return self.data

    def remove(self, obj):
        data = self.data

        for i, item in enumerate(data):
            if all([obj[field] == item[field] for field in self.fields]):
                del data[i]

        self.save()
