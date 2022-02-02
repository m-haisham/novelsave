from nextcord import Interaction
from nextcord.ext import commands

from .bot import bot


async def is_direct_only(intr: Interaction) -> bool:
    """Custom direct only check

    This check returns true when one of the below checks are true
    - The message is not from a guild
    """
    if await bot.is_owner(intr.user):
        return True

    if intr.guild is not None:
        raise commands.CheckFailure(
            "This command is disabled inside guilds. "
            "Use `/dm` to start a private session.",
        )

    return True


async def assert_check(intr: Interaction, func) -> bool:
    try:
        return await func(intr)
    except commands.CheckFailure as e:
        await intr.send(str(e))

    return False
