from pathlib import Path

import requests

from .concurrent import ConcurrentActionsController
from .database import NovelData
from .database.config import UserConfig
from .epub import NovelEpub
from .logger import NovelLogger
from .metasources import meta_sources
from .models import MetaData
from .sources import sources
from .tools import UiTools
from .ui import Loader


class NovelSave:
    verbose = False

    IS_CHAPTERS_UPDATED = 'is_cu'

    def __init__(self, url, username=None, password=None, directory=None):

        self.url = url
        self.username = username
        self.password = password
        self.user = UserConfig()

        # change path value
        if directory is not None:
            path = Path(directory).resolve().absolute()

            if not path.exists():
                path.mkdir(parents=True)
                UiTools.print_success(f'Created dir {path}')

            self.user.directory.put(str(path))

        # initialize logger
        NovelLogger.instance = NovelLogger(self.user.directory.get())

        self.source = self.parse_source()
        self.netloc_slug = self.source.source_folder_name()
        self.db, self.path = self.open_db()

    def update(self, force_cover=False):

        UiTools.print_info('Retrieving novel info...')
        UiTools.print_info(self.url)
        novel, chapters = self.source.novel(self.url)

        UiTools.print_info(f'Found {len(chapters)} chapters')

        if (force_cover or not self.cover_path().exists()) and novel.thumbnail:
            # download cover
            response = requests.get(novel.thumbnail)
            with self.cover_path().open('wb') as f:
                f.write(response.content)

        # update novel information
        self.db.novel.set(novel)

        # update metadata
        for metadata in novel.meta:
            self.db.metadata.put(metadata)

        # update_pending
        saved = self.db.chapters.all()
        pending = list(set(chapters).difference(saved))

        self.db.pending.truncate()
        self.db.pending.put_all(pending)

        UiTools.print_success(f'Pending {len(pending)} chapters',
                              f'| {pending[0].no} {pending[0].title}' if len(pending) == 1 else '')

    def metadata(self, url, force=False):
        # normalize url
        url = url.rstrip('/')

        meta_source = self.parse_metasource(url)

        # check caching
        novel = self.db.novel.parse()
        if not force and novel.meta_source == url:
            return

        # set meta_source for novel
        self.db.novel.put('meta_source', url)

        UiTools.print_info('Retrieving metadata...')
        UiTools.print_info(url)

        # remove previous external metadata
        self.remove_metadata(with_source=False)

        # update metadata
        for metadata in meta_source.retrieve(url):
            # convert to object and mark as external metadata
            metadata.src = MetaData.SOURCE_EXTERNAL
            obj = vars(metadata)

            self.db.metadata.put(obj)

    def remove_metadata(self, with_source=True):
        self.db.metadata.remove_where('src', MetaData.SOURCE_EXTERNAL)

        # remove meta source link from novel
        if with_source:
            self.db.novel.put('meta_source', None)

    def download(self, thread_count=4, limit=None):
        # parameter validation
        if limit and limit <= 0:
            UiTools.print_error("'limit' must be greater than 0")

        pending = self.db.pending.all()
        if not pending:
            UiTools.print_error('No pending chapters')
            return

        pending.sort(key=lambda c: c.index)

        # limiting number of chapters downloaded
        if limit is not None and limit < len(pending):
            pending = pending[:limit]

        # some useful information
        if not self.verbose:
            if len(pending) == 1:
                additive = str(pending[0].index)
            else:
                additive = f'{pending[0].index} - {pending[-1].index}'

            UiTools.print_info(f'Downloading {len(pending)} chapters | {additive}...')

        with Loader(f'Populating tasks ({len(pending)})', value=0, total=len(pending), draw=self.verbose) as brush:

            # initialize controller
            controller = ConcurrentActionsController(thread_count, task=self.task)
            for chapter in pending:
                controller.add(chapter)

            # set new downloads flag to true
            self.db.misc.put(self.IS_CHAPTERS_UPDATED, True)

            # start downloading
            for chapter in controller.iter():
                # debug
                # brush.print(controller.queue_out.qsize())
                # brush.print(f'{chapter.no} {chapter.title}')

                # update brush
                if self.verbose:
                    brush.value += 1
                    brush.desc = f'[{brush.value}/{brush.total}] {chapter.url}'

                self.db.chapters.put(chapter)

                # at last remove chapter from pending
                self.db.pending.remove(chapter.url)

        # ensure all operations are done
        self.db.chapters.flush()

    def create_epub(self, force=False):
        UiTools.print_info('Packing epub...')

        # retrieve metadata
        novel = self.db.novel.parse()
        novel.meta = self.db.metadata.all()

        epub = NovelEpub(
            novel=novel,
            cover=self.cover_path(),
            chapters=self.db.chapters.all(),
            save_path=self.path,
        )

        # get new downloads flag
        is_updated = self.db.misc.get(self.IS_CHAPTERS_UPDATED, default=False)

        # check flags and whether the epub already exists
        if not is_updated and not force and epub.path.exists():
            UiTools.print_info('Aborted. No changes to chapter database')
            return

        epub.create()

        # reset new downloads flag
        self.db.misc.put(self.IS_CHAPTERS_UPDATED, False)

        UiTools.print_success(f'Saved to {epub.path}')

    def open_db(self):
        # trailing slash adds nothing
        path = Path(self.user.directory.get()) / Path(self.netloc_slug) / self.source.novel_folder_name(self.url)

        return NovelData(path), path

    def cover_path(self):
        return self.db.path.parent / Path('cover.jpg')

    def parse_source(self):
        """
        create source object to which the url belongs to

        :return: source object
        """
        for source in sources:
            if source.of(self.url):
                return source()

        raise TypeError(f'"{self.url}" does not belong to any available source')

    def parse_metasource(self, url):
        """
        create neta source object to which the url belongs to

        :return: meta source object
        """
        for source in meta_sources:
            if source.of(url):
                return source()

        raise TypeError(f'"{url}" does not belong to any available metadata source')

    def task(self, partialc):
        ch = self.source.chapter(partialc.url)
        ch.index = partialc.index
        ch.title = ch.title or partialc.title
        ch.volume = partialc.volume

        return ch
