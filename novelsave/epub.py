from pathlib import Path

from ebooklib import epub
from yattag import Doc


class Epub:
    def create(self, novel, cover, volumes, chapters, save_path):
        # prepare data
        chapters.sort(key=lambda c: c.no)

        book = epub.EpubBook()

        book.set_identifier(str(novel.id))
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
            book_chapter = epub.EpubHtml(title=chapter.title, file_name=f'chapter_{chapter.no}.xhtml', lang='en')

            book_chapter.content = self._chapter(chapter)
            book.add_item(book_chapter)

            volume = volume_map[chapter.id]
            if volume in book_chapters.keys():
                book_chapters[volume].append(book_chapter)
            else:
                book_chapters[volume] = [book_chapter]

        # table of contents
        book.toc = (
            *[
                (
                    epub.Section(name),
                    tuple(chapters)
                ) for name, chapters in book_chapters.items()
            ],
        )

        # add default NCX and Nav file
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        book.spine = ['nav', *[c for volume in book_chapters.values() for c in volume]]
        epub.write_epub(save_path / Path(novel.title + '.epub'), book, {})

    def _chapter(self, chapter):
        """
        create chapter xhtml

        :param chapter: novel chapter
        :return: chapter xhtml
        """
        doc, tag, text = Doc().tagtext()
        with tag('h1'):
            text(chapter.title)

        for para in chapter.paragraphs:
            with tag('p'):
                text(para)

        return doc.getvalue()
