from loguru import logger

from novelsave.containers import Application
from . import config
from .containers import DiscordApplication


def wire(packages):
    """Wire the containers to the packages"""
    app_config = config.app()
    app_config["config"]["dir"].mkdir(parents=True, exist_ok=True)

    application = Application()
    application.config.from_dict(config.app())
    application.wire(packages=packages)

    discord_application = DiscordApplication()
    discord_application.discord_config.from_dict(config.discord())
    discord_application.wire(packages=packages)

    return application, discord_application


def main():
    """Start the discord bot"""
    from .bot import bot
    from . import endpoints

    application, discord_application = wire([endpoints])

    # cogs
    bot.add_cog(endpoints.SessionCog())
    bot.add_cog(endpoints.Download())
    bot.add_cog(endpoints.Search())

    logger.debug("Running discord bot...")
    bot.run(discord_application.discord_config.get("key"))
