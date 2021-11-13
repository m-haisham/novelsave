import functools
import json
from pathlib import Path
from typing import Dict

from ...core.services.config import BaseConfigService


def ensure_key_exists(func):
    """Decorator that checks if the provided key is valid"""

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        self, key = args[0], kwargs.get("key", args[1])
        if key not in self._defaults:
            raise KeyError(f"The specified key is not in configurations: '{key}'")

        return func(*args, **kwargs)

    return wrapped


class ConfigService(BaseConfigService):
    version = 2

    def __init__(self, config_file: Path, default_novel_dir: Path):
        self.data = {"version": self.version, "config": {}}

        self._defaults = {
            "novel.dir": str(default_novel_dir),
        }

        self.config_file = config_file
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.load()

    def save(self):
        with self.config_file.open("w") as f:
            json.dump(self.data, f, indent=4)

    def load(self):
        try:
            with self.config_file.open("r") as f:
                self.data = json.load(f)

            self.data["version"] = self.version
        except FileNotFoundError:
            pass

    @property
    def config(self) -> dict:
        return self.data.setdefault("config", {})

    def get_all_configs(self) -> Dict:
        config = self._defaults.copy()
        for key in config:
            try:
                config[key] = self.config[key]
            except KeyError:
                pass

        return config

    @ensure_key_exists
    def set_config(self, key: str, value: object):
        self.config[key] = value
        self.save()

    @ensure_key_exists
    def get_config(self, key: str) -> object:
        return self.config.get(key, self._defaults[key])

    @ensure_key_exists
    def reset_config(self, key: str):
        del self.config[key]
        self.save()
