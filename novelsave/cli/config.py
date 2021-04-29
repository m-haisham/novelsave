import errno
from pathlib import Path

from ..database import UserConfig
from ..utils.ui import TableBuilder, ConsoleHandler


class CliConfig:
    def __init__(self, verbose):
        self.console = ConsoleHandler(verbose=verbose)
        self.user = UserConfig.instance()

    @staticmethod
    def handle(args):
        config = CliConfig(args.verbose)

        # updating storage directory
        try:
            if args.dir:
                config.set_dir(args.dir)
        except IOError as e:
            if e.errno == 22:  # invalid filename
                config.console.error(f'The provided path is syntactically incorrect: ({args.dir})')
            else:
                config.console.error(str(e))
            return
        except ValueError as e:  # check for validation failures
            config.console.error('''
Path validation failed. make sure that:
  - The path exists
  - The path points a directory
    ''')
            return

        if args.toggle_banner:
            config.toggle_banner()

        # breathe,
        config.console.newline()

        table = TableBuilder(('field', 'value'))
        for p in config.user.configs:
            table.add_row((p.name, p.get()))

        config.console.info('Current configurations')
        print(table)

    def set_dir(self, _dir):
        with self.console.line('Updating novels location, ') as line:
            # could throw an OSError: illegal directory names
            dir = Path(_dir).resolve().absolute()

            self.user.directory.put(str(dir))
            line.end(f'"{self.user.directory.get()}", done.')

    def toggle_banner(self):
        new_mode = not self.user.show_banner.get()
        self.user.show_banner.put(new_mode)

        self.console.success(f'Banner mode set to "{"show" if new_mode else "hide"}"')