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

    def search_where(self, key, value):
        docs = []
        data = self.data

        for item in data:
            try:
                if item[key] == value:
                    docs.append(dict(item))
            except KeyError:
                pass

        return docs

    def remove_where(self, key, value):
        data = self.data

        if not data:
            return

        for i in range(len(data) - 1, -1, -1):
            item = data[i]
            try:
                if item[key] == value:
                    del data[i]
            except KeyError:
                pass

        self.save()
