import functools
import os
import sys

import nextcord
from loguru import logger

from novelsave.utils.helpers import dotenv_helper
from . import config

logger.configure(**config.logger_config())

try:
    from nextcord.ext import commands
except ImportError as e:
    logger.exception(e)
    sys.exit(1)


bot = commands.Bot("$")

dotenv_helper.load_dotenv()
if os.getenv("MODE", "prod").lower() == "dev":
    bot.slash_command = functools.partial(
        bot.slash_command, guild_ids=[int(os.getenv("GUILD"))]
    )

    nextcord.slash_command = functools.partial(
        nextcord.slash_command, guild_ids=[int(os.getenv("GUILD"))]
    )
