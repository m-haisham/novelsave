from pathlib import Path

import requests
from webnovel import WebnovelBot
from webnovel.api import ParsedApi
from webnovel.models import Novel
from webnovel.tools import UrlTools

from .concurrent import ConcurrentActionsController
from .database import WebNovelData
from .epub import NovelEpub
from .models import Chapter
from .template import NovelSaveTemplate
from .tools import UiTools
from .ui import Loader


class WebNovelSave(NovelSaveTemplate):
    timeout: int = 60

    _api: ParsedApi = None

    def __init__(self, url, username=None, password=None, directory=None):
        super(WebNovelSave, self).__init__(url, username, password, directory)

        self.novel_id = UrlTools.from_novel_url(url)
        self.netloc_slug = "www_webnovel_com"

    def update(self, force_cover=False):
        # get api
        api = self.get_api()

        UiTools.print_info('Retrieving novel info...')
        UiTools.print_info(self.url)
        novel = Novel.from_url(UrlTools.to_novel_url(self.novel_id))

        # obtain table of contents
        toc = api.toc(self.novel_id)

        UiTools.print_success(f'Found {len([c for v in toc.values() for c in v if not c.locked])} chapters')

        if force_cover or not self.cover_path().exists():
            # download cover
            response = requests.get(novel.cover_url)
            with self.cover_path().open('wb') as f:
                f.write(response.content)

        # # #
        # update data
        data = self.open_db()

        # info and volume
        data.info.set_info(novel)
        for volume, chapters in toc.items():
            data.volumes.set_volume(volume, [c.id for c in chapters])

        # update pending
        saved = data.chapters.all_basic()
        pending = list({self.to_chapter(c) for v in toc.values() for c in v if not c.locked}.difference(saved))

        data.pending.truncate()
        data.pending.put_all([c for c in pending])

        UiTools.print_info(f'Pending {len(pending)} chapters',
                           f'| {pending[0].no} {pending[0].title}' if len(pending) == 1 else '')

    def download(self, thread_count=4, limit=None):
        """
        Download remaining chapters
        """
        # parameter validation
        if limit and limit <= 0:
            UiTools.print_error("'limit' must be greater than 0")

        data = self.open_db()
        data.chapters.check()  # check if any external files are missing
        pending = data.pending.all()
        if len(pending) <= 0:
            UiTools.print_error('No pending chapters')
            return

        # limiting number of chapters downloaded
        if limit is not None and limit < len(pending):
            pending = pending[:limit]

        api = self.get_api()

        # some useful information
        if not self.verbose:
            if len(pending) == 1:
                additive = str(pending[0].index)
            else:
                additive = f'{pending[0].index} - {pending[-1].index}'

            UiTools.print_info(f'Downloading {len(pending)} chapters | {additive}...')

        with Loader(f'Populating tasks ({len(pending)})', value=0, total=len(pending), draw=self.verbose) as brush:

            # initialize controller
            controller = ConcurrentActionsController(
                thread_count,
                task=lambda nid, cid: self.to_chapter(api.chapter(nid, cid))
            )
            for chapter in pending:
                controller.add(self.novel_id, chapter.index)

            # set new downloads flag to true
            data.misc.put(self.IS_CHAPTERS_UPDATED, True)

            # start downloading
            for chapter in controller.iter():
                # update brush
                if self.verbose:
                    brush.value += 1
                    brush.desc = f'[{brush.value}/{brush.total}] {chapter.url}'

                data.chapters.put(chapter)

                # at last
                data.pending.remove(chapter.url)

    def create_epub(self, force=False):
        """
        Create epub with current data
        """
        data = self.open_db()

        UiTools.print_info('Packing epub...')
        epub = NovelEpub(
            novel=data.info.get_info(),
            cover=self.cover_path(),
            volumes=data.volumes.all(),
            chapters=data.chapters.all(),
            save_path=self.path()
        )

        # get new downloads flag
        is_updated = data.misc.get(self.IS_CHAPTERS_UPDATED, default=False)

        # check flags and whether the epub already exists
        if not is_updated and not force and epub.path.exists():
            UiTools.print_info('Aborted. No changes to chapter database')
            return

        epub.create()

        # reset new downloads flag
        data.misc.put(self.IS_CHAPTERS_UPDATED, False)

        UiTools.print_success(f'Saved to {epub.path}')

    def get_api(self) -> ParsedApi:
        """
        if api exists returns existing
        else creates api according to provided credentials

        :return: Api according to access level
        """
        if self._api is None:
            if self.should_signin():
                # sign in to get access token
                webnovel = WebnovelBot(timeout=self.timeout)
                webnovel.driver.get(UrlTools.to_novel_url(self.novel_id))
                webnovel.signin(self.username, self.password)

                # get api with token
                self._api = webnovel.create_api()
                webnovel.close()
            else:

                # full credentials not provided so
                # create api with no token create
                self._api = ParsedApi()

        return self._api

    def open_db(self):
        return WebNovelData(self.path())

    def should_signin(self):
        return self.username is not None and self.password is not None

    def cover_path(self) -> Path:
        return self.path() / Path('cover.jpg')

    def path(self):
        path = Path(self.user.directory.get()) / Path(self.netloc_slug) / Path(f'n{self.novel_id}')
        path.mkdir(parents=True, exist_ok=True)

        return path

    def to_chapter(self, wchapter):
        return Chapter(
            index=wchapter.id,
            no=wchapter.no,
            title=wchapter.title,
            paragraphs=wchapter.paragraphs,
            url=wchapter.url
        )
