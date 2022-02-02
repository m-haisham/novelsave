import shutil
from concurrent import futures
from pathlib import Path
from typing import List, Iterable

import nextcord
import requests
from dependency_injector.wiring import Provide
from loguru import logger
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

from novelsave.core.dtos import NovelDTO
from novelsave.core.entities.novel import Novel
from novelsave.core.services.cloud.filehost import BaseCloudFileHost
from novelsave.core.services.packagers import BasePackager
from novelsave.core.services.source import BaseSourceGateway
from novelsave.exceptions import SourceNotFoundException
from novelsave.utils.helpers import url_helper, string_helper
from .. import utils
from ..checks import assert_check, is_direct_only
from ..decorators import session_task
from ..session import SessionFragment, SessionHandler


class DownloadHandler(SessionFragment):
    filehost: BaseCloudFileHost = Provide["cloud.filehost"]

    def __init__(self, *args, **kwargs):
        super(DownloadHandler, self).__init__(*args, **kwargs)

        self.value = 0
        self.total = 0

    def is_busy(self) -> bool:
        return any(
            self.session.state == state
            for state in [self.info_state, self.download_state, self.packaging_state]
        )

    async def info_state(self, intr: Interaction):
        await intr.send("I'm busy retrieving novel information.")

    async def download_state(self, intr: Interaction):
        await intr.send(
            f"The current download progress is {self.value} of {self.total}."
        )

    async def packaging_state(self, intr: Interaction):
        await intr.send("I'm currently packaging the novel.")

    @session_task()
    def download(self, url: str, targets: List[str]):
        self.session.state = self.info_state

        try:
            source_gateway = self.session.source_service().source_from_url(url)
        except SourceNotFoundException:
            self.session.send_sync(utils.error("This website is not yet supported."))
            self.session.send_sync(
                "You can request a new source by creating an issue at "
                "<https://github.com/mensch272/novelsave/issues/new/choose>"
            )
            return

        try:
            packagers = self.session.packager_provider().filter_packagers(targets)
        except ValueError as e:
            self.session.send_sync(utils.error(str(e)))
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

        novel_service = self.session.novel_service()

        novel = novel_service.insert_novel(novel_dto)
        novel_service.insert_chapters(novel, novel_dto.volumes)
        novel_service.insert_metadata(novel, novel_dto.metadata)

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
            self.session.send_sync(utils.error("Connection terminated unexpectedly."))

    def download_thumbnail(self, novel: Novel):
        if novel.thumbnail_url is None:
            logger.debug(f"No thumbnail url found for '{novel.title}'.")
            return

        self.session.send_sync(f"Downloading thumbnail <{novel.thumbnail_url}>…")
        try:
            response = requests.get(novel.thumbnail_url)
        except requests.ConnectionError:
            self.session.send_sync(utils.error("Connection terminated unexpectedly."))
            return

        if not response.ok:
            self.session.send_sync(
                utils.error(f"{response.status_code} {response.reason}")
            )
            return

        path_service = self.session.path_service()
        novel_service = self.session.novel_service()

        thumbnail_path = path_service.thumbnail_path(novel)
        novel_service.set_thumbnail_asset(
            novel, path_service.relative_to_data_dir(thumbnail_path)
        )

        thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
        self.session.file_service().write_bytes(thumbnail_path, response.content)

        size = string_helper.format_bytes(len(response.content))
        self.session.send_sync(f"Downloaded and saved thumbnail image ({size}).")

    def download_chapters(self, novel: Novel, source_gateway: BaseSourceGateway):
        novel_service = self.session.novel_service()

        chapters = novel_service.get_pending_chapters(novel, -1)
        if not chapters:
            logger.info("Skipped chapter download as none are pending.")
            return

        self.session.send_sync(
            f"Downloading {len(chapters)} chapters using {self.session.thread_count - 1} threads…"
        )

        self.total = len(chapters)
        self.value = 1

        dto_adapter = self.session.dto_adapter()
        asset_service = self.session.asset_service()

        download_futures = [
            self.session.executor.submit(
                source_gateway.update_chapter_content,
                dto_adapter.chapter_to_dto(c),
            )
            for c in chapters
        ]

        for chapter in futures.as_completed(download_futures):
            try:
                chapter_dto = chapter.result()
            except Exception as e:
                logger.exception(e)
                continue

            chapter_dto.content = asset_service.collect_assets(novel, chapter_dto)
            novel_service.update_content(chapter_dto)

            logger.debug(
                f"Chapter content downloaded: '{chapter_dto.title}' ({chapter_dto.index})"
            )

            self.value += 1

    def package(self, novel: Novel, packagers: Iterable[BasePackager]):
        formats = ", ".join(p.keywords()[0] for p in packagers)
        self.session.send_sync(f"Packing the novel into the formats: {formats}…")

        for packager in packagers:
            output = packager.package(novel)
            if output.is_dir():
                self.session.send_sync(f"Archiving {output.name}…")
                archive = shutil.make_archive(str(output), "zip", str(output))
                output = Path(archive)

            # discord does not allow uploads greater than 8mb
            # hence, they are relegated to a third-party
            if output.stat().st_size <= 7.99 * 1024 * 1024:
                self.session.send_sync(f"Uploading {output.name}…")
                self.session.send_sync(file=nextcord.File(output, output.name))
            else:
                self.session.send_sync(
                    f"File is bigger than 8Mb, uploading to {self.filehost.name()}…"
                )

                try:
                    url = self.filehost.upload(
                        output, "An upload by novelsave discord bot"
                    )
                    self.session.send_sync(url)
                except Exception as e:
                    logger.exception(e)
                    self.session.send_sync(
                        utils.error(f"Failed to upload file.\nError: {e}")
                    )


class Download(commands.Cog):
    """This controls download"""

    session_handler: SessionHandler = Provide["session.session_handler"]

    @nextcord.slash_command(
        description="Start a new download session", force_global=True
    )
    async def download(
        self,
        intr: Interaction,
        url: str = SlashOption(
            description="The absolute url pointing to the novel", required=True
        ),
        target1: str = SlashOption(
            description="The packaging target (1)", default="epub", required=False
        ),
        target2: str = SlashOption(
            description="The packaging target (2)", default="", required=False
        ),
        target3: str = SlashOption(
            description="The packaging target (3)", default="", required=False
        ),
    ):
        """Start a new download session

        :param intr: Command interaction
        :param url: The absolute url pointing to the novel
        :param target1: The packaging target (1)
        :param target2: The packaging target (2)
        :param target3: The packaging target (3)
        """
        if not await assert_check(intr, is_direct_only):
            return

        targets = {
            target.strip()
            for target in (target1, target2, target3)
            if type(target) == str and target.strip()
        }

        if not await self.valid(intr, url):
            return

        session = self.session_handler.get_or_create(intr)
        await session.run(
            intr,
            DownloadHandler.download,
            url,
            targets,
            message=utils.task(f"Download ({url=}, {targets=})"),
        )

    @staticmethod
    async def valid(intr: Interaction, url: str = None) -> bool:
        if intr.user.bot:
            await intr.send(utils.error("Download is not allowed with bots"))
        elif not url_helper.is_url(url):
            await intr.send(utils.error("The url provided is not valid."))
        else:
            return True

        return False
