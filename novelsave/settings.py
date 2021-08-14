import sys
from pathlib import Path

from appdirs import user_config_dir

NAME = 'novelsave'
AUTHOR = 'mhaisham'

BASE_DIR = Path(__file__).resolve().parent.parent

# operating system specific configuration file
# config directory is used to place logs, config, cache
CONFIG_DIR = Path(user_config_dir(NAME, AUTHOR))
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = CONFIG_DIR / 'config.yml'
DATA_DIR = CONFIG_DIR / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_FILE = str((CONFIG_DIR / 'data.sqlite').resolve())
DATABASE_URL = 'sqlite:///' + DATABASE_FILE

NOVEL_DIR = Path.home() / 'novels'

# defined the extension format of the file
# where chapter content is stored
CHAPTER_EXTENSION = '.html'

# the following map defines how files are stored
# by further subdivision into sub-folders
DIVISION_RULES = {
    CHAPTER_EXTENSION: 'chapters',
    **{
        key: 'assets'
        for key in {'.jpeg', '.jpg', '.png', '.webp', '.gif'}
    },
}


LOGGER_CONFIG = {
    "handlers": [
        {
            "sink": sys.stdout,
            "format": "<level>{level:<8}</level> | <level>{message}</level>",
            'level': 'TRACE',
            'colorize': True,
        },
    ],
}

# same information just as a dict for convenience with injector
def as_dict():
    return {
        'name': NAME,
        'author': AUTHOR,
        'base_dir': BASE_DIR,
        'config': {
            'dir': CONFIG_DIR,
            'file': CONFIG_FILE,
        },
        'data': {
            'dir': DATA_DIR,
            'chapter_extension': CHAPTER_EXTENSION,
            'division_rules': DIVISION_RULES,
        },
        'novel': {
            'dir': NOVEL_DIR,
        },
        'infrastructure': {
            'database': {
                'url': DATABASE_URL,
            }
        }
    }


# defines the editable configurations
__editable__ = {'database_url', 'chapter_extension', 'data_division'}
