import json
from pathlib import Path


class ConfigBase:
    def __init__(self, path, name):
        self.path = path / Path(name)
        self.name = name
        self.data = {}

    def save(self):
        with self.path.open('w') as f:
            json.dump(self.data, f)

    def load(self):
        try:
            with self.path.open('r') as f:
                self.data = json.load(f)

        # edit error message
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f'{self.path} - {e.msg}', e.doc, e.pos)

        # treat as empty
        except FileNotFoundError:
            pass
