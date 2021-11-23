import sys

from loguru import logger

from . import config

logger.configure(**config.logger_config())

try:
    from nextcord.ext import commands
except ImportError as e:
    logger.exception(e)
    sys.exit(1)


bot = commands.Bot("$")
