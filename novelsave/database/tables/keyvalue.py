from .template import Table


class KeyValueTable(Table):
    def __init__(self, db, table):
        super(KeyValueTable, self).__init__(db, table)

    def put(self, key, value):
        self.data[key] = value
        self.flush()

    def get(self, key, default=None):
        return self.data.get(key, default)

    def remove(self, key):
        try:
            del self.data[key]
        except KeyError:
            pass

    def all(self):
        return dict(self.data)
