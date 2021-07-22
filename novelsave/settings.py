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

DATABASE_URL = 'sqlite:///' + str(CONFIG_DIR / 'data.sqlite')

# defined the extension format of the file
# where chapter content is stored
CHAPTER_EXTENSION = '.nschtml'

# the following map defines how files are stored
# by further subdivision into sub-folders
DATA_DIVISION = {
    CHAPTER_EXTENSION: 'chapters',
    **{
        key: 'assets'
        for key in {'.jpeg', '.jpg', '.png', '.webp', '.gif'}
    },
}

# same information just as a dict for convenience with injector
__config__ = {
    'name': NAME,
    'author': AUTHOR,
    'base_dir': BASE_DIR,
    'config_dir': CONFIG_DIR,
    'config_file': CONFIG_FILE,
    'data_dir': DATA_DIR,
    'database_url': DATABASE_URL,
    'chapter_extension': CHAPTER_EXTENSION,
    'data_division': DATA_DIVISION,
}

# defines the editable configurations
__editable__ = {'database_url', 'chapter_extension', 'data_division'}
