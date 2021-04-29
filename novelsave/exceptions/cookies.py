
class UnsupportedBrowserException(Exception):

    supported = ('chrome', 'firefox', 'chromium', 'opera', 'edge')

    def __init__(self, browser: str):
        super(UnsupportedBrowserException, self).__init__()
        self.browser = browser

    @property
    def message(self):
        message = f'Browser "{self.browser}" is not recognised. Use one of the supported browsers as described below.'
        for b in self.supported:
            message += f'\n    --use-cookies {b}'
        message += '\n'

        return message

    def __str__(self):
        return self.message
