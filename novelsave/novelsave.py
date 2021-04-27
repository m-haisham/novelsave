from pathlib import Path
from typing import Union

import browser_cookie3
import requests
from requests.cookies import RequestsCookieJar

from novelsave.models import Chapter
from .concurrent import ConcurrentActionsController
from .database import NovelData, CookieDatabase
from .database.config import UserConfig
from .epub import NovelEpub
from .exceptions import ChapterException
from .logger import NovelLogger
from .metasources import parse_metasource
from .models import MetaData
from .sources import parse_source
from .ui import Loader, ConsolePrinter, PrinterPrefix


class NovelSave:
    IS_CHAPTERS_UPDATED = 'is_cu'

    def __init__(self, url, username=None, password=None, verbose=False):

        self.url = url
        self.username = username
        self.password = password

        self.user = UserConfig.instance()

        # initialize writers
        self.console = ConsolePrinter(verbose)
        NovelLogger.instance = NovelLogger(self.user.path, self.console)

        self.source = parse_source(self.url)
        self.cookies = CookieDatabase(self.user.path)
        self.netloc_slug = self.source.source_folder_name()
        self.db, self.path = self.open_db()

    def update(self, force_cover=False):

        self.console.print('Retrieving novel info...')
        self.console.print(self.url)
        novel, chapters = self.source.novel(self.url)

        self.console.print(f'Found {len(chapters)} chapters')

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

        self.console.print(
            f'Pending {len(pending)} chapters',
            f'| {pending[0].title}' if len(pending) == 1 else '',
            prefix=PrinterPrefix.SUCCESS
        )

    def metadata(self, url, force=False):
        # normalize url
        url = url.rstrip('/')

        meta_source = parse_metasource(url)

        # check caching
        novel = self.db.novel.parse()
        if not force and novel.meta_source == url:
            return

        # set meta_source for novel
        self.db.novel.put('meta_source', url)

        self.console.print('Retrieving metadata...')
        self.console.print(url)

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
            self.console.print("'limit' must be greater than 0", prefix=PrinterPrefix.ERROR)

        pending = self.db.pending.all()
        if not pending:
            self.console.print('No pending chapters')
            return

        pending.sort(key=lambda c: c.index)

        # limiting number of chapters downloaded
        if limit is not None and limit < len(pending):
            pending = pending[:limit]

        # some useful information
        if len(pending) == 1:
            additive = str(pending[0].index)
        else:
            additive = f'{pending[0].index} - {pending[-1].index}'
        self.console.print(f'Downloading {len(pending)} chapters | {additive}...')

        with Loader(desc=f'Populating tasks ({len(pending)})', should_draw=self.console.verbose) \
                as loader:

            value = 0
            total = len(pending)

            # initialize controller
            controller = ConcurrentActionsController(min(thread_count, len(pending)), task=self.task)
            for chapter in pending:
                controller.add(chapter)

            # set new downloads flag to true
            self.db.misc.put(self.IS_CHAPTERS_UPDATED, True)

            # desc is updated to show that tasks have been populated
            # and that script is in download faze
            loader.update(desc='')

            # start downloading
            for result in controller.iter():
                # debug
                # brush.print(controller.queue_out.qsize())
                # brush.print(f'{chapter.no} {chapter.title}')

                # update brush
                if self.console.verbose:
                    value += 1
                    loader.update(value=value / total, desc=f'{chapter.url} [{value}/{total}]')

                if type(result) is Chapter:
                    chapter = result

                    self.db.chapters.put(chapter)

                    # at last remove chapter from pending
                    self.db.pending.remove(chapter.url)
                elif type(result) is ChapterException:
                    loader.print(f'{PrinterPrefix.WARNING} [{result.type}] {result.message}')
                else:
                    loader.print(f'{PrinterPrefix.WARNING} {str(result)}')

        if self.console.verbose:
            pending = self.db.pending.all()
            if len(pending) > 0:
                self.console.print(f'Download finished with {len(pending)} '
                                   f'chapter{"s" if len(pending) > 0 else ""} pending')

        # ensure all operations are done
        self.db.chapters.flush()

    def create_epub(self, force=False):
        self.console.print('Packing epub...', verbose=True)

        # retrieve metadata
        novel = self.db.novel.parse()
        novel.meta = self.db.metadata.all()

        # this limits metadata to an external source should it be provided
        # using metadata from both sources causes duplicate entries
        if novel.meta_source:
            novel.meta = self.db.metadata.search_where('src', MetaData.SOURCE_EXTERNAL)

        chapters = self.db.chapters.all()
        if not chapters:
            self.console.print('Aborted. No chapters downloaded', prefix=PrinterPrefix.ERROR)
            return

        epub = NovelEpub(
            novel=novel,
            cover=self.cover_path(),
            chapters=chapters,
            save_path=self.path,
        )

        # get new downloads flag
        is_updated = self.db.misc.get(self.IS_CHAPTERS_UPDATED, default=False)

        # check flags and whether the epub already exists
        if not is_updated and not force and epub.path.exists():
            self.console.print('Aborted. No changes to chapter database', prefix=PrinterPrefix.ERROR)
            return

        epub.create()

        # reset new downloads flag
        self.db.misc.put(self.IS_CHAPTERS_UPDATED, False)

        self.console.print(f'Saved to {epub.path}', prefix=PrinterPrefix.SUCCESS)

    def login(self, cookie_browser: Union[str, None] = None, force=False):

        # retrieve cookies from browser
        if cookie_browser:
            # retrieve cookiejar of the selected browser
            try:
                cookies = getattr(browser_cookie3, cookie_browser)()
            except AttributeError:
                raise ValueError(f"browser '{cookie_browser}' not recognised; must be of either ['chrome', "
                                 f"'firefox', 'chromium', 'opera', 'edge', ]")

            # filter cookie domains
            cj = RequestsCookieJar()
            for c in cookies:
                if c.domain in self.source.cookie_domains:
                    cj.set(c.name, c.value, domain=c.domain, path=c.path)

            # set cookies jar to be used by source
            self.source.set_cookies(cj)
            self.console.print(f'Set cookiejar with {len(cj)} cookies', prefix=PrinterPrefix.SUCCESS, verbose=True)
        else:
            if force:
                self._login_and_persist()
            else:
                # get existing cookies and check if they are expired
                # expired cookies are discarded
                existing_cookies = self.cookies.select(self.source.cookie_domains)
                if self.cookies.check_expired(existing_cookies):
                    self._login_and_persist()
                else:
                    # if they aren't expired add the existing cookies request session
                    self.source.set_cookies(existing_cookies)

            self.console.print(f'Login successful', prefix=PrinterPrefix.SUCCESS, verbose=True)

    def _login_and_persist(self):
        """
        Delete existing cookies and replace with new received from via fresh login
        """
        # remove existing cookies
        self.cookies.delete(self.source.cookie_domains)

        # source specific login
        self.source.login(self.username, self.password)

        # set new cookies
        self.cookies.insert(self.source.session.cookies)

    def open_db(self):
        # trailing slash adds nothing
        path = Path(self.user.directory.get()) / Path(self.netloc_slug) / self.source.novel_folder_name(self.url)

        return NovelData(path), path

    def cover_path(self):
        return self.db.path.parent / Path('cover.jpg')

    def task(self, partial_c) -> Union[Chapter, Exception]:
        try:
            ch = self.source.chapter(partial_c.url)
        except Exception as e:
            return e

        ch.index = partial_c.index
        ch.title = ch.title or partial_c.title
        ch.volume = partial_c.volume

        return ch
