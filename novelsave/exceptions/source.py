from urllib.parse import urlparse

from ..meta import __version__, new_issue


class MissingSource(TypeError):
    def __init__(self, url, metadata: bool = False):
        super(MissingSource, self).__init__()
        self.source = urlparse(url).netloc
        self.url = url
        self.metadata = metadata

    @property
    def message(self):
        # TODO add help to check for update
        return f'''
The source ({self.source}) of the url is not supported in the current version ({__version__}).
Request support by creating a new issue:
    {new_issue}
'''

    def __str__(self):
        return self.message


class ChapterException(Exception):
    def __init__(self, type, message):
        super(ChapterException, self).__init__(f'[{type}] {message}')
        self.type = type
        self.message = message
