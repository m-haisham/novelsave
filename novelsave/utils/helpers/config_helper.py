import json
from pathlib import Path

from ...settings import CONFIG_FILE


def from_file() -> dict:
    with CONFIG_FILE.open('r') as f:
        data: dict = json.load(f)

    config = data.get('config', {})

    try:
        config['novel']['dir'] = Path(config['novel']['dir'])
    except KeyError:
        pass

    return config
