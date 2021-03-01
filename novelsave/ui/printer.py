from .prefix import PrinterPrefix


class ConsolePrinter:
    """
    handles output to stdout based on set attributes
    """
    def __init__(self, verbose=False):
        self.verbose = verbose

    def print(self, *args, verbose=False, prefix=None, sep=' ', end='\n'):
        if prefix is None:
            prefix = PrinterPrefix.NEUTRAL

        if verbose:
            if self.verbose:
                print(prefix, *args, sep=sep, end=end)
        else:
            print(prefix, *args, sep=sep, end=end)

    def raw_print(self, *args, verbose=False, sep=' ', end='\n'):
        if verbose:
            if self.verbose:
                print(*args, sep=sep, end=end)
        else:
            print(*args, sep=sep, end=end)

    def list(self, *args, sep=' ', end='\n'):
        print(PrinterPrefix.LIST, *args, sep=sep, end=end)

    def switch_print(self, concise='', verbose='', prefix=None, sep=' ', end='\n'):
        if prefix is None:
            prefix = PrinterPrefix.NEUTRAL

        if self.verbose:
            print(prefix, verbose, sep=sep, end=end)
        else:
            print(prefix, concise, sep=sep, end=end)

    def confirm(self, desc, default=False):
        print(f'[?] {desc}: {"(Y/n)" if default else "(y/N)"} ', end='')

        try:
            choice = input()
        except (EOFError, KeyboardInterrupt):
            print()
            return False

        if choice.lower() in ['yes', 'y']:
            return True
        elif choice.lower() in ['no', 'n']:
            return False
        else:
            self.print(f"Unrecognised input. Using default value '{default}'", prefix=PrinterPrefix.ERROR)
            return default

    def endline(self):
        print()
