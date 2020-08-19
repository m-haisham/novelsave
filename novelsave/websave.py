from pathlib import Path

from webnovel import WebnovelBot
from webnovel.api import ParsedApi
from webnovel.models import Novel
from webnovel.tools import UrlTools

from .database import DIR
from .database import WebNovelData
from .epub import Epub
from .template import NovelSaveTemplate
from .ui import Loader, UiTools


class WebNovelSave(NovelSaveTemplate):
    timeout: int = 60

    _api: ParsedApi = None

    def __init__(self, url, email=None, password=None):
        super(WebNovelSave, self).__init__(url, email, password)

        self.novel_id = UrlTools.from_novel_url(url)

    def update(self):
        # get api
        api = self.get_api()

        with Loader('Scraping novel'):
            novel = Novel.from_url(UrlTools.to_novel_url(self.novel_id))

            # obtain table of contents
            toc = api.toc(self.novel_id)

        # download cover
        cover_data = UiTools.download(novel.cover_url)
        with self.cover_path().open('wb') as f:
            f.write(cover_data.getbuffer())

        # # #
        # update data
        data = WebNovelData(self.novel_id)

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

    def download(self):
        """
        Download remaining chapters
        """
        data = WebNovelData(self.novel_id)
        pending_ids = data.pending_access.all()
        if len(pending_ids) <= 0:
            print('[✗] No pending chapters')
            return

        api = self.get_api()

        with Loader('Init', value=0, total=len(pending_ids)) as brush:
            for i, id in enumerate(pending_ids):
                # update brush
                brush.value += 1

                prefix = f'[{brush.value}/{brush.total}]'
                brush.desc = f'{prefix} {id}'

                # get data
                chapter = api.chapter(self.novel_id, id)
                data.chapters_access.put(chapter)

                # at last
                data.pending_access.remove(id)

    def create_epub(self):
        """
        Create epub with current data
        """
        data = WebNovelData(self.novel_id)

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
                webnovel.signin(self.email, self.password)

                # get api with token
                self._api = webnovel.create_api()
                webnovel.close()
            else:

                # full credentials not provided so
                # create api with no token create
                self._api = ParsedApi()

        return self._api

    def should_signin(self):
        return self.email is not None and self.password is not None

    def cover_path(self) -> Path:
        return self.path() / Path('cover.jpg')

    def path(self):
        path = DIR / Path(f'n{self.novel_id}')
        path.mkdir(parents=True, exist_ok=True)

        return path
