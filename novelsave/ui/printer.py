
class ConsolePrinter:
    """
    handles output to stdout based on set attributes
    """
    P_SUCCESS = '[✓]'
    P_NEUTRAL = '[-]'
    P_ERROR = '[✗]'

    def __init__(self, verbose=False):
        self.verbose = verbose

    def print(self, *args, verbose=False, prefix=None, sep=' ', end='\n'):
        if not prefix:
            prefix = self.P_NEUTRAL

        if verbose:
            if self.verbose:
                print(prefix, *args, sep=sep, end=end)
        else:
            print(prefix, *args, sep=sep, end=end)

    def switch_print(self, concise='', verbose='', prefix=None, sep=' ', end='\n'):
        if not prefix:
            prefix = self.P_NEUTRAL

        if self.verbose:
            print(prefix, verbose, sep=sep, end=end)
        else:
            print(prefix, concise, sep=sep, end=end)
