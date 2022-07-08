import shutil
from functools import lru_cache
from pathlib import Path
from typing import List, Dict

from bs4 import BeautifulSoup
from loguru import logger

from novelsave.core.entities.novel import Novel, MetaData
from novelsave.core.services import (
    BaseNovelService,
    BaseFileService,
    BasePathService,
)
from novelsave.core.services.packagers import BasePackager
from novelsave.utils.helpers import metadata_helper


class TextPackager(BasePackager):
    endl = "\n"

    def __init__(
        self,
        novel_service: BaseNovelService,
        file_service: BaseFileService,
        path_service: BasePathService,
    ):
        self.novel_service = novel_service
        self.file_service = file_service
        self.path_service = path_service

    @property
    def priority(self):
        return 1

    def keywords(self) -> List[str]:
        return ["text"]

    def package(self, novel: Novel) -> Path:
        urls = self.novel_service.get_urls(novel)
        volumes = self.novel_service.get_volumes_with_chapters(novel)
        chapter_count = len([c for cl in volumes.values() for c in cl])
        metadata = self.novel_service.get_metadata(novel)
        logger.debug(
            f"Preparing to package to epub (id={novel.id}, title='{novel.title}', volumes={len(volumes)}, "
            f"chapters={chapter_count}, metadata={len(metadata)})"
        )

        folder = self.destination(novel)
        if folder.exists():
            for path in folder.iterdir():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()

            logger.debug(
                f"Removed existing content in target folder (folder='{self.path_service.relative_to_novel_dir(folder)}')"
            )

        folder.mkdir(parents=True, exist_ok=True)

        with (folder / "_preface.txt").open("w", encoding="utf-8") as f:
            f.write(self.preface(novel, metadata, urls))

        logger.debug("Written novel information to file (file='_preface.txt').")

        for volume, chapters in volumes.items():
            for chapter in chapters:
                volume_prefix = (
                    ("v" + str(volume.index).zfill(2)) if volume.index >= 0 else ""
                )
                filename = volume_prefix + "c" + str(chapter.index).zfill(4) + ".txt"
                with (folder / filename).open("w", encoding="utf-8") as f:
                    f.write(self.chapter(volume, chapter))

        logger.debug(f"Written chapter content to text files (count={chapter_count})")

        return folder

    @lru_cache(maxsize=1)
    def destination(self, novel: Novel):
        path = self.path_service.novel_save_path(novel)
        return path / f"{path.name} (text)"

    def preface(self, novel, metadata, sources) -> str:
        text = ""

        text += novel.title + self.endl
        text += "by " + (novel.author or "Unknown") + self.endl
        text += self.endl
        text += "Synopsis = " + self.endl
        for line in novel.synopsis.splitlines():
            text += "   " + line.strip() + self.endl

        text += self.endl

        meta_by_name: Dict[str, List[MetaData]] = {}
        for item in metadata:
            meta_by_name.setdefault(item.name, []).append(item)

        for name, metas in meta_by_name.items():
            text += (
                name.capitalize()
                + " = "
                + ", ".join(metadata_helper.display_value(meta) for meta in metas)
                + self.endl * 2
            )

        text += "Sources = " + self.endl
        for source in sources:
            text += "   " + source.url.strip() + self.endl

        return text

    def chapter(self, volume, chapter):
        volume_prefix = volume.name if volume.index >= 0 else ""

        text = ""
        text += volume_prefix + chapter.title + self.endl
        text += self.endl

        soup = BeautifulSoup(chapter.content, "lxml")
        for line in soup.text.splitlines():
            if line.strip():
                text += line.strip() + self.endl + self.endl

        return text
