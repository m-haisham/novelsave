import json
from pathlib import Path
from typing import Tuple, List, Dict

import lxml.html
from ebooklib import epub
from loguru import logger

from novelsave.core.entities.novel import Novel, Chapter, MetaData, NovelUrl
from novelsave.core.services import BaseNovelService
from novelsave.core.services.compilers import BaseCompiler

from lxml.html import builder as E

from novelsave.core.services.source import BaseSourceGatewayProvider
from novelsave.utils.helpers import string_helper


class EpubCompiler(BaseCompiler):

    def __init__(
            self,
            novels_dir: Path,
            novel_service: BaseNovelService,
            source_provider: BaseSourceGatewayProvider,
    ):
        self.novels_dir = novels_dir
        self.novel_service = novel_service
        self.source_provider = source_provider

    def keywords(self) -> Tuple[str]:
        return 'epub',

    def compile(self, novel: Novel):
        logger.debug(f'Preparing to compile to epub (novel.id={novel.id}, novel.title={novel.title})')

        urls = self.novel_service.get_urls(novel)
        logger.debug(f'Preparing to compile to epub (urls={len(urls)})')

        volumes = self.novel_service.get_volumes_with_chapters(novel)
        chapter_count = len([c for cl in volumes.values() for c in cl])
        logger.debug(f'Preparing to compile to epub (volumes={len(volumes)}, chapters={chapter_count})')

        metadata = self.novel_service.get_metadata(novel)
        logger.debug(f'Preparing to compile to epub (metadata={len(metadata)})')

        book = epub.EpubBook()
        book.set_identifier(str(novel.id))
        book.set_title(novel.title)
        book.set_language(novel.lang)
        book.add_author(novel.author)
        logger.debug(
            f'Bound attributes to epub (id={novel.id}, title={novel.title}, lang={novel.lang}, author={novel.author})')

        if novel.synopsis:
            book.add_metadata('DC', 'synopsis', novel.synopsis)
            logger.debug(f'Bound attributes to epub (synopsis={novel.synopsis[:min(30, len(novel.synopsis))]}…)')
        else:
            logger.debug(f'Bound attributes to epub (synopsis=None')

        for data in metadata:
            book.add_metadata(data.namespace, data.name, data.value, json.loads(getattr(data, 'others', '{}')))
        logger.debug(f'Bound attributes to epub (metadata.count={len(metadata)})')

        book_preface = self.preface_html(novel, urls, metadata)
        book.add_item(book_preface)
        logger.debug(f'Added pages to epub (pages.count=1, page=preface)')

        book_chapters = {}
        for volume, chapters in volumes.items():
            volume_tuple = (volume.index, volume.name)
            book_chapters[volume_tuple] = []

            for chapter in sorted(chapters, key=lambda c: c.index):
                epub_chapter = self.chapter_html(novel, chapter)
                book.add_item(epub_chapter)
                book_chapters[volume_tuple].append(epub_chapter)

        logger.debug(f'Added pages to epub (pages.count={chapter_count})')

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

        path = self.save_path(novel)
        path.parent.mkdir(parents=True, exist_ok=True)

        epub.write_epub(path, book, {})
        logger.debug(f'Saved epub file (loc="{path}")')

        return path

    def save_path(self, novel: Novel):
        url = self.novel_service.get_primary_url(novel)
        source_gateway = self.source_provider.source_from_url(url)

        source_folder_name = source_gateway.source_name() if source_gateway else ''
        logger.debug(f'Retrieved source name for epub file (source={source_gateway.source_name() if source_gateway else None})')

        novel_name_slug = string_helper.slugify(novel.title, "_")

        return self.novels_dir / source_folder_name / novel_name_slug / f'{novel_name_slug}.epub'

    def chapter_html(self, novel: Novel, chapter: Chapter) -> epub.EpubHtml:
        content = f'<h1>{chapter.title}</h1>{chapter.content}'
        file_name = f'{str(chapter.index).zfill(4)}.xhtml'

        return epub.EpubHtml(
            title=chapter.title,
            content=content,
            file_name=file_name,
            lang=novel.lang,
        )

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
            section = E.DIV(
                E.H4('Synopsis'),
                E.DIV(
                    ', '.join([item.value for item in items]),
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
