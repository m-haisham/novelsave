from typing import List, Iterable

import nextcord
import requests
from dependency_injector.wiring import Provide
from loguru import logger
from nextcord.ext import commands

from novelsave.core.dtos import NovelDTO
from novelsave.core.entities.novel import Novel
from novelsave.core.services.packagers import BasePackager
from novelsave.core.services.source import BaseSourceGateway
from novelsave.exceptions import SourceNotFoundException
from novelsave.utils.helpers import url_helper, string_helper
from .. import checks, mfmt
from ..session import SessionFragment, ensure_close, SessionHandler


class DownloadHandler(SessionFragment):
    def __init__(self, *args, **kwargs):
        super(DownloadHandler, self).__init__(*args, **kwargs)

        self.value = 0
        self.total = 0

    def is_busy(self) -> bool:
        return any(
            self.session.state == state
            for state in [self.info_state, self.download_state, self.packaging_state]
        )

    async def info_state(self, ctx: commands.Context):
        await ctx.send("I'm busy retrieving novel information.")

    async def download_state(self, ctx: commands.Context):
        await ctx.send(
            f"The current download progress is {self.value} of {self.total}.\n"
            f"To cancel the current download, send `{ctx.clean_prefix}cancel`"
        )

    async def packaging_state(self, ctx: commands.Context):
        await ctx.send("I'm currently packaging the novel.")

    @ensure_close
    def download(self, url: str, targets: List[str]):
        self.session.state = self.info_state

        try:
            source_gateway = self.session.source_service.source_from_url(url)
        except SourceNotFoundException:
            self.session.send_sync(mfmt.error("This website is not yet supported."))
            self.session.send_sync(
                "You can request a new source by creating an issue at "
                "<https://github.com/mensch272/novelsave/issues/new/choose>"
            )
            return

        try:
            packagers = self.session.packager_provider.filter_packagers(targets)
        except ValueError as e:
            self.session.send_sync(mfmt.error(str(e)))
            return

        self.session.send_sync(f"Retrieving novel information from <{url}>…")
        novel_dto = self.retrieve_novel_info(source_gateway, url)
        if novel_dto is None:
            return

        chapter_count = len([c for v in novel_dto.volumes for c in v.chapters])
        self.session.send_sync(
            f"**{novel_dto.title.strip()}** by {novel_dto.author}, with {len(novel_dto.volumes)} "
            f"volumes of {chapter_count} chapters."
        )

        novel = self.session.novel_service.insert_novel(novel_dto)
        self.session.novel_service.insert_chapters(novel, novel_dto.volumes)
        self.session.novel_service.insert_metadata(novel, novel_dto.metadata)

        self.session.state = self.download_state
        self.download_thumbnail(novel)
        self.download_chapters(novel, source_gateway)

        self.session.state = self.packaging_state
        self.package(novel, packagers)

    def retrieve_novel_info(
        self, source_gateway: BaseSourceGateway, url: str
    ) -> NovelDTO:
        try:
            return source_gateway.novel_by_url(url)
        except requests.ConnectionError:
            self.session.send_sync(mfmt.error("Connection terminated unexpectedly."))

    def download_thumbnail(self, novel: Novel):
        if novel.thumbnail_url is None:
            logger.debug(f"No thumbnail url found for '{novel.title}'.")
            return

        self.session.send_sync(f"Downloading thumbnail <{novel.thumbnail_url}>…")
        try:
            response = requests.get(novel.thumbnail_url)
        except requests.ConnectionError:
            self.session.send_sync(mfmt.error("Connection terminated unexpectedly."))
            return

        if not response.ok:
            self.session.send_sync(
                mfmt.error(f"{response.status_code} {response.reason}")
            )
            return

        thumbnail_path = self.session.path_service.thumbnail_path(novel)
        self.session.novel_service.set_thumbnail_asset(
            novel, self.session.path_service.relative_to_data_dir(thumbnail_path)
        )

        thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
        self.session.file_service.write_bytes(thumbnail_path, response.content)

        size = string_helper.format_bytes(len(response.content))
        self.session.send_sync(f"Downloaded and saved thumbnail image ({size}).")

    def download_chapters(self, novel: Novel, source_gateway: BaseSourceGateway):
        chapters = self.session.novel_service.get_pending_chapters(novel, -1)
        if not chapters:
            logger.info("Skipped chapter download as none are pending.")
            return

        self.session.send_sync(f"Downloading {len(chapters)} chapters…")
        self.total = len(chapters)
        self.value = 1

        for chapter in chapters:

            try:
                chapter_dto = source_gateway.update_chapter_content(
                    self.session.dto_adapter.chapter_to_dto(chapter)
                )
            except Exception as e:
                self.session.send_sync(mfmt.error(f"Error downloading {chapter.url}."))
                logger.exception(e)
                continue

            chapter_dto.content = self.session.asset_service.collect_assets(
                novel, chapter_dto
            )
            self.session.novel_service.update_content(chapter_dto)

            logger.debug(
                f"Chapter content downloaded: '{chapter_dto.title}' ({chapter_dto.index})"
            )

            self.value += 1

    def package(self, novel: Novel, packagers: Iterable[BasePackager]):
        self.session.send_sync("Packing the novel into the formats: epub…")

        for packager in packagers:
            output = packager.package(novel)
            if output.is_file():
                self.session.send_sync(f"Uploading {output.name}…")
                self.session.send_sync(file=nextcord.File(output, output.name))
            else:
                self.session.send_sync(
                    mfmt.error(
                        f"I do not yet have support to upload directories ({packager.keywords()[0]})."
                    )
                )


class Download(commands.Cog):
    """This controls download"""

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
    async def download(self, ctx: commands.Context, url: str, targets: str = None):
        """Start a new download session

        :param ctx: Command context
        :param url: The absolute url pointing to the novel
        :param targets: The packaging targets
        """
        targets = targets.lower().split(",") if targets is not None else ["epub"]
        if not await self.valid(ctx, url):
            return

        self.session_handler.cleanup()
        session = await self.session_handler.get_or_create(ctx)
        await session.run(ctx, DownloadHandler.download, url, targets)

    @staticmethod
    async def valid(ctx: commands.Context, url: str = None) -> bool:
        if ctx.author.bot:
            await ctx.send(mfmt.error("Download is not allowed with bots"))
        elif url is None:
            await ctx.send(
                mfmt.error("Please confirm your request to the following format:")
            )
            await ctx.send(
                f"`{ctx.clean_prefix}download <required:url> <optional:targets>`"
            )
        elif not url_helper.is_url(url):
            await ctx.send(mfmt.error("The url provided is not valid."))
        else:
            return True

        return False
