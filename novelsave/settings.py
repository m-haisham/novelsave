from pathlib import Path

from appdirs import user_config_dir

NAME = 'novelsave'
AUTHOR = 'mhaisham'

BASE_DIR = Path(__file__).resolve().parent.parent

# operating system specific configuration file
# config directory is used to place logs, config, cache
CONFIG_DIR = Path(user_config_dir(NAME, AUTHOR))

CONFIG_FILE = CONFIG_DIR / 'config.yml'
DATA_DIR = CONFIG_DIR / 'data'

DATABASE_URL = 'sqlite:///' + str((CONFIG_DIR / 'data.sqlite').resolve())

# defined the extension format of the file
# where chapter content is stored
CHAPTER_EXTENSION = '.nschtml'

# the following map defines how files are stored
# by further subdivision into sub-folders
DIVISION_RULES = {
    CHAPTER_EXTENSION: 'chapters',
    **{
        key: 'assets'
        for key in {'.jpeg', '.jpg', '.png', '.webp', '.gif'}
    },
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
        'infrastructure': {
            'database': {
                'url': DATABASE_URL,
            }
        }
    }


# defines the editable configurations
__editable__ = {'database_url', 'chapter_extension', 'data_division'}
