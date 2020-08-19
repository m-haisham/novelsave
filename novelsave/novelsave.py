class NovelSave:
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

    def download(self):
        """
        Download current pending chapters
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
