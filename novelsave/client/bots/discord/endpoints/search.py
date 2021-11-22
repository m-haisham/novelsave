from typing import Dict, List, Optional

from dependency_injector.wiring import Provide
from loguru import logger
from nextcord.ext import commands

from novelsave.containers import Application
from novelsave.core.dtos import NovelDTO
from novelsave.core.services.source import BaseSourceService
from .. import checks, mfmt
from ..session import SessionHandler, SessionFragment


class SearchHandler(SessionFragment):
    source_service: BaseSourceService = Provide[Application.services.source_service]

    def __init__(self, *args, **kwargs):
        super(SearchHandler, self).__init__(*args, **kwargs)

        self.sorted_keys = []
        self.results: Dict[str, List[NovelDTO]] = {}
        self.key: Optional[str] = None

    def is_busy(self):
        return self.session.state == self._state_searching

    def is_select(self):
        return any(
            self.session.state == state
            for state in [self._state_novel_select, self._state_source_select]
        )

    def is_novel_select(self):
        return self.session.state == self._state_novel_select

    async def _state_searching(self, ctx: commands.Context):
        await ctx.send("I'm busy searching for novels.")

    async def _state_novel_select(self, ctx: commands.Context):
        await ctx.send("Please select a novel from the list.")
        await ctx.send(self._novel_list())

    async def _state_source_select(self, ctx: commands.Context):
        self.session.send_sync(
            f"**{self.key}** selected. Now please select the source from the list below."
        )
        await ctx.send(self._source_list())

    def search(self, word: str):
        self.session.state = self._state_searching
        search_capable = [
            s
            for s in self.source_service.get_supported_novel_sources()
            if s.is_search_capable
        ]

        self.session.send_sync(
            f"Searching for '{word}' in {len(search_capable)} sources…"
        )

        self.results.clear()
        for gateway in search_capable:
            if not gateway.is_search_capable:
                logger.debug(f"'{gateway.name}' does not support search.")
                return

            novels = gateway.search(word)
            logger.debug(f"Found {len(novels)} novels in '{gateway.name}'.")
            for novel in novels:
                self.results.setdefault(novel.title, []).append(novel)

        self.sorted_keys = [
            k for k, _ in list(sorted(self.results.items(), key=lambda i: len(i[1])))
        ]

        self.session.send_sync(
            f"Please select a novel from the list using `{self.session.ctx.clean_prefix}select <number>`."
        )
        self.session.send_sync(self._novel_list())
        self.session.state = self._state_novel_select

    def select_novel(self, index: int):
        if index < 0 or index >= min(20, len(self.results)):
            self.session.send_sync(
                f"Please limit selection to between 1 and {min(20, len(self.results))}"
            )
            return

        self.key = self.sorted_keys[index]
        self.session.send_sync(
            f"`{self.key}` selected. Now please select the source from the list below."
        )
        self.session.send_sync(self._source_list())
        self.session.state = self._state_source_select

    def select_source(self, index: int):
        try:
            novel = self.results[self.key][index]
        except KeyError:
            self.session.send_sync("Novel not found")
            return

        self.session.state = self.session.initial
        self.close()

        return novel.url

    def close(self):
        self.sorted_keys.clear()
        self.results.clear()
        self.key = None

    def _novel_list(self) -> str:
        items = self.sorted_keys

        output = ""
        if len(items) > 20:
            items = items[:20]
            output += "Limiting results to 20 novels!\n"

        output += "\n".join(
            f"{i + 1}: {title} ({len(self.results[title])} sources)"
            for i, title in enumerate(items)
        )

        return output

    def _source_list(self) -> str:
        return "\n".join(
            f"{i + 1}: <{novel.url}> ({self.source_service.source_from_url(novel.url).name})"
            for i, novel in enumerate(self.results[self.key])
        )


class Search(commands.Cog):
    """This controls search"""

    session_handler: SessionHandler = Provide["session.session_handler"]

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await checks.direct_only(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CheckFailure) or isinstance(
            error, commands.MissingRequiredArgument
        ):
            await ctx.send(mfmt.error(str(error)))

        logger.exception(repr(error))

    @commands.command()
    async def search(self, ctx: commands.Context, *, words):
        """Start a search task"""
        session = await self.session_handler.get_or_create(ctx)
        await session.run(ctx, SearchHandler.search, words)

    @commands.command()
    async def select(self, ctx: commands.Context, no: int):
        """Select from the provided search results"""
        session = await self.session_handler.get_or_create(ctx)
        if not await session.call(SearchHandler.is_select):
            await ctx.send("Session does not require selection.")
            return

        if await session.call(SearchHandler.is_novel_select):
            await session.run(ctx, SearchHandler.select_novel, no - 1)
        else:
            url = await session.call(SearchHandler.select_source, no - 1)
            await ctx.send(f"{url} selected.")
            await ctx.invoke(session.bot.get_command("download"), url)
