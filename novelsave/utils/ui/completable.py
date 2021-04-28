from .printer import ConsoleHandler


class Completable:
    def __init__(self, console: ConsoleHandler, text: str, on_complete: str = 'done.', on_error: str = 'error.', only_verbose: bool = False):
        self.console = console
        self.text = text
        self.on_complete = on_complete
        self.on_error = on_error
        self.only_verbose = only_verbose

        self._completed = False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._completed:
            return

        if exc_type is None:
            self.complete(self.on_complete)
        else:
            self.complete(self.on_error)

    def start(self):
        self.console.info(self.text, end='', verbose=self.only_verbose)
        return self

    def complete(self, end: str = None):
        self.console.print(end or self.on_complete, verbose=self.only_verbose)
        self._completed = True
