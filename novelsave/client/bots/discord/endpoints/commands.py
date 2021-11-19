from dependency_injector.wiring import inject, Provide
from nextcord.ext import commands

from novelsave import __version__
from novelsave.containers import Application
from novelsave.core.services import BaseNovelService
from novelsave.core.services.source import BaseSourceService
from ..bot import bot


@bot.command()
async def start(ctx):
    """Initialize the bot"""
    # you can use docstrings for the slash command description too
    await ctx.send("Initialized the bot")


@bot.command()
@inject
async def test(
    ctx: commands.Context,
    *args,
    novel_service: BaseNovelService = Provide[Application.services.novel_service],
    **kwargs,
):
    await ctx.send("[link](https://www.wattpad.com)")


@bot.command()
@inject
async def sources(
    ctx: commands.Context,
    *args,
    source_service: BaseSourceService = Provide[Application.services.source_service],
):
    with ctx.typing():
        await ctx.send(f"The sources currently supported include (v{__version__}):")

        source_list = "\n".join(
            f"• <{gateway.base_url}> " + ("🔍" if gateway.is_search_capable else "")
            for gateway in sorted(
                source_service.get_supported_novel_sources(), key=lambda g: g.base_url
            )
        )

        await ctx.send(source_list)
        await ctx.send(
            "You can request a new source by creating an issue at "
            "<https://github.com/mensch272/novelsave/issues/new/choose>"
        )
