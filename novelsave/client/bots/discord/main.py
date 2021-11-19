import sys

from loguru import logger

from novelsave.containers import Application
from . import config
from .containers import DiscordApplication


def wire(packages):
    application = Application()
    application.config.from_dict(config.app())
    application.wire(packages=packages)

    discord_application = DiscordApplication()
    discord_application.config.from_dict(config.discord())
    application.wire(packages=packages)

    return application, discord_application


def main():
    """Start the discord bot"""
    logger.configure(**config.logger())

    try:
        from nextcord.ext import commands
    except ImportError as e:
        logger.exception(e)
        sys.exit(1)

    from . import endpoints

    application, discord_application = wire([endpoints])

    # initialize
    bot = commands.Bot(">> ")

    # register commands
    bot.command()(endpoints.start)
    bot.command()(endpoints.test)

    # start server
    bot.run(discord_application.config.get("key"))
