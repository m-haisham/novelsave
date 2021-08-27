import json
from pathlib import Path

from ...core.services.config import BaseConfigService


class ConfigService(BaseConfigService):
    version = 1

    def __init__(self, config_file: Path, default_novel_dir: Path):
        self.data = {'version': self.version, 'config': {}}

        self.config_file = config_file
        self.default_novel_dir = default_novel_dir

        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.load()

    def save(self):
        with self.config_file.open('w') as f:
            json.dump(self.data, f, indent=4)

    def load(self):
        try:
            with self.config_file.open('r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            pass

    @property
    def novel(self) -> dict:
        return self.data['config'].setdefault('novel', {})

    def get_novel_dir(self):
        return self.novel.get('dir', self.default_novel_dir)

    def set_novel_dir(self, path: Path):
        if path.is_file():
            raise NotADirectoryError()

        self.novel['dir'] = str(path)
        self.save()

    def reset_novel_dir(self):
        try:
            del self.novel['dir']
        except KeyError:
            pass

        self.save()
