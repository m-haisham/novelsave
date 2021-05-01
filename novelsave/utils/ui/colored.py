from colorama import Fore

from ..helpers import unzip_arguments


class ColoredTemplate:
    def __init__(self, console, fore):
        self.console = console
        self.fore = fore

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError


class Colored(ColoredTemplate):
    def __new__(cls, *args, **kwargs):
        console, = unzip_arguments(args, kwargs, ((0, 'console'),))

        if console.plain:
            return PlainColored(*args, **kwargs)
        else:
            return VerboseColored(*args, **kwargs)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class VerboseColored(ColoredTemplate):
    def __enter__(self):
        self.console.write(self.fore)
        return self.console

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.console.write(Fore.RESET)
        self.console.flush()


class PlainColored(ColoredTemplate):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
