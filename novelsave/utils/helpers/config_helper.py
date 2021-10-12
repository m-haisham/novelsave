import json
from pathlib import Path

from ...settings import CONFIG_FILE


def _version_1(data: dict):
    config = data.get('config', {})

    try:
        config['novel']['dir'] = Path(config['novel']['dir'])
    except KeyError:
        pass

    return config


def _version_2(data: dict):
    config = data.get('config', {})

    types = {
        'novel.dir': Path,
    }

    parsed = {}

    for key, value in config.items():
        try:
            value = types[key](value)
        except KeyError:
            pass

        parent = parsed
        for segment in key.split('.')[:-1]:
            parent = parent.setdefault(segment, {})

        parent[key.split('.')[-1]] = value

    return parsed


def from_file() -> dict:
    with CONFIG_FILE.open('r') as f:
        data: dict = json.load(f)

    version = data.get('version', 0)
    if version == 0:
        return {}
    elif version == 1:
        return _version_1(data)
    elif version == 2:
        return _version_2(data)
