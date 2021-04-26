class MissingSource(TypeError):
    def __init__(self, url, *args):
        super(MissingSource, self).__init__(*args)
        self.url = url


class ChapterException(Exception):
    def __init__(self, type, message):
        super(ChapterException, self).__init__(f'[{type}] {message}')
        self.type = type
        self.message = message
