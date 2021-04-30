from colorama import Fore


class Colored:
    def __init__(self, console, fore):
        self.console = console
        self.fore = fore

    def __enter__(self):
        if not self.console.plain:
            self.console.write(self.fore)

        return self.console

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.console.plain:
            self.console.write(Fore.RESET)
            self.console.flush()
