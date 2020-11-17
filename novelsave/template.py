from pathlib import Path

from .database.config import UserConfig
from .tools import UiTools


class NovelSaveTemplate:
    verbose = False

    IS_CHAPTERS_UPDATED = 'is_cu'

    def __init__(self, url, username, password, directory=None):
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

    def update(self, force_cover=False):
        """
        Update novel data

        - Get new data
        - Download new cover
        - Update pending
        """
        raise NotImplementedError

    def download(self, thread_count=4, limit=None):
        """
        Download current pending chapters

        :param thread_count: amount of download threads
        :param limit: amount of chapters to download
        """
        raise NotImplementedError

    def create_epub(self, force=False):
        """
        create epub from current data
        """
        raise NotImplementedError

    def open_db(self):
        """
        Create or open database of current novel

        :return: database
        """
        raise NotImplementedError
