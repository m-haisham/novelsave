from pathlib import Path

from ..database import UserConfig
from ..utils.ui import TableBuilder, ConsolePrinter, PrinterPrefix


class CliConfig:
    def __init__(self, verbose):
        self.console = ConsolePrinter(verbose=verbose)
        self.user = UserConfig.instance()

    @staticmethod
    def handle(args):
        config = CliConfig(args.verbose)

        # updating storage directory
        if args.dir:
            config.set_dir(args.dir)

        if args.toggle_banner:
            config.toggle_banner()

        # breathe,
        config.console.newline()

        table = TableBuilder(('field', 'value'))
        for p in config.user.configs:
            table.add_row((p.name, p.get()))

        print(table)

    def set_dir(self, _dir):
        # could throw an OSError: illegal directory names
        dir = Path(_dir).resolve().absolute()

        try:
            self.user.directory.put(str(dir))
            self.console.print(f'Updated {self.user.directory.name}', prefix=PrinterPrefix.SUCCESS)
        except ValueError as e:  # check for validation failures
            self.console.print(e, prefix=PrinterPrefix.ERROR)

    def toggle_banner(self):
        new_mode = not self.user.show_banner.get()
        self.user.show_banner.put(new_mode)

        self.console.print(f'Banner mode set to {new_mode}', prefix=PrinterPrefix.SUCCESS)