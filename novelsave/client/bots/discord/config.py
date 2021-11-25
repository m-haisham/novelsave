import functools
import os
import sys
from datetime import timedelta

import dotenv
from loguru import logger

from novelsave.settings import config, console_formatter


@functools.lru_cache()
def app() -> dict:
    """Initialize and return the configuration used by the base application"""
    return config.copy()


def logger_config() -> dict:
    return {
        "handlers": [
            {
                "sink": sys.stderr,
                "level": "TRACE",
                "format": console_formatter,
                "backtrace": True,
                "diagnose": True,
            },
            {
                "sink": config["config"]["dir"] / "logs" / "{time}.log",
                "level": "TRACE",
                "retention": "3 days",
                "encoding": "utf-8",
            },
        ]
    }


def intenv(key: str, default: int) -> int:
    try:
        return int(os.getenv(key))
    except (TypeError, ValueError):
        return default


@functools.lru_cache()
def discord() -> dict:
    """Initialize and return discord configurations as a dict

    The returned dict must contain 'DISCORD_TOKEN'
    """
    dotenv.load_dotenv()

    discord_token = os.getenv("DISCORD_TOKEN")
    if not discord_token:
        logger.error("Required environment variable 'DISCORD_TOKEN' is not set.")

    return {
        "key": discord_token,
        "session": {
            "retain": timedelta(minutes=intenv("DISCORD_SESSION_TIMEOUT", 10)),
        },
        "download": {
            "threads": intenv("DISCORD_DOWNLOAD_THREADS", 4),
        },
        "search": {
            "limit": intenv("DISCORD_SEARCH_LIMIT", 20),
            "disabled": os.getenv("DISCORD_SEARCH_DISABLED", "no").lower(),
        },
    }
