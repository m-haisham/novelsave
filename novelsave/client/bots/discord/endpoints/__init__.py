from dependency_injector.wiring import inject, Provide
from nextcord.ext import commands

from novelsave.containers import Application
from novelsave.core.services import BaseNovelService


async def start(ctx):
    """Initialize the bot"""
    # you can use docstrings for the slash command description too
    await ctx.send("Initialized the bot")


@inject
async def test(
    ctx: commands.Context,
    *args,
    novel_service: BaseNovelService = Provide[Application.services.novel_service],
    **kwargs,
):
    for novel in novel_service.get_all_novels():
        await ctx.send(f"{novel.id:<2}: {novel.title} by {novel.author}")
