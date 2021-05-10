from pathlib import Path
from typing import Union

import browser_cookie3
import requests
from requests.cookies import RequestsCookieJar

from .database import NovelData, CookieDatabase, UserConfig
from .epub import NovelEpub
from .exceptions import ChapterException, UnsupportedBrowserException, CookieAuthException, DownloadLimitException
from .logger import NovelLogger
from .sources import parse_source, parse_metasource
from .models import Chapter, MetaData
from .utils.concurrent import ConcurrentActionsController
from .utils.ui import Loader, ConsoleHandler


class NovelSave:
    IS_CHAPTERS_UPDATED = 'is_cu'

    def __init__(self, url, no_input, username=None, password=None, plain=False):
        self.url = url
        self.username = username
        self.password = password

        self.user = UserConfig.instance()

        # initialize writers
        self.console = ConsoleHandler(plain, no_input)
        NovelLogger.instance = NovelLogger(self.user.path, self.console)

        self.source = parse_source(self.url)
        self.cookies = CookieDatabase(self.user.path)
        self.db, self.path = self.open_db()

    def update(self, force_cover=False):

        with self.console.line('Downloading webpage, ') as line:
            novel, chapters = self.source.novel(self.url)

            line.end(f'"{novel.title}" parsed with {len(chapters)} chapters.')

        with self.console.line('Downloading cover, ') as line:
            if (force_cover or not self.cover_path().exists()) and novel.thumbnail:

                # download cover
                response = requests.get(novel.thumbnail)
                with self.cover_path().open('wb') as f:
                    f.write(response.content)

                line.end(f'{len(response.content)} bytes, done.')
            else:
                if novel.thumbnail:
                    line.end('already downloaded, aborted.')
                else:
                    line.end('not provided, aborted.')

        with self.console.line('Updating novel information, ') as line:
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

            line.end(f'with {len(pending)} chapters pending, done.')

    def metadata(self, url, force=False):
        # normalize url
        url = url.rstrip('/')

        meta_source = parse_metasource(url)

        with self.console.line('Retrieving metadata, ') as line:
            # check caching
            novel = self.db.novel.parse()
            if not force and novel.meta_source == url:
                line.end('already exists, aborted.')
                return

            # set meta_source for novel
            self.db.novel.put('meta_source', url)

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
            raise DownloadLimitException(limit)

        pending = self.db.pending.all()
        if not pending:
            self.console.info('No pending chapters, download aborted.')
            return

        pending.sort(key=lambda c: c.index)

        # limiting number of chapters downloaded
        if limit is not None and limit < len(pending):
            pending = pending[:limit]
            self.console.info(f'Download limited to {len(pending)} chapters.')

        # below this point is stuff directly related to download
        value = 0
        total = len(pending)

        # initialize controller
        thread_count = min(thread_count, len(pending))

        with self.console.line(f'Creating download controller with {thread_count} threads, '):
            controller = ConcurrentActionsController(thread_count, task=self.task)
            for chapter in pending:
                controller.add(chapter)

        # set new downloads flag to true
        self.db.misc.put(self.IS_CHAPTERS_UPDATED, True)

        loader_desc = f'Downloading {len(pending)} chapters, '\
            if self.console.plain \
            else f'Downloading chapters, {Loader.percent} ({value}/{total}), '

        with Loader(self.console, desc=loader_desc, done='done.') as loader:

            # start downloading
            for result in controller.iter():
                # debug
                # brush.print(controller.queue_out.qsize())
                # brush.print(f'{chapter.no} {chapter.title}')

                value += 1
                loader.update(value=value / total, desc=f'Downloading chapters, {Loader.percent} ({value}/{total}), ')

                if type(result) is Chapter:
                    chapter = result

                    self.db.chapters.put(chapter)

                    # at last remove chapter from pending
                    self.db.pending.remove(chapter.url)
                elif type(result) is ChapterException:
                    loader.print(f'{result.type} - {result.message}', func=self.console.warning)
                else:
                    loader.print(str(result), func=self.console.warning)

        pending = self.db.pending.all()
        if len(pending) > 0:
            self.console.info(f'Download finished with {len(pending)} chapters pending.')

        # ensure all operations are done
        self.db.chapters.flush()

    def create_epub(self, force=False):
        line = self.console.line('Packing epub, ').start()

        # retrieve metadata
        novel = self.db.novel.parse()
        novel.meta = self.db.metadata.all()

        # this limits metadata to an external source should it be provided
        # using metadata from both sources causes duplicate entries
        if novel.meta_source:
            novel.meta = self.db.metadata.search_where('src', MetaData.SOURCE_EXTERNAL)

        chapters = self.db.chapters.all()
        if not chapters:
            line.end('no chapters downloaded, aborted.')
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
            line.end('no changes to chapter database, aborted.')
            return

        epub.create()

        # reset new downloads flag
        self.db.misc.put(self.IS_CHAPTERS_UPDATED, False)

        line.end(f'saved to "{epub.path}".')

    def cookie_auth(self, cookie_browser: Union[str, None] = None):

        # retrieve cookies from browser
        if cookie_browser:
            with self.console.line(f'Extracting browser cookies from "{cookie_browser}", ') as line:
                # retrieve cookiejar of the selected browser
                try:
                    cookies = getattr(browser_cookie3, cookie_browser)()
                except AttributeError:
                    raise UnsupportedBrowserException(cookie_browser)

                # filter cookie domains
                cj = RequestsCookieJar()
                for c in cookies:
                    if c.domain in self.source.cookie_domains:
                        cj.set(c.name, c.value, domain=c.domain, path=c.path)

                # set cookies jar to be used by source
                self.source.set_cookies(cj)
                line.end(f'{len(cj)} cookies, done.')
        else:
            with self.console.line('Attempting authentication using existing cookies, ') as line:
                # get existing cookies and check if they are expired
                # expired cookies are discarded
                existing_cookies = self.cookies.select(self.source.cookie_domains)
                if not existing_cookies:
                    line.end('none.')
                    raise CookieAuthException()
                elif self.cookies.check_expired(existing_cookies):
                    line.end('expired.')
                    raise CookieAuthException()
                else:
                    # if they aren't expired add the existing cookies request session
                    self.source.set_cookies(existing_cookies)

    def credential_auth(self):
        """
        Delete existing cookies and replace with new received from via fresh login
        """
        with self.console.line('Attempting authentication using credentials, '):
            # remove existing cookies
            self.cookies.delete(self.source.cookie_domains)

            # source specific login
            self.source.login(self.username, self.password)

            # set new cookies
            self.cookies.insert(self.source.session.cookies)

    def open_db(self):
        # trailing slash adds nothing
        path = Path(self.user.directory.get()) / Path(self.source.source_folder_name()) / self.source.novel_folder_name(self.url)

        return NovelData(path), path

    def cover_path(self):
        return self.db.path / Path('cover.jpg')

    def task(self, partial_c) -> Union[Chapter, Exception]:
        try:
            ch = self.source.chapter(partial_c.url)
        except Exception as e:
            return e

        ch.index = partial_c.index
        ch.title = ch.title or partial_c.title
        ch.volume = partial_c.volume

        return ch
