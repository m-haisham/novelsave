from nextcord.ext import commands
from . import mfmt


def direct_only(ctx: commands.Context):
    """Custom direct only check

    Either
    - The message author is bot owner and is invoked with help
    - The message is not from a guild
    """
    if ctx.bot.is_owner(ctx.author) and ctx.invoked_with == "help":
        return True

    if ctx.guild is not None:
        raise commands.CheckFailure(
            mfmt.error(
                f"You may not use this command inside a guild. Use the '{ctx.clean_prefix}dm' to start a private session.",
            )
        )

    return True
