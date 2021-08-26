import sys
from pathlib import Path

from appdirs import user_config_dir
from tqdm import tqdm

NAME = 'novelsave'
AUTHOR = 'Mensch272'

BASE_DIR = Path(__file__).resolve().parent.parent

# operating system specific configuration file
# config directory is used to place logs, config, cache
CONFIG_DIR = Path(user_config_dir(NAME, AUTHOR))
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = CONFIG_DIR / 'config.json'
DATA_DIR = CONFIG_DIR / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# database file and the corresponding link to it
# the database is where all the novel data is stored
DATABASE_FILE = str((CONFIG_DIR / 'data.sqlite').resolve())
DATABASE_URL = 'sqlite:///' + DATABASE_FILE

NOVEL_DIR = Path.home() / 'novels'

# the following map defines how files are stored
# by further subdivision into sub-folders
DIVISION_RULES = {
    **{
        key: 'assets'
        for key in {'.jpeg', '.jpg', '.png', '.webp', '.gif'}
    },
}

LOGGER_CONFIG = {
    "handlers": [
        {
            'sink': lambda msg: tqdm.write(msg, end=""),
            'format': '<level>{level:<8}</level> | <level>{message}</level>',
            'level': 'TRACE',
            'colorize': True,
        },
        {
            'sink': CONFIG_DIR / 'logs' / 'dev' / '{time:YYYY-MM-DD}.log',
            'level': 'TRACE',
        }
    ],
}

TQDM_CONFIG = {
    'ncols': 80,
    'bar_format': f'{"PROGRESS":<8}' + ' | {percentage:3.0f}% |{bar}| {r_bar}'
}

_config = {
    'name': NAME,
    'author': AUTHOR,
    'base_dir': BASE_DIR,
    'config': {
        'dir': CONFIG_DIR,
        'file': CONFIG_FILE,
    },
    'data': {
        'dir': DATA_DIR,
        'division_rules': DIVISION_RULES,
    },
    'novel': {
        'dir': NOVEL_DIR,
    },
    'infrastructure': {
        'database': {
            'url': DATABASE_URL,
        }
    },
    'logger': LOGGER_CONFIG,
}


# same information just as a dict for convenience with injector
def as_dict():
    return _config.copy()
