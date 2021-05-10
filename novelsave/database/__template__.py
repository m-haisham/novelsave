import json
from pathlib import Path
from typing import Optional, Dict


class Database:

    def __init__(self, directory, should_create=True):
        self.path = directory / Path('data')
        self.db_path = self.path / Path('meta.db')
        self.should_create = should_create

        self._data = {}
        self.load_or_create()

    def get_table(self, key: str, default: Optional[Dict] = None):
        return self._data.get(key, default or {})

    def set_table(self, key: str, data: Dict):
        self._data[key] = data

    def save(self):
        with self.db_path.open('w') as f:
            json.dump(self._data, f)

    def load(self):
        with self.db_path.open('r') as f:
            self._data = json.load(f)

    def create(self):
        self.path.mkdir(parents=True, exist_ok=True)
        self.save()

    def load_or_create(self):
        try:
            self.load()
        except FileNotFoundError:
            if self.should_create:
                self.create()
