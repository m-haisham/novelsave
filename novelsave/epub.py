import hashlib
from pathlib import Path

from ebooklib import epub
from yattag import Doc

from .tools import StringTools


class Epub:
    def create(self, novel, cover, volumes, chapters, save_path) -> Path:
        # parameter validation
        if not chapters:
            raise ValueError("'chapters' may not be 'None'")

        # prepare data
        chapters.sort(key=lambda c: c.order)

        book = epub.EpubBook()

        # id
        book.set_identifier(str(novel.id if hasattr(novel, 'id') else hashlib.md5(novel.title.encode('utf-8')).hexdigest()))
        book.set_title(novel.title)
        book.add_author(novel.author)

        # cover
        with cover.open('rb') as f:
            book.set_cover('cover.jpg', f.read())

        # volume mapper
        volume_map = {}
        for volume_key in volumes.keys():
            chs = volumes[volume_key]
            for ch in chs:
                volume_map[ch] = volume_key

        # create chapters
        book_chapters = {}
        for chapter in chapters:
            epub_chapter = self._epub_chapter(chapter)
            book.add_item(epub_chapter)

            try:
                volume = volume_map[chapter.id]
            except (AttributeError, KeyError):
                volume = '_default'

            if volume in book_chapters.keys():
                book_chapters[volume].append(epub_chapter)
            else:
                book_chapters[volume] = [epub_chapter]

        # table of contents
        if len(book_chapters.keys()) == 1:
            # no volume sections
            book.toc = list(book_chapters.values())[0]
        else:
            book.toc = (
                (epub.Section(name), tuple(chapters))
                for name, chapters in book_chapters.items()
            )

        # add default NCX and Nav file
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        book.spine = [c for volume in book_chapters.values() for c in volume]

        path = save_path / Path(f'{StringTools.slugify(novel.title)}.epub').resolve()
        epub.write_epub(path, book, {})

        return path

    def _epub_chapter(self, chapter):
        """
        create chapter xhtml

        :param chapter: novel chapter
        :return: chapter xhtml
        """
        prefix = f'{f"{StringTools.from_float(chapter.no)} " if chapter.no and chapter.no > 0 else ""}'
        title = f'{prefix}{chapter.title}'
        epub_chapter = epub.EpubHtml(title=title, file_name=f'{chapter.index}.xhtml', lang='en')

        # html content
        doc, tag, text = Doc().tagtext()
        with tag('h1'):
            text(title)

        # for the more neatly scraped
        if type(chapter.paragraphs) == list:
            for para in chapter.paragraphs:
                with tag('p'):
                    text(para)

        # those that are scraped as a single blob
        elif type(chapter.paragraphs) == str:
            doc.asis(chapter.paragraphs)

        epub_chapter.content = doc.getvalue()
        return epub_chapter
