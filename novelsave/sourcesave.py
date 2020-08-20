from pathlib import Path

from . import Epub
from .database import NovelData
from .sources import WuxiaWorldCo
from .template import NovelSaveTemplate
from .ui import Loader, UiTools


class SourceNovelSave(NovelSaveTemplate):
    def __init__(self, url):
        super(SourceNovelSave, self).__init__(url, None, None)

        self.db = self.open_db()
        self.source = self.parse_source()

    def update(self):
        # scrape website, get novel info and toc
        with Loader('Scraping novel'):
            novel, chapters = self.source.novel(self.url)

        # download cover
        data = UiTools.download(novel.thumbnail, desc=f'Downloading cover {novel.thumbnail}')
        with self.cover_path().open('wb') as f:
            f.write(data.getbuffer())

        # update novel information
        with Loader('Update novel'):
            self.db.novel.set(novel)

        # update_pending
        with Loader('Update pending'):
            saved_urls = [chapter.url for chapter in self.db.chapters.all()]

            # so that downloads are ascending
            pending = list({chapter.url for chapter in sorted(chapters, key=lambda c: c.no)}.difference(saved_urls))

            self.db.pending.truncate()
            self.db.pending.insert_all(
                pending,
                check=False
            )

    def download(self):
        pending = self.db.pending.all()
        if not pending:
            print('[✗] No pending chapters')
            return

        with Loader('Init', value=0, total=len(pending)) as brush:
            for i, url in enumerate(pending):
                # update brush
                brush.value += 1

                prefix = f'[{brush.value}/{brush.total}]'
                brush.desc = f'{prefix} {url}'

                # get data
                chapter = self.source.chapter(url)
                self.db.chapters.put(chapter)

                # at last remove chapter from pending
                self.db.pending.remove(url)

    def create_epub(self):
        with Loader('Create epub'):
            Epub().create(
                novel=self.db.novel.parse(),
                cover=self.cover_path(),
                volumes={},
                chapters=self.db.chapters.all(),
                save_path=self.db.path.parent
            )

    def open_db(self):
        return NovelData(self.url)

    def cover_path(self):
        return self.db.path.parent / Path('cover.jpg')

    def parse_source(self):
        """
        create source object to which the url belongs to

        :return: source object
        """
        for source in [WuxiaWorldCo]:
            if source.of(self.url):
                return source()

        raise ValueError(f'"{self.url}" does not belong to any available source')