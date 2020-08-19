from pathlib import Path

from .novelsave import NovelSave

from .database import NovelBase
from .sources import WuxiaWorldCo
from .ui import Loader, UiTools


class SourceNovelSave(NovelSave):
    def __init__(self, url):
        super(SourceNovelSave, self).__init__(url, None, None)

        self.db = self.open_db()
        self.source = self.parse_source()

    def update(self):
        # scrape website, get novel info and toc
        with Loader('Scraping novel'):
            novel, chapters = self.source.novel(self.url)

        # download cover
        data = UiTools.download(novel.thumbnail, desc='Downloading cover')
        with self.cover_path().open('wb') as f:
            f.write(data)

        # update novel information
        with Loader('Update novel'):
            self.db.novel.set(novel)

        # update_pending
        with Loader('Update pending'):
            saved_urls = [chapter.url for chapter in self.db.chapters.all()]

            self.db.pending.truncate()
            self.db.pending.insert_all(
                list({chapter.url for chapter in chapters}.difference(saved_urls)),
                check=False
            )

    def download(self):
        pass

    def create_epub(self):
        pass

    def open_db(self):
        return NovelBase(self.url)

    def cover_path(self):
        return self.db.path.parent / Path('cover.jpg')

    def parse_source(self):
        return WuxiaWorldCo()