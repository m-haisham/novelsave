class NovelSaveTemplate:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def update(self):
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

    def create_epub(self):
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
