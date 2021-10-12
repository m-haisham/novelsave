import json
from pathlib import Path

from ...settings import CONFIG_FILE


def _load_version_1(data: dict):
    config = data.get('config', {})

    try:
        config['novel']['dir'] = Path(config['novel']['dir'])
    except KeyError:
        pass

    return config


def from_file() -> dict:
    with CONFIG_FILE.open('r') as f:
        data: dict = json.load(f)

    version = data.get('version', 0)
    if version == 0:
        return {}
    elif version == 1:
        return _load_version_1(data)
