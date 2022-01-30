from loguru import logger

from .config import config
from .containers import DiscordApplication


def wire(packages):
    """Wire the containers to the packages"""
    discord_config = config()
    discord_config["app"]["config"]["dir"].mkdir(parents=True, exist_ok=True)

    discord_application = DiscordApplication()
    discord_application.config.from_dict(discord_config)
    discord_application.wire(packages=packages)

    return discord_application


def main():
    """Start the _discord_config bot"""
    from .bot import bot
    from . import endpoints, session

    discord_application = wire([endpoints, session])

    # cogs
    bot.add_cog(endpoints.SessionCog())
    bot.add_cog(endpoints.Download())
    bot.add_cog(endpoints.Search())

    logger.debug("Running discord bot...")
    bot.run(discord_application.config.get("discord.key"))
