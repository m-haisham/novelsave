from .prefix import PrinterPrefix


class ConsolePrinter:
    """
    handles output to stdout based on set attributes
    """
    def __init__(self, verbose=False):
        self.verbose = verbose

    def print(self, *args, verbose=False, prefix=None, sep=' ', end='\n'):
        if not prefix:
            prefix = PrinterPrefix.NEUTRAL

        if verbose:
            if self.verbose:
                print(prefix, *args, sep=sep, end=end)
        else:
            print(prefix, *args, sep=sep, end=end)

    def switch_print(self, concise='', verbose='', prefix=None, sep=' ', end='\n'):
        if not prefix:
            prefix = PrinterPrefix.NEUTRAL

        if self.verbose:
            print(prefix, verbose, sep=sep, end=end)
        else:
            print(prefix, concise, sep=sep, end=end)
