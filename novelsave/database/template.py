import json
from pathlib import Path
from typing import Optional, Dict


class DatabaseTemplate:
    def __init__(self, path, should_create=True):
        self.path = path / Path('data')
        self.db_path = self.path / Path('meta.db')
        self.should_create = should_create

        self._data = {}

    def get_table(self, key: str):
        return self._data[key]

    def set_table(self, key: str, data: Dict):
        self._data[key] = data

    def save(self):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError


class Database(DatabaseTemplate):
    def __new__(cls, *args, **kwargs):
        path = kwargs.get('path', args[0])

        if path == ':memory:':
            return MemoryDatabase(*args, **kwargs)
        else:
            return FileDatabase(*args, **kwargs)

    def save(self):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError


class FileDatabase(DatabaseTemplate):
    def __init__(self, path, should_create=True):
        super(FileDatabase, self).__init__(path, should_create)
        self._load_or_create()

    def save(self):
        with self.db_path.open('w') as f:
            json.dump(self._data, f)

    def load(self):
        with self.db_path.open('r') as f:
            self._data = json.load(f)

    def _create(self):
        self.path.mkdir(parents=True, exist_ok=True)
        self.save()

    def _load_or_create(self):
        try:
            self.load()
        except FileNotFoundError:
            if self.should_create:
                self._create()


class MemoryDatabase(DatabaseTemplate):
    def save(self):
        pass

    def load(self):
        pass
