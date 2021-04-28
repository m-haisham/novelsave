import sys

from .prefix import PrinterPrefix


class ConsoleHandler:
    """
    handles output to stdout based on set attributes
    """
    def __init__(self, verbose=False, target=sys.stdout):
        self.verbose = verbose

        self._target = target
        self._text_only = not self._target.isatty()

    def print(self, *args, verbose=False, prefix='', sep=' ', end='\n'):
        if prefix:
            prefix += ' '

        text = f'{prefix}{sep.join(args)}{end}'

        if verbose:
            if self.verbose:
                self._target.write(text)
                self._target.flush()
        else:
            self._target.write(text)
            self._target.flush()

    def info(self, *args, **kwargs):
        self.print(*args, **kwargs)

    def success(self, *args, **kwargs):
        self.print(*args, **kwargs)

    def error(self, *args, **kwargs):
        self.print(*args, **kwargs)

    def warning(self, *args, **kwargs):
        self.print(*args, **kwargs)

    def list(self, *args, **kwargs):
        kwargs['prefix'] = PrinterPrefix.LIST
        self.print(*args, **kwargs)

    def confirm(self, desc, default=False):
        self._target.write(f'{PrinterPrefix.QUERY} {desc}: {"(Y/n)" if default else "(y/N)"} ')
        self._target.flush()

        try:
            choice = input()
        except (EOFError, KeyboardInterrupt):
            return False

        if choice.lower() in ['yes', 'y']:
            return True
        elif choice.lower() in ['no', 'n']:
            return False
        else:
            self.warning(f"Unrecognised input. Using default value '{default}'")
            return default

    def newline(self):
        self._target.write('\n')
        self._target.flush()
