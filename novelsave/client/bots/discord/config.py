import functools
import os

import dotenv

from novelsave.settings import config


@functools.lru_cache()
def app() -> dict:
    """Initialize and return the configuration used by the base application"""
    return config.copy()


def logger() -> dict:
    return {
        "handlers": [
            {
                "sink": config["config"]["dir"] / "logs" / "{time}.log",
                "level": "TRACE",
                "retention": "2 days",
                "compression": "zip",
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

    return {"key": os.getenv("DISCORD_TOKEN")}
