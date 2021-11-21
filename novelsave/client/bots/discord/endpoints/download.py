import asyncio
import functools
import logging
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Dict, Callable, Coroutine, List, Iterable

import nextcord
import requests
from dependency_injector.wiring import inject, Provide
from loguru import logger
from nextcord.ext import commands

from novelsave import migrations
from novelsave.containers import Application
from novelsave.core.dtos import NovelDTO
from novelsave.core.entities.novel import Novel
from novelsave.core.services import (
    BaseNovelService,
    BasePathService,
    BaseAssetService,
    BaseFileService,
)
from novelsave.core.services.packagers import BasePackagerProvider, BasePackager
from novelsave.core.services.source import BaseSourceService, BaseSourceGateway
from novelsave.exceptions import SourceNotFoundException
from novelsave.utils.adapters import DTOAdapter
from novelsave.utils.helpers import url_helper, string_helper
from .. import config, checks, mfmt
from ..containers import DiscordApplication

DownloadState = Callable[[commands.Context], Coroutine]


def ensure_close(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        self = args[0]

        result = None
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            if not self.is_closed:
                self.send_sync(f"`❗ {str(e).strip()}`")

            logging.exception(e)

        if not self.is_closed:
            self.close_and_inform()

        return result

    return wrapped


class DownloadHandler:
    application: Application
    source_service: BaseSourceService
    novel_service: BaseNovelService
    path_service: BasePathService
    dto_adapter: DTOAdapter
    asset_service: BaseAssetService
    file_service: BaseFileService
    packager_provider: BasePackagerProvider
    close_session: Callable[[], None]

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
        self.application = Application()
        self.application.config.from_dict(self.config())

        # acquire services
        self.source_service = self.application.services.source_service()
        self.novel_service = self.application.services.novel_service()
        self.path_service = self.application.services.path_service()
        self.dto_adapter = self.application.adapters.dto_adapter()
        self.asset_service = self.application.services.asset_service()
        self.file_service = self.application.services.file_service()
        self.packager_provider = self.application.packagers.packager_provider()

        # migrate database to latest schema
        migrations.migrate(self.application.config.get("infrastructure.database.url"))

    def close_session(self):
        self.application.infrastructure.session().close()
        self.application.infrastructure.session_factory().close_all()
        self.application.infrastructure.engine().dispose()

    def config(self):
        temp: dict = config.app()

        config_dir = temp["config"]["dir"] / str(self.ctx.author.id)
        schema, url = temp["infrastructure"]["database"]["url"].split(
            ":///", maxsplit=1
        )

        temp.update(
            {
                "config": {
                    "dir": config_dir,
                    "file": config_dir / temp["config"]["file"].name,
                },
                "novel": {
                    "dir": config_dir / "novels",
                },
                "data": {
                    "dir": config_dir / "data",
                },
                "infrastructure": {
                    "database": {
                        "url": f"{schema}:///{str(config_dir / 'data.sqlite')}",
                    },
                },
            }
        )

        shutil.rmtree(config_dir, ignore_errors=True)
        config_dir.mkdir(parents=True, exist_ok=True)

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
        await ctx.send("Just spinning things up.")

    async def info_state(self, ctx: commands.Context):
        await ctx.send("I'm busy retrieving novel information.")

    async def download_state(self, ctx: commands.Context):
        await ctx.send(
            f"The current download progress is {self.value} of {self.total}."
        )

    async def packaging_state(self, ctx: commands.Context):
        await ctx.send("I'm currently packaging the novel.")

    def send_sync(self, *args, **kwargs):
        logger.debug(
            " ".join(args) + ", " + " ".join(f"{k}={v}" for k, v in kwargs.items())
        )
        asyncio.run_coroutine_threadsafe(
            self.ctx.send(*args, **kwargs),
            self.bot.loop,
        ).result(timeout=3 * 60)

    def process(self, url: str, targets: List[str]):
        self.last_activity = datetime.now()
        self.executor.submit(self.start, url, targets)

    @ensure_close
    def start(self, url: str, targets: List[str]):
        self.state = self.info_state

        try:
            source_gateway = self.source_service.source_from_url(url)
        except SourceNotFoundException:
            self.send_sync(mfmt.error("This website is not yet supported."))
            self.send_sync(
                "You can request a new source by creating an issue at "
                "<https://github.com/mensch272/novelsave/issues/new/choose>"
            )
            return

        try:
            packagers = self.packager_provider.filter_packagers(targets)
        except ValueError as e:
            self.send_sync(mfmt.error(str(e)))
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
        self.download_chapters(novel, source_gateway)

        self.state = self.packaging_state
        self.package(novel, packagers)

    def retrieve_novel_info(
        self, source_gateway: BaseSourceGateway, url: str
    ) -> NovelDTO:
        try:
            return source_gateway.novel_by_url(url)
        except requests.ConnectionError:
            self.send_sync(mfmt.error("Connection terminated unexpectedly."))

    def download_thumbnail(self, novel: Novel):
        if novel.thumbnail_url is None:
            logger.debug(f"No thumbnail url found for '{novel.title}'.")
            return

        self.send_sync(f"Downloading thumbnail <{novel.thumbnail_url}>…")
        try:
            response = requests.get(novel.thumbnail_url)
        except requests.ConnectionError:
            self.send_sync(mfmt.error("Connection terminated unexpectedly."))
            return

        if not response.ok:
            self.send_sync(mfmt.error(f"{response.status_code} {response.reason}"))
            return

        thumbnail_path = self.path_service.thumbnail_path(novel)
        self.novel_service.set_thumbnail_asset(
            novel, self.path_service.relative_to_data_dir(thumbnail_path)
        )

        thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_service.write_bytes(thumbnail_path, response.content)

        size = string_helper.format_bytes(len(response.content))
        self.send_sync(f"Downloaded and saved thumbnail image ({size}).")

    def download_chapters(self, novel: Novel, source_gateway: BaseSourceGateway):
        chapters = self.novel_service.get_pending_chapters(novel, -1)
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
                self.send_sync(mfmt.error(f"Error downloading {chapter.url}."))
                logger.exception(e)
                continue

            chapter_dto.content = self.asset_service.collect_assets(novel, chapter_dto)
            self.novel_service.update_content(chapter_dto)

            logger.debug(
                f"Chapter content downloaded: '{chapter_dto.title}' ({chapter_dto.index})"
            )

            self.value += 1

    def package(self, novel: Novel, packagers: Iterable[BasePackager]):
        self.send_sync("Packing the novel into the formats: epub…")

        for packager in packagers:
            output = packager.package(novel)
            if output.is_file():
                self.send_sync(f"Uploading {output.name}…")
                self.send_sync(file=nextcord.File(output, output.name))
            else:
                self.send_sync(
                    mfmt.error(
                        f"I do not yet have support to upload directories ({packager.keywords()[0]})."
                    )
                )

    def close_and_inform(self):
        self.send_sync("Cleaning up temporary files…")
        self.close()

        self.send_sync("Session closed.")

    def close(self):
        if self.is_closed:
            raise ValueError("This download session is already closed.")

        self.executor.shutdown(wait=False, cancel_futures=True)
        self.close_session()
        shutil.rmtree(self.path_service.config_path, ignore_errors=True)

        self.is_closed = True


class Download(commands.Cog):
    """This controls download sessions on a per user basis"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.handlers: Dict[str, DownloadHandler] = {}

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await checks.direct_only(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CheckFailure):
            await ctx.send(str(error))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(mfmt.error(str(error)))

        logger.exception(repr(error))

    @commands.command()
    async def status(self, ctx: commands.Context):
        """Show status of current download session"""
        if str(ctx.author.id) not in self.handlers:
            await ctx.send(mfmt.error("You have no active download session."))
            return

        handler = self.handlers[str(ctx.author.id)]
        if handler.state is None:
            await ctx.send(mfmt.error("You have no active download session."))
        else:
            await handler.state(ctx)

    @commands.command()
    async def download(self, ctx: commands.Context, url: str, targets: str = None):
        """Start a new download session"""
        targets = targets.lower().split(",") if targets is not None else ["epub"]
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
        handler.process(url, targets)

    @commands.command()
    async def cancel(self, ctx: commands.Context):
        """Cancel the current download session"""
        key = str(ctx.author.id)
        if key not in self.handlers:
            await ctx.send(mfmt.error("You have no active download session."))
            return

        handler = self.handlers[key]
        if handler.is_closed:
            await ctx.send(mfmt.error("You have no active download session."))
            del self.handlers[key]
            return

        handler.close_and_inform()

    @staticmethod
    async def valid(ctx: commands.Context, url: str = None) -> bool:
        if ctx.author.bot:
            await ctx.send(mfmt.error("Download is not allowed with bots"))
        elif url is None:
            await ctx.send(
                mfmt.error("Please confirm your request to the following format:")
            )
            await ctx.send(f"`{ctx.clean_prefix}download <required:url>`")
        elif not url_helper.is_url(url):
            await ctx.send(mfmt.error("The url provided is not valid."))
        else:
            return True

        return False

    async def cleanup(self):
        current_time = datetime.now()

        expired = []
        for key, handler in self.handlers.items():
            if handler.is_closed:
                expired.append(key)
            elif handler.is_expired(current_time):
                logger.debug(f"Closing expired session: {handler.ctx.author.id}.")
                handler.close()
                expired.append(key)

        for key in expired:
            del self.handlers[key]
