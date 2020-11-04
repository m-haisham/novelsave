from pathlib import Path

from webnovel import WebnovelBot
from webnovel.api import ParsedApi
from webnovel.models import Novel
from webnovel.tools import UrlTools

from .concurrent import ConcurrentActionsController
from .database import WebNovelData
from .epub import Epub
from .template import NovelSaveTemplate
from .tools import UiTools
from .ui import Loader


class WebNovelSave(NovelSaveTemplate):
    timeout: int = 60

    _api: ParsedApi = None

    def __init__(self, url, username=None, password=None, directory=None):
        super(WebNovelSave, self).__init__(url, username, password, directory)

        self.novel_id = UrlTools.from_novel_url(url)

    def update(self, force_cover=False):
        # get api
        api = self.get_api()

        with Loader('Scraping novel'):
            novel = Novel.from_url(UrlTools.to_novel_url(self.novel_id))

            # obtain table of contents
            toc = api.toc(self.novel_id)

        if force_cover or not self.cover_path().exists():
            # download cover
            cover_data = UiTools.download(novel.cover_url, desc=f'Downloading cover {novel.cover_url}')
            with self.cover_path().open('wb') as f:
                f.write(cover_data.getbuffer())

        # # #
        # update data
        data = self.open_db()

        with Loader('Update novel'):
            data.info_access.set_info(novel)

        with Loader('Update volumes'):
            for volume, chapters in toc.items():
                data.volumes_access.set_volume(volume, [c.id for c in chapters])

        with Loader('Update pending'):
            all_saved_ids = [c.id for c in data.chapters_access.all()]

            data.pending_access.truncate()
            data.pending_access.insert_all(
                list({c.id for v in toc.values() for c in v if not c.locked}.difference(all_saved_ids)),
                check=False
            )

    def download(self, thread_count=4, limit=None):
        """
        Download remaining chapters
        """
        data = self.open_db()
        pending_ids = data.pending_access.all()
        if len(pending_ids) <= 0:
            print('[✗] No pending chapters')
            return

        # limiting number of chapters downloaded
        if limit is not None and limit < len(pending_ids):
            pending_ids = pending_ids[:limit]

        api = self.get_api()

        with Loader('Populating tasks', value=0, total=len(pending_ids)) as brush:

            # initialize controller
            controller = ConcurrentActionsController(thread_count, task=api.chapter)
            for id in pending_ids:
                controller.add(self.novel_id, id)

            # start downloading
            for chapter in controller.iter():
                # update brush
                brush.value += 1

                prefix = f'[{brush.value}/{brush.total}]'
                brush.desc = f'{prefix} {chapter.id}'

                # get data
                data.chapters_access.insert(chapter)

                # at last
                data.pending_access.remove(chapter.id)

    def create_epub(self):
        """
        Create epub with current data
        """
        data = self.open_db()

        with Loader('Create epub'):
            Epub().create(
                novel=data.info_access.get_info(),
                cover=self.cover_path(),
                volumes=data.volumes_access.all(),
                chapters=data.chapters_access.all(),
                save_path=self.path()
            )

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
        path = Path(self.user.directory.get()) / Path(f'n{self.novel_id}')
        path.mkdir(parents=True, exist_ok=True)

        return path
