from nextcord.ext import commands


def session_key(ctx: commands.Context) -> str:
    return str(ctx.author.id)
