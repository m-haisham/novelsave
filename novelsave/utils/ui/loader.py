import math
import shutil
import sys


class Loader:
    _width: int

    styles = {
        'unicode': {
            'completed': '█',
            'head': [" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉"],
        },
        'ascii': {
            'completed': '=',
            'head': [' ', ' ', ' ', ' ', '-', '-', '-', '-'],
        },
    }

    percent = "{:6.2f}%"

    def __init__(self, console, value: float = 0, desc: str = None, done='', target=sys.stdout, style=None):
        self._target = target
        self._text_only = not self._target.isatty()

        self.console = console

        self.desc = desc
        self.value = value
        self.done = done

        if style is None:
            self.style = self.styles['unicode']
        else:
            self.style = style

        self.line = self.console.line(self.desc, self.done)

        if self.console.plain:
            self.update = lambda *args, **kwargs: None
        else:
            if desc:
                self._update(0)
            self.update = self._update

    def __enter__(self):
        if self.console.plain:
            self.line.__enter__()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.console.plain:
            self.line.__exit__(exc_type, exc_val, exc_tb)
            return

        if exc_type is None:
            self.update(1.0)

        if not self._text_only:
            self._update_width()
            # self._target.write(f'\033[2K\033[1G{self.desc_str(self._width - 2)}')
            self._target.write(self.done + '\n')

        self._target.flush()

    def print(self, *args, end='\n', sep=' '):
        if self.console.plain:
            self.console.print(*args, end=end, sep=sep)
            return

        text = sep.join(args) + end

        if self._text_only:
            self._target.write(text)
        else:
            # remove current progress bar and print
            self._target.write(f'\033[2K\033[1G')
            self._target.write(text)

            # re draw progressbar
            self.update()

        self._target.flush()

    def _update_width(self):
        self._width, _ = shutil.get_terminal_size((80, 20))

    def _update(self, value: float = None, desc: str = None):
        self._update_width()

        if value is not None:
            self.value = value
        if desc is not None:
            self.desc = desc

        # Standard progress bar desc and label
        desc_length = max(15, self._width)
        desc_str = self.desc_str(desc_length).format(self.value * 100)

        if self._text_only:
            self._target.write(f'{desc_str}\n')
            self._target.flush()
        else:
            self._target.write(f'\033[G{desc_str}')
            self._target.flush()

    def desc_str(self, width: int) -> str:
        width = width - 1

        if not self.desc:
            return ' ' * width
        if len(self.desc) <= width:
            return self.desc
        elif len(self.desc) > width:
            return '…' + self.desc[len(self.desc) - width:]