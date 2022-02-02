from dependency_injector.wiring import inject, Provide
from nextcord.interactions import Interaction

from novelsave.core.services.source import BaseSourceService
from ..bot import bot
from ..checks import assert_check, is_direct_only

source_service: BaseSourceService = Provide["application.services.source_service"]


@bot.slash_command(description="Send a direct message to you")
async def dm(intr: Interaction):
    await intr.send("Sending you a direct message now.")
    await intr.user.send(f"Hello, {intr.user.name}.")


@bot.slash_command(description="List all the sources supported", force_global=True)
@inject
async def sources(
    intr: Interaction,
):
    """List all the sources supported"""
    if not await assert_check(intr, is_direct_only):
        return

    await intr.response.defer()

    messages = [
        f"The sources currently supported include (v{source_service.current_version}):",
        "\n".join(
            f"• `{'🔍' if gateway.is_search_capable else ' '}` <{gateway.base_url}>"
            for gateway in sorted(
                source_service.get_novel_sources(), key=lambda g: g.base_url
            )
        ),
    ]

    await intr.send("\n".join(messages))
    await intr.channel.send(
        "You can request a new source by creating an issue at "
        "<https://github.com/mensch272/novelsave/issues/new/choose>"
    )
