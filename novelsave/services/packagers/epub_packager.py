import json
from functools import lru_cache
from pathlib import Path
from typing import Tuple, List, Dict
import mimetypes

import ebooklib
import lxml.html
from ebooklib import epub
from loguru import logger
from lxml.html import builder as E

from novelsave.core.entities.novel import Novel, Chapter, MetaData, NovelUrl, Asset
from novelsave.core.services import BaseNovelService, BasePathService, BaseFileService, BaseAssetService
from novelsave.core.services.packagers import BasePackager


class EpubPackager(BasePackager):
    def __init__(
            self,
            novel_service: BaseNovelService,
            file_service: BaseFileService,
            path_service: BasePathService,
            asset_service: BaseAssetService,
    ):
        self.novel_service = novel_service
        self.file_service = file_service
        self.path_service = path_service
        self.asset_service = asset_service

    def keywords(self) -> Tuple[str]:
        return 'epub',

    def package(self, novel: Novel):
        logger.debug(f'Preparing to package to epub (novel.id={novel.id}, novel.title={novel.title})')

        urls = self.novel_service.get_urls(novel)
        logger.debug(f'Preparing to package to epub (urls={len(urls)})')

        volumes = self.novel_service.get_volumes_with_chapters(novel)
        chapter_count = len([c for cl in volumes.values() for c in cl])
        logger.debug(f'Preparing to package to epub (volumes={len(volumes)}, chapters={chapter_count})')

        metadata = self.novel_service.get_metadata(novel)
        logger.debug(f'Preparing to package to epub (metadata={len(metadata)})')

        book = epub.EpubBook()
        book.set_identifier(str(novel.id))
        book.set_title(novel.title)
        book.set_language(novel.lang)
        book.add_author(novel.author)
        logger.debug(
            f'Bound attributes to epub (id={novel.id}, title={novel.title}, lang={novel.lang}, author={novel.author})')

        self.set_cover(book, novel)

        if novel.synopsis:
            book.add_metadata('DC', 'description', novel.synopsis)
            logger.debug(f'Bound attributes to epub (synopsis={novel.synopsis[:min(30, len(novel.synopsis))]}…)')
        else:
            logger.debug(f'Bound attributes to epub (synopsis=None')

        for data in metadata:
            book.add_metadata(data.namespace, data.name, data.value, json.loads(data.others))
        logger.debug(f'Bound attributes to epub (metadata.count={len(metadata)})')

        book_preface = self.preface_html(novel, urls, metadata)
        book.add_item(book_preface)
        logger.debug(f'Added pages to epub (pages.count=1, type=preface)')

        book_chapters = {}
        for volume, chapters in volumes.items():
            volume_tuple = (volume.index, volume.name)
            book_chapters[volume_tuple] = []

            for chapter in sorted(chapters, key=lambda c: c.index):
                epub_chapter = self.chapter_html(novel, chapter)
                book.add_item(epub_chapter)
                book_chapters[volume_tuple].append(epub_chapter)

        logger.debug(f'Added pages to epub (pages.count={chapter_count}, type=chapter)')

        self.add_assets(book, novel)

        # table of contents
        book.toc = [book_preface]
        if len(book_chapters.keys()) == 1:  # no volume sections
            book.toc += list(book_chapters.values())[0]
            logger.debug(f'Built table of content of epub (type=single_section)')
        else:
            book.toc += [
                (epub.Section(volume[1]), tuple(book_chapters[volume]))
                for volume in sorted(book_chapters.keys(), key=lambda k: k[0])
            ]
            logger.debug(f'Built table of content of epub (type=multiple_section)')

        # add default NCX and Nav file
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        logger.debug(f'Added default items to epub (items=[ncx, nav])')

        book.spine = [book_preface] + [c for volume in book_chapters.values() for c in volume]
        logger.debug(f'Built epub spine (count={len(book.spine)})')

        path = self.destination(novel)
        path.parent.mkdir(parents=True, exist_ok=True)

        epub.write_epub(path, book, {})
        logger.debug(f'Saved epub file (path="{path}")')

        return path

    @lru_cache(maxsize=1)
    def destination(self, novel: Novel):
        path = self.path_service.novel_save_path(novel)
        return path / (path.name + '.epub')

    def set_cover(self, book: epub.EpubBook, novel: Novel):
        cover = None
        if novel.thumbnail_path is not None:
            possible_cover = self.path_service.resolve_data_path(Path(novel.thumbnail_path))
            if possible_cover.exists() and possible_cover.is_file():
                cover = possible_cover

        if cover is None:
            logger.debug(f"Copying cover image aborted (path='{novel.thumbnail_path}', reason='file does not exist')")
            return

        book.set_cover(cover.name, self.file_service.read_bytes(cover))
        logger.debug(f"Copied cover image to epub (path='{novel.thumbnail_path}')")

    @lru_cache(1)
    def path_mapping(self, novel: Novel) -> Dict[int, str]:
        assets = self.asset_service.downloaded_assets(novel)

        return {
            asset.id: f'assets/{Path(asset.path).name}'
            for asset in assets
        }

    @lru_cache(1)
    def mapping_dict(self, novel: Novel):
        return self.asset_service.mapping_dict(self.path_mapping(novel))

    def chapter_html(self, novel: Novel, chapter: Chapter) -> epub.EpubHtml:
        content = self.asset_service.inject_assets(chapter.content, self.mapping_dict(novel))
        content_with_heading = f'<h1>{chapter.title}</h1>{content}'
        file_name = f'chapters/{str(chapter.index).zfill(4)}.xhtml'

        return epub.EpubHtml(
            title=chapter.title,
            content=content_with_heading,
            file_name=file_name,
            lang=novel.lang,
        )

    def add_assets(self, book: epub.EpubBook, novel: Novel):
        path_mapping = self.path_mapping(novel)

        assets = self.asset_service.downloaded_assets(novel)
        for asset in assets:
            file = self.path_service.resolve_data_path(asset.path)
            content = self.file_service.read_bytes(file)
            mimetype, encoding = mimetypes.guess_type(asset.path)

            image = epub.EpubItem(
                file_name=path_mapping[asset.id],
                media_type=mimetype,
                content=content,
            )

            book.add_item(image)

        logger.debug(f'Added assets to epub (count={len(assets)})')

    @staticmethod
    def metadata_display_value(data: MetaData):
        try:
            others = json.loads(data.others)
        except json.JSONDecodeError:
            others = {}

        others = [f'{key}={value}' for key, value in others.items()]
        postfix = f'(' + ', '.join(others) + ')' if others else ''

        return f'{data.value}{postfix}'

    def preface_html(self, novel: Novel, urls: List[NovelUrl], metadata: List[MetaData]) -> epub.EpubHtml:
        synopsis_section = E.DIV(
            E.H4('Synopsis'),
            E.DIV(
                *[E.P(para) for para in novel.synopsis.split('\n')],
                style="padding: 0 1rem",
            )
        )

        meta_by_name: Dict[str, List[MetaData]] = {}
        for item in metadata:
            meta_by_name.setdefault(item.name, []).append(item)

        metadata_sections = []
        for name, items in meta_by_name.items():
            item_strings = [self.metadata_display_value(item) for item in items]

            section = E.DIV(
                E.H4(name.capitalize()),
                E.DIV(
                    ', '.join(item_strings),
                    style="padding: 0 1rem",
                ),
            )

            metadata_sections.append(section)

        html = E.DIV(
            E.H1(novel.title, style="margin-bottom: 0;"),
            E.DIV(f'by: {novel.author}'),
            synopsis_section,
            *metadata_sections,
            E.DIV(
                E.H4('Sources'),
                E.DIV(
                    *[E.A(n_url.url, href=n_url.url) for n_url in urls],
                    style="padding: 0 1rem",
                )
            )
        )

        return epub.EpubHtml(
            title='Preface',
            file_name=f'preface.xhtml',
            content=lxml.html.tostring(html),
            lang=novel.lang,
        )
