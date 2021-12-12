from dependency_injector.wiring import inject, Provide
from loguru import logger
from nextcord.ext import commands

from novelsave.containers import Application
from novelsave.core.services.source import BaseSourceService
from .. import checks, mfmt
from ..bot import bot


@bot.command()
async def dm(ctx: commands.Context):
    """Send a direct message to you"""
    await ctx.author.send(
        f"Hello, {ctx.author.name}.\n"
        f"Send `{ctx.clean_prefix}help` to get usage instructions."
    )


@bot.command()
@commands.check(checks.direct_only)
@inject
async def sources(
    ctx: commands.Context,
    *args,
    source_service: BaseSourceService = Provide[Application.services.source_service],
):
    """List all the sources supported"""
    with ctx.typing():
        await ctx.send(
            f"The sources currently supported include (v{source_service.current_version}):"
        )

        source_list = "\n".join(
            f"• `{'🔍' if gateway.is_search_capable else ' '}` <{gateway.base_url}>"
            for gateway in sorted(
                source_service.get_novel_sources(), key=lambda g: g.base_url
            )
        )

        await ctx.send(source_list)
        await ctx.send(
            "You can request a new source by creating an issue at "
            "<https://github.com/mensch272/novelsave/issues/new/choose>"
        )


@sources.error
async def sources_error(ctx: commands.Context, error: Exception):
    if isinstance(error, commands.CommandError):
        await ctx.send(mfmt.error(str(error)))

    logger.exception(repr(error))
