from pathlib import Path

from appdirs import user_config_dir

from .containers import ApplicationContainer

NAME = 'novelsave'
AUTHOR = 'mhaisham'

BASE_DIR = Path(__file__).resolve().parent.parent

# operating system specific configuration file
# config directory is used to place logs, config, cache
CONFIG_DIR = Path(user_config_dir(NAME, AUTHOR))

DATABASE_URL = 'sqlite:///' + str(CONFIG_DIR / 'data.sqlite')


# same information just as a dict for convenience with injector
__dict__ = {
    'name': NAME,
    'author': AUTHOR,
    'base_dir': BASE_DIR,
    'config_dir': CONFIG_DIR,
    'database_url': DATABASE_URL,
}

# setup injectors
ApplicationContainer.config.from_dict(__dict__)
