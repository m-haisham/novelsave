
class MissingSource(TypeError):
    def __init__(self, url, *args):
        super(MissingSource, self).__init__(*args)
        self.url = url
