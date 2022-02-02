import functools
import os
import sys
from datetime import timedelta

from loguru import logger
import copy

from novelsave.settings import config as base_config


def config() -> dict:
    """:returns: Configuration for _discord_config bot"""
    return {"app": copy.deepcopy(base_config), "discord": _discord_config()}


def logger_config() -> dict:
    return {
        "handlers": [
            {
                "sink": sys.stdout,
                "level": "TRACE",
                "backtrace": True,
                "diagnose": True,
            },
        ]
    }


def intenv(key: str, default: int) -> int:
    try:
        return int(os.getenv(key))
    except (TypeError, ValueError):
        return default


@functools.lru_cache()
def _discord_config() -> dict:
    """Initialize and return discord configurations as a dict

    The returned dict must contain 'DISCORD_TOKEN'
    """
    discord_token = os.getenv("DISCORD_TOKEN")
    if not discord_token:
        logger.error("Required environment variable 'DISCORD_TOKEN' is not set.")
        sys.exit(1)

    return {
        "key": discord_token,
        "session": {
            "retain": timedelta(minutes=intenv("DISCORD_SESSION_TIMEOUT", 10)),
            "threads": intenv("DISCORD_SESSION_THREADS", 5),
        },
        "search": {
            "limit": intenv("DISCORD_SEARCH_LIMIT", 20),
            "disabled": os.getenv("DISCORD_SEARCH_DISABLED", "no").lower(),
        },
        "cloud": {
            "filehost": os.getenv("DISCORD_EXTERNAL_FILEHOST", "none").lower(),
        },
    }
