import functools
import os
import sys
from datetime import timedelta

import dotenv

from novelsave.settings import config, console_formatter


@functools.lru_cache()
def app() -> dict:
    """Initialize and return the configuration used by the base application"""
    return config.copy()


def logger() -> dict:
    return {
        "handlers": [
            {
                "sink": sys.stderr,
                "level": "DEBUG",
                "format": console_formatter,
            },
            {
                "sink": config["config"]["dir"] / "logs" / "{time}.log",
                "level": "TRACE",
                "retention": "15 days",
                "encoding": "utf-8",
            },
        ]
    }


@functools.lru_cache()
def discord() -> dict:
    """Initialize and return discord configurations as a dict

    The returned dict must contain 'DISCORD_TOKEN'
    """
    dotenv.load_dotenv()

    return {
        "key": os.getenv("DISCORD_TOKEN"),
        "session": {
            "retain": timedelta(minutes=10),
        },
        "search": {
            "limit": 20,
        },
    }
