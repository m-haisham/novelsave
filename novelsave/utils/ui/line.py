class LineHandler:
    def __init__(self, console, text: str, on_success: str = 'done.', on_error: str = 'error.', hide_plain: bool = False):
        self.console = console
        self.text = text
        self.on_complete = on_success
        self.on_error = on_error
        self.hide_plain = hide_plain

        self._ended = False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._ended:
            return

        if exc_type is None:
            self.end(self.on_complete)
        else:
            self.end(self.on_error)

    def start(self):
        self.console.info(self.text, end='', hide_plain=self.hide_plain)
        return self

    def write(self, s: str):
        self.console.print(s, end='', hide_plain=self.hide_plain)

    def end(self, s: str = None, error = False):
        self.console.print(s or (self.on_error if error else self.on_complete), hide_plain=self.hide_plain)
        self._ended = True
