from pathlib import Path
from typing import Union

import browser_cookie3
import requests
from requests.cookies import RequestsCookieJar

from .concurrent import ConcurrentActionsController
from .database import NovelData, CookieDatabase
from .database.config import UserConfig
from .epub import NovelEpub
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

        self.user = UserConfig()

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
            self.console.print('No pending chapters', prefix=PrinterPrefix.ERROR)
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

        with Loader(f'Populating tasks ({len(pending)})', value=0, total=len(pending), draw=self.console.verbose) \
                as brush:

            # initialize controller
            controller = ConcurrentActionsController(min(thread_count, len(pending)), task=self.task)
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
                if self.console.verbose:
                    brush.value += 1
                    brush.desc = f'[{brush.value}/{brush.total}] {chapter.url}'

                self.db.chapters.put(chapter)

                # at last remove chapter from pending
                self.db.pending.remove(chapter.url)

        # ensure all operations are done
        self.db.chapters.flush()

    def create_epub(self, force=False):
        self.console.print('Packing epub...')

        # retrieve metadata
        novel = self.db.novel.parse()
        novel.meta = self.db.metadata.all()

        # this limits metadata to an external source should it be provided
        # using metadata from both sources causes duplicate entries
        if novel.meta_source:
            novel.meta = self.db.metadata.search_where('src', MetaData.SOURCE_EXTERNAL)

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
            self.console.print('Aborted. No changes to chapter database')
            return

        epub.create()

        # reset new downloads flag
        self.db.misc.put(self.IS_CHAPTERS_UPDATED, False)

        self.console.print(f'Saved to {epub.path}', prefix=PrinterPrefix.SUCCESS)

    def login(self, cookie_browser: Union[str, None] = None, force=False):

        # retrieve cookies from browser
        if cookie_browser:
            # retrieve cookiejar of the selected browser
            if cookie_browser in ['chrome', 'firefox', 'chromium', 'opera', 'edge', ]:
                cookies = getattr(browser_cookie3, cookie_browser)()
            else:
                raise ValueError(f"'{cookie_browser}' not recognised; must be of ['chrome', "
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

    def task(self, partial_c):
        ch = self.source.chapter(partial_c.url)
        ch.index = partial_c.index
        ch.title = ch.title or partial_c.title
        ch.volume = partial_c.volume

        return ch
