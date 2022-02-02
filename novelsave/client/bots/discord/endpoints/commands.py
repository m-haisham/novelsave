from dependency_injector.wiring import inject, Provide
from nextcord import Embed
from nextcord.interactions import Interaction

from novelsave.core.services.source import BaseSourceService
from ..bot import bot
from ..checks import assert_check, is_direct_only

source_service: BaseSourceService = Provide["application.services.source_service"]


@bot.slash_command(description="Send a direct message to you")
async def dm(intr: Interaction):
    await intr.send("💬 Sending you a direct message now.")
    await intr.user.send(f"👋 Hello, {intr.user.name}.")


@bot.slash_command(description="List all the sources supported", force_global=True)
@inject
async def sources(intr: Interaction):
    """List all the sources supported"""
    if not await assert_check(intr, is_direct_only):
        return

    await intr.response.defer()

    embed = Embed(
        title="Supported sources",
        description="This embed shows the list of all the sources currently supported",
        url="https://novelsave-sources.readthedocs.io/en/latest/content/support.html#supported-novel-sources",
    )

    for gateway in sorted(source_service.get_novel_sources(), key=lambda g: g.base_url):
        value = f"search: {'✅' if gateway.is_search_capable else '❌'}"
        embed.add_field(name=f"<{gateway.base_url}>", value=value)

    embed.set_footer(text=f"Version {source_service.current_version}")

    request_embed = Embed(
        title="Looking for something else?",
        description="You can request a new source by creating an issue at github",
        url="https://github.com/mensch272/novelsave/issues/new/choose",
    )

    await intr.send(embeds=[embed, request_embed])
