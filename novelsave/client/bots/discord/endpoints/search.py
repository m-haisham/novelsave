from typing import Dict, List, Optional

import nextcord
from dependency_injector.wiring import Provide
from loguru import logger
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

from novelsave.core.dtos import NovelDTO
from novelsave.core.services.source import BaseSourceService
from .. import utils
from ..bot import bot
from ..checks import assert_check, is_direct_only
from ..decorators import log_error, session_task
from ..session import SessionHandler, SessionFragment, Session


class SearchHandler(SessionFragment):
    source_service: BaseSourceService = Provide["application.services.source_service"]
    search_limit: int = Provide["config.discord.search.limit"]

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

    async def _state_searching(self, intr: Interaction):
        await intr.send("I'm busy searching for novels.")

    async def _state_novel_select(self, intr: Interaction):
        await intr.send("Please select a novel from the list.")
        await intr.send(self._novel_list())

    async def _state_source_select(self, intr: Interaction):
        self.session.send_sync(
            f"**{self.key}** selected. Now please select the source from the list below."
        )
        await intr.send(self._source_list())

    @log_error
    @session_task(False)
    def search(self, word: str):
        self.session.state = self._state_searching
        search_capable = [
            s for s in self.source_service.get_novel_sources() if s.is_search_capable
        ]

        self.session.send_sync(
            f"Searching for '{word}' in {len(search_capable)} sources…"
        )

        self.results.clear()
        for gateway in search_capable:
            if not gateway.is_search_capable:
                logger.debug(f"'{gateway.name}' does not support search.")
                return

            try:
                novels = gateway.search(word)
            except Exception as e:
                logger.exception(e)
                self.session.send_sync(
                    utils.error(
                        f"Encountered error while searching in {gateway.name}: {type(e).__name__}"
                    )
                )
                continue

            logger.debug(f"Found {len(novels)} novels in '{gateway.name}'.")
            for novel in novels:
                self.results.setdefault(novel.title, []).append(novel)

        self.sorted_keys = [
            k for k, _ in list(sorted(self.results.items(), key=lambda i: len(i[1])))
        ]

        self.session.send_sync(
            "Please select a novel from the list using `/select <number>`."
        )
        self.session.send_sync(self._novel_list())
        self.session.state = self._state_novel_select

    @log_error
    def select_novel(self, index: int):
        if index < 0 or index >= min(self.search_limit, len(self.results)):
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

    @log_error
    def select_source(self, index: int):
        try:
            novel = self.results[self.key][index]
        except IndexError:
            self.session.send_sync(
                f"Select a valid source (1-{len(self.results[self.key])})."
            )
            return
        except KeyError:
            self.session.send_sync("Novel not found.")
            return

        self.session.state = self.session.initial
        self.clear()

        return novel.url

    def clear(self):
        self.sorted_keys.clear()
        self.results.clear()
        self.key = None

    def _novel_list(self) -> str:
        items = self.sorted_keys

        output = ""
        if len(items) > self.search_limit:
            items = items[: self.search_limit]
            output += f"Limiting results to {self.search_limit} novels!\n"

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
    unsupported = utils.error("Search is disabled.")

    @staticmethod
    def is_supported(session: Session):
        """Whether search is implemented"""
        return session.has_fragment(SearchHandler)

    @nextcord.slash_command(description="Start a search task", force_global=True)
    async def search(
        self,
        intr: Interaction,
        *,
        query: str = SlashOption(description="The search query"),
    ):
        """Start a search task"""
        if not await assert_check(intr, is_direct_only):
            return

        session = self.session_handler.get_or_create(intr)
        if not self.is_supported(session):
            await intr.send(self.unsupported)
            return

        await session.run(
            intr, SearchHandler.search, query, message=utils.task(f"Search ({query=})")
        )

    @nextcord.slash_command(
        description="Select from the provided search results", force_global=True
    )
    async def select(
        self,
        intr: Interaction,
        num: int = SlashOption(
            description="The no. of item to select",
        ),
    ):
        """Select from the provided search results"""
        if not await assert_check(intr, is_direct_only):
            return

        session = self.session_handler.get_or_create(intr)
        if not self.is_supported(session):
            await intr.send(self.unsupported)
            return

        if not session.get(SearchHandler.is_select)():
            await intr.send(utils.error("Session does not require selection."))
            return

        if session.get(SearchHandler.is_novel_select)():
            await session.run(intr, SearchHandler.select_novel, num - 1)
        else:
            url = session.get(SearchHandler.select_source)(num - 1)
            await intr.send(f"✔ {url} selected.")
            await bot.get_cog("Download").download.callback(
                bot.get_cog("Download"), intr, url, "epub"
            )
