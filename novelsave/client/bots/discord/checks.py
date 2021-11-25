from nextcord.ext import commands


async def direct_only(ctx: commands.Context):
    """Custom direct only check

    This check returns true when one of the below checks are true
    - The message author is bot owner and is invoked with help
    - The message is not from a guild
    """
    if await ctx.bot.is_owner(ctx.author) and ctx.invoked_with == "help":
        return True

    if ctx.guild is not None:
        raise commands.CheckFailure(
            f"You may not use this command inside a guild. "
            f"Use the '{ctx.clean_prefix}dm' to start a private session.",
        )

    return True
