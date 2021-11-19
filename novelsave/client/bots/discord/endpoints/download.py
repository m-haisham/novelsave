import asyncio
import functools
import logging
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Callable, Coroutine, Optional

import requests
from dependency_injector.wiring import inject, Provide
from loguru import logger
from nextcord.ext import commands

from novelsave.containers import Application
from novelsave.core.dtos import NovelDTO
from novelsave.core.entities.novel import Novel
from novelsave import migrations
from novelsave.core.services import (
    BaseNovelService,
    BasePathService,
    BaseAssetService,
    BaseFileService,
)
from novelsave.core.services.source import BaseSourceService, BaseSourceGateway
from novelsave.exceptions import SourceNotFoundException
from novelsave.utils.adapters import DTOAdapter
from novelsave.utils.helpers import url_helper, string_helper
from .. import config
from ..containers import DiscordApplication

DownloadState = Callable[[commands.Context], Coroutine]


def catch_error(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            args[0].send_sync(str(e))
            logging.exception(e)

    return wrapped


class DownloadHandler:
    source_service: BaseSourceService
    novel_service: BaseNovelService
    path_service: BasePathService
    dto_adapter: DTOAdapter
    asset_service: BaseAssetService
    file_service: BaseFileService

    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self.ctx = ctx

        self.state: DownloadState = self.initial_state
        self.last_activity = datetime.now()

        self.executor = ThreadPoolExecutor(max_workers=10)

        self.novel = None
        self.value = 0
        self.total = 0

        self.is_closed = False

        self.setup()

    def setup(self):
        application = Application()
        application.config.from_dict(self.config())

        # acquire services
        self.source_service = application.services.source_service()
        self.novel_service = application.services.novel_service()
        self.path_service = application.services.path_service()
        self.dto_adapter = application.adapters.dto_adapter()
        self.asset_service = application.services.asset_service()
        self.file_service = application.services.file_service()

        # migrate database to latest schema
        migrations.migrate(application.config.get("infrastructure.database.url"))

    def config(self):
        temp: dict = config.app()

        # make the config directories message specific
        temp["config"]["dir"] /= str(self.ctx.author.id)
        temp["config"]["file"] = temp["config"]["dir"] / temp["config"]["file"].name
        temp["novel"]["dir"] = temp["config"]["dir"] / "novels"
        temp["data"]["dir"] = temp["config"]["dir"] / "data"

        schema, url = temp["infrastructure"]["database"]["url"].split(
            ":///", maxsplit=1
        )
        db_path = Path(url)
        new_url = f"{schema}:///{str(db_path.parent / str(self.ctx.author.id) / db_path.name)}"

        temp["infrastructure"]["database"]["url"] = new_url

        # create config directories
        temp["config"]["dir"].mkdir(parents=True, exist_ok=True)

        return temp

    def is_busy(self) -> bool:
        return any(
            self.state == state for state in [self.info_state, self.download_state]
        )

    @inject
    def is_expired(
        self,
        current: datetime,
        session_retain_time: timedelta = Provide[
            DiscordApplication.config.session.retain
        ],
    ) -> bool:
        if self.is_busy():
            return False
        elif current - self.last_activity < session_retain_time:
            return False
        else:
            return True

    async def initial_state(self, ctx: commands.Context):
        pass

    async def info_state(self, ctx: commands.Context):
        await ctx.send("I'm busy retrieving novel information.")

    async def download_state(self, ctx: commands.Context):
        await ctx.send(
            f"I'm currently downloading with progress {self.value} of {self.total}."
        )

    def send_sync(self, *args, **kwargs):
        asyncio.run_coroutine_threadsafe(
            self.ctx.send(*args, **kwargs),
            self.bot.loop,
        )

    def process(self, url: str):
        self.last_activity = datetime.now()
        self.executor.submit(self.start, url)

    @catch_error
    def start(self, url: str):
        self.state = self.info_state

        try:
            source_gateway = self.source_service.source_from_url(url)
        except SourceNotFoundException:
            self.send_sync("This website is not yet supported.")
            self.send_sync(
                "You can request a new source by creating an issue at "
                "<https://github.com/mensch272/novelsave/issues/new/choose>"
            )
            return

        self.send_sync(f"Retrieving novel information from <{url}>…")
        novel_dto = self.retrieve_novel_info(source_gateway, url)
        if novel_dto is None:
            return

        chapter_count = len([c for v in novel_dto.volumes for c in v.chapters])
        self.send_sync(
            f"**{novel_dto.title.strip()}** by {novel_dto.author}, with {len(novel_dto.volumes)} "
            f"volumes of {chapter_count} chapters."
        )

        novel = self.novel_service.insert_novel(novel_dto)
        self.novel_service.insert_chapters(novel, novel_dto.volumes)
        self.novel_service.insert_metadata(novel, novel_dto.metadata)

        self.state = self.download_state
        self.download_thumbnail(novel)
        self.download_chapters(novel, url, source_gateway)

    def retrieve_novel_info(
        self, source_gateway: BaseSourceGateway, url: str
    ) -> NovelDTO:
        try:
            return source_gateway.novel_by_url(url)
        except requests.ConnectionError:
            self.send_sync("`Connection terminated unexpectedly.`")

    def download_thumbnail(self, novel: Novel):
        if novel.thumbnail_url is None:
            logger.debug(f"No thumbnail url found for '{novel.title}'.")
            return

        self.send_sync(f"Downloading thumbnail <{novel.thumbnail_url}>…")
        try:
            response = requests.get(novel.thumbnail_url)
        except requests.ConnectionError:
            self.send_sync("❗ Connection terminated unexpectedly.")
            return

        if not response.ok:
            self.send_sync(f"❗ {response.status_code} {response.reason}")
            return

        thumbnail_path = self.path_service.thumbnail_path(novel)
        self.novel_service.set_thumbnail_asset(
            novel, self.path_service.relative_to_data_dir(thumbnail_path)
        )

        thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_service.write_bytes(thumbnail_path, response.content)

        size = string_helper.format_bytes(len(response.content))
        self.send_sync(f"Downloaded and saved thumbnail image ({size}).")

    def download_chapters(
        self, novel: Novel, url: str, source_gateway: BaseSourceGateway
    ):
        chapters = self.novel_service.get_pending_chapters(novel)
        if not chapters:
            logger.info("Skipped chapter download as none are pending.")
            return

        self.send_sync(f"Downloading {len(chapters)} chapters…")
        self.total = len(chapters)
        self.value = 1

        for chapter in chapters:

            try:
                chapter_dto = source_gateway.update_chapter_content(
                    self.dto_adapter.chapter_to_dto(chapter)
                )
            except Exception as e:
                self.send_sync(f"❗ Error downloading {chapter.url}")
                logger.exception(e)
                continue

            chapter_dto.content = self.asset_service.collect_assets(novel, chapter_dto)
            self.novel_service.update_content(chapter_dto)

            logger.debug(
                f"Chapter content downloaded: '{chapter_dto.title}' ({chapter_dto.index})"
            )

            self.value += 1

    def close(self):
        self.executor.shutdown(wait=False, cancel_futures=True)
        shutil.rmtree(self.path_service.config_path)

        self.is_closed = True


class DownloadCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.handlers: Dict[str, Optional[DownloadHandler]] = {}

    @commands.command()
    async def status(self, ctx: commands.Context):
        if str(ctx.author.id) not in self.handlers:
            await ctx.send("You have no active download.")
            return

        handler = self.handlers[str(ctx.author.id)]
        if handler.state is None:
            await ctx.send("You have no active download.")
        else:
            await handler.state(ctx)

    @commands.command()
    async def download(self, ctx: commands.Context, url: str = None):
        if not await self.valid(ctx, url):
            return

        await self.cleanup()

        key = str(ctx.author.id)
        if key in self.handlers:
            if self.handlers[key].is_busy():
                await self.status(ctx)
                return
            elif not self.handlers[key].is_closed:
                self.handlers[key].close()

        handler = DownloadHandler(self.bot, ctx)
        self.handlers[key] = handler
        handler.process(url)

    @staticmethod
    async def valid(ctx: commands.Context, url: str = None) -> bool:
        if ctx.author.bot:
            await ctx.send("Download is not allowed with bots")
        elif url is None:
            await ctx.send(
                "Please confirm your request to the following format:\n"
                "`>> download <required:url>`"
            )
        elif not url_helper.is_url(url):
            await ctx.send("The url provided is not valid.\n")
        else:
            return True

        return False

    async def cleanup(self):
        current_time = datetime.now()

        for key, handler in self.handlers.items():
            if handler.is_closed:
                self.handlers[key] = None
            elif handler.is_expired(current_time):
                handler.close()
                self.handlers[key] = None
