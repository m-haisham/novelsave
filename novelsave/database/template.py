import json
from pathlib import Path
from typing import Optional, Dict, Union


class DatabaseTemplate:
    def __init__(self, file: Union[str, Path], should_create=True):
        self.file: Path = Path(file)
        self.path: Path = getattr(file, 'parent', '')

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
        file = kwargs.get('file', args[0])

        if file == ':memory:':
            return MemoryDatabase(*args, **kwargs)
        else:
            return FileDatabase(*args, **kwargs)

    def save(self):
        pass

    def load(self):
        pass


class FileDatabase(DatabaseTemplate):
    def __init__(self, file, should_create=True):
        super(FileDatabase, self).__init__(file)
        self._load_or_create(should_create)

    def save(self):
        with self.file.open('w') as f:
            json.dump(self._data, f)

    def load(self):
        with self.file.open('r') as f:
            self._data = json.load(f)

    def _create(self):
        self.path.mkdir(parents=True, exist_ok=True)
        self.save()

    def _load_or_create(self, should_create):
        try:
            self.load()
        except FileNotFoundError:
            if should_create:
                self._create()


class MemoryDatabase(DatabaseTemplate):
    def save(self):
        pass

    def load(self):
        pass
