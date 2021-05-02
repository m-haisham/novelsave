import sys
from pathlib import Path

from ..database import UserConfig
from ..utils.ui import ConsoleHandler


class CliConfig:
    def __init__(self, plain, no_input):
        self.console = ConsoleHandler(plain, no_input)
        self.user = UserConfig.instance()

    @staticmethod
    def handle(args):
        config = CliConfig(args.plain, args.no_input)

        # updating storage directory
        try:
            if args.save_dir:
                config.set_dir(args.save_dir)
        except IOError as e:
            if e.errno == 22:  # invalid filename
                config.console.error(f'The provided path is syntactically incorrect: ({args.dir})')
            else:
                config.console.error(str(e))
            sys.exit(1)
        except ValueError as e:  # check for validation failures
            config.console.error('''
Path validation failed. make sure that:
  - The path exists
  - The path points a directory
    ''')
            sys.exit(1)

        if args.toggle_banner:
            config.toggle_banner()

        # put some space if there has been any status changes
        if any((args.save_dir, args.toggle_banner)):
            config.console.newline()

        config.display()

    def set_dir(self, _dir):
        with self.console.line('Updating novels location, ') as line:
            # could throw an OSError: illegal directory names
            dir = Path(_dir).resolve().absolute()

            self.user.directory.put(str(dir))
            line.end(f'"{self.user.directory.get()}", done.')

    def toggle_banner(self):
        new_mode = not self.user.show_banner.get()
        self.user.show_banner.put(new_mode)

        self.console.success(f'Banner mode changed to "{"show" if new_mode else "hide"}"')

    def display(self):
        self.console.write(f'[CONFIGURATIONS]\n')
        self.console.write(f'Banner mode is set to "{"show" if self.user.show_banner.get() else "hide"}".\n')
        self.console.write(f'Current save directory is "{self.user.directory.get()}".\n')
        self.console.flush()