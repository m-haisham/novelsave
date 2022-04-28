import mimetypes
from pathlib import Path

from appdirs import user_config_dir
from tqdm import tqdm

NAME = "novelsave"
AUTHOR = "Mensch272"

# base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_DIR = BASE_DIR / "novelsave/resources"

# operating system specific configuration file
# config directory is used to place logs, config, cache
CONFIG_DIR = Path(user_config_dir(NAME, AUTHOR))
CONFIG_FILE = CONFIG_DIR / "config.json"

DATA_DIR = CONFIG_DIR / "data"

DATABASE_FILE = (CONFIG_DIR / "data.sqlite").resolve()
DATABASE_URL = "sqlite:///" + str(DATABASE_FILE)

# default novel directory, where packaged files such
# as epub and pdf are stored.
DEFAULT_NOVEL_DIR = Path.home() / "novels"
DEFAULT_HTML_FONT_SIZE = "1rem"

# the following map defines how files are stored
# by further subdivision into sub-folders
DIVISION_RULES = {
    k: v.split("/", maxsplit=1)[0] for k, v in mimetypes.types_map.items()
}


def console_formatter(record):
    if record["level"].name == "INFO":
        return "{message}\n"
    else:
        return "<level>{level}: {message}</level>\n"


LOGGER_CONFIG = {
    "handlers": [
        {
            "sink": lambda msg: tqdm.write(msg, end=""),
            "format": console_formatter,
            "level": "INFO",
            "colorize": True,
            "backtrace": False,
            "diagnose": False,
        },
        {
            "sink": CONFIG_DIR / "logs" / "{time}.log",
            "level": "TRACE",
            "retention": "2 days",
            "compression": "zip",
            "encoding": "utf-8",
        },
    ],
}

TQDM_CONFIG = {"ncols": 80, "bar_format": "{percentage:3.0f}% |{bar}{r_bar}"}

config = {
    "name": NAME,
    "author": AUTHOR,
    "base_dir": BASE_DIR,
    "static": {
        "dir": STATIC_DIR,
    },
    "config": {
        "dir": CONFIG_DIR,
        "file": CONFIG_FILE,
        "defaults": {
            "novel.dir": DEFAULT_NOVEL_DIR,
            "html.font_size": DEFAULT_HTML_FONT_SIZE,
        },
    },
    "data": {
        "dir": DATA_DIR,
        "division_rules": DIVISION_RULES,
    },
    "novel": {
        "dir": DEFAULT_NOVEL_DIR,
    },
    "infrastructure": {
        "database": {
            "url": DATABASE_URL,
        }
    },
}
