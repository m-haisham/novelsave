import mimetypes
import os
from pathlib import Path

import dotenv
import fs
from appdirs import user_config_dir
from tqdm import tqdm

NAME = "novelsave"
AUTHOR = "Mensch272"

# load environment variables
dotenv.load_dotenv()  # take environment variables from .env

STORAGE = os.environ.get("STORAGE") or "filesystem"
LOGTOFILE = bool(int(os.environ.get("LOGTOFILE") or "1"))

fs_storage = {
    "filesystem": "osfs",
    "memory": "mem",
}

# base project directory
BASE_DIR = fs.open_fs(
    fs_storage[STORAGE] + "://" + str(Path(__file__).resolve().parent.parent)
)

STATIC_DIR = "novelsave/resources"

# operating system specific configuration file
# config directory is used to place logs, config, cache
CONFIG_PATH = Path(user_config_dir(NAME, AUTHOR))
CONFIG_DIR = fs.open_fs(fs_storage[STORAGE] + "://" + str(CONFIG_PATH))
CONFIG_FILE = "config.json"

DATA_DIR = fs.open_fs(fs_storage[STORAGE] + "://" + str(CONFIG_PATH / "data"))

if STORAGE == "memory":
    DATABASE_URL = "sqlite:///:memory:"
else:
    DATABASE_FILE = (CONFIG_PATH / "data.sqlite").resolve()
    DATABASE_URL = "sqlite:///" + str(DATABASE_FILE)

# default novel directory, where packaged files such
# as epub and pdf are stored.
NOVEL_DIR = fs.open_fs(fs_storage[STORAGE] + "://" + str(Path.home()))

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
    ],
}

if LOGTOFILE:
    LOGGER_CONFIG["handlers"] += [
        {
            "sink": CONFIG_PATH / "logs" / "{time}.log",
            "level": "TRACE",
            "retention": "2 days",
            "compression": "zip",
            "encoding": "utf-8",
        }
    ]

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
    },
    "data": {
        "dir": DATA_DIR,
        "division_rules": DIVISION_RULES,
    },
    "novel": {
        "dir": NOVEL_DIR,
    },
    "infrastructure": {
        "database": {
            "url": DATABASE_URL,
        }
    },
    "logger": LOGGER_CONFIG,
    "tqdm": TQDM_CONFIG,
}
