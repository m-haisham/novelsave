import hashlib
from pathlib import Path

from ebooklib import epub

from .models import MetaData
from .utils.helpers import StringHelper


class NovelEpub:
    def __init__(self, novel, cover, chapters, save_path):
        self.novel = novel
        self.cover = cover
        self.chapters = chapters
        self.save_path = save_path

    def create(self):
        # attribute validation
        if not self.chapters:
            raise ValueError("'chapters' cannot be 'None'")

        # prepare data
        self.chapters.sort(key=lambda c: c.index)

        book = epub.EpubBook()

        # metadata
        book.set_identifier(str(self.novel.id if hasattr(self.novel, 'id') else hashlib.md5(self.novel.title.encode('utf-8')).hexdigest()))
        book.set_title(self.novel.title)
        book.set_language(self.novel.lang)
        book.add_author(self.novel.author)

        if self.novel.synopsis:
            book.add_metadata(MetaData.DEFAULT_NAMESPACE, 'synopsis', self.novel.synopsis)

        for data in self.novel.meta:
            book.add_metadata(data['namespace'], data['name'], data['value'], data['others'])

        book.add_metadata(MetaData.DEFAULT_NAMESPACE, 'source', self.novel.url)

        # cover
        if self.cover.exists() and self.cover.is_file():
            with self.cover.open('rb') as f:
                book.set_cover('cover.jpg', f.read())

        # create chapters
        book_preface = self._preface()
        book.add_item(book_preface)
        book_chapters = {}
        for chapter in self.chapters:
            epub_chapter = self._epub_chapter(chapter)
            book.add_item(epub_chapter)

            try:
                volume = tuple(chapter.volume) or (-1, '_default')
            except (AttributeError, TypeError, IndexError):
                volume = (-1, '_default')

            if volume in book_chapters.keys():
                book_chapters[volume].append(epub_chapter)
            else:
                book_chapters[volume] = [epub_chapter]

        # table of contents
        book.toc = [book_preface]
        if len(book_chapters.keys()) == 1:  # no volume sections
            book.toc += list(book_chapters.values())[0]
        else:
            book.toc += [
                (epub.Section(volume[1]), tuple(book_chapters[volume]))
                for volume in sorted(book_chapters.keys(), key=lambda k: k[0])
            ]

        # add default NCX and Nav file
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        book.spine = [book_preface] + [c for volume in book_chapters.values() for c in volume]

        epub.write_epub(self.path, book, {})

    @property
    def path(self):
        return self.save_path / Path(f'{StringHelper.slugify(self.novel.title)}.epub').resolve()

    def _epub_chapter(self, chapter):
        """
        create chapter xhtml

        :param chapter: novel chapter
        :return: chapter xhtml
        """
        prefix = f'{f"{StringHelper.from_float(chapter.no)} " if chapter.no and chapter.no > 0 else ""}'
        title = f'{prefix}{chapter.title}'
        epub_chapter = epub.EpubHtml(title=title, file_name=f'{chapter.index}.xhtml', lang=self.novel.lang)

        content = f'''<h1>{title}</h1>'''
        if type(chapter.paragraphs) == list:
            content += '<p>' + '</p><p>'.join(chapter.paragraphs) + '</p>'
        else:
            content += chapter.paragraphs

        epub_chapter.content = content

        return epub_chapter

    def _preface(self) -> epub.EpubHtml:

        content = f'''
            <h1 style="margin-bottom: 0;">{self.novel.title}</h1>
            <div>Writtten by: {self.novel.author}</div>
        '''

        if self.novel.synopsis:
            content += '<div style="margin-bottom: 0.2rem">'
            content += f'<h4 style="margin-bottom: 0.2rem">Synopsis:</h4>'
            for para in self.novel.synopsis.split('\n'):
                content += f'<p>{para.strip()}</p>'
            content += '</div>'

        meta = {}
        for item in self.novel.meta:
            try:
                meta[item['name']].append(item)
            except KeyError:
                meta[item['name']] = [item]

        for key, value in sorted(meta.items()):
            content += '<div style="margin-bottom: 0.2rem">'
            content += f'<h4 style="margin-bottom: 0.2rem">{key}:</h4>'

            values = []
            for item in value:
                postfix = ''
                if len(item.get('others', {})) > 0:
                    postfix = '(' + ', '.join([f'{key}={value}' for key, value in item.get('others', {}).items()]) + ')'

                values.append(f'{item["value"]} {postfix}')

            content += '<p>' + ', '.join(values) + '</p>'
            content += '</div>'

        content += f'<h4 style="margin-bottom: 0.2rem">Source:</h4>'
        content += f'<p><a href="{self.novel.url}">{self.novel.url}</a></p>'

        return epub.EpubHtml(title='Preface', file_name=f'preface.xhtml', content=content, lang=self.novel.lang)
