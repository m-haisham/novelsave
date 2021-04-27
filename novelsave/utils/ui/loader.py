import math
import shutil
import sys

from .prefix import PrinterPrefix


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

    def __init__(self, value: float = 0, desc: str = None, target=sys.stdout, should_draw=True, style=None):
        self._target = target
        self._text_only = not self._target.isatty()

        self.desc = desc
        self.value = value

        if style is None:
            self.style = self.styles['unicode']
        else:
            self.style = style

        self.should_draw = should_draw
        if should_draw:
            if desc:
                self._update(0)
            self.update = self._update
        else:
            self.update = lambda *args, **kwargs: None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.should_draw:
            return

        if exc_type is None:
            self.update(1.0)

        if not self._text_only:
            self._update_width()
            # self._target.write(f'\033[2K\033[1G{self.desc_str(self._width - 2)}')
            self._target.write('\n')

        self._target.flush()

    def print(self, *args, end='\n', sep=' '):
        if not self.should_draw:
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

        if self._width < 12:
            # No percent string
            desc_str = ''
            percent_str = ''
            bar_str = self.progress_bar_str(self.value, self._width - 2)
        elif self._width < 40:
            # No padding and desc at smaller size
            desc_str = ''
            percent_str = "{:6.2f} %".format(self.value * 100)
            bar_str = self.progress_bar_str(self.value, self._width - 12) + ' '
        else:
            # Standard progress bar desc and label
            desc_length = max(15, math.floor(self._width * (2 / 5)))

            desc_str = self.desc_str(desc_length)
            percent_str = "[{:6.2f}%]".format(self.value * 100).ljust(PrinterPrefix.LENGTH)
            bar_str = " " + self.progress_bar_str(self.value,
                                                  self._width - desc_length - PrinterPrefix.LENGTH - 6) + ' '

        if self._text_only:
            self._target.write(f'{percent_str}{bar_str}{desc_str}\n')
            self._target.flush()
        else:
            self._target.write(f'\033[G{percent_str}{bar_str}{desc_str}')
            self._target.flush()

    def desc_str(self, width: int) -> str:
        width = width - 1

        if not self.desc:
            return ' ' * width
        if len(self.desc) <= width:
            # whitespace is added to pad the string
            # to overwrite the previous desc, should it be longer
            return self.desc + ' ' * (width - len(self.desc) + 1)
        elif len(self.desc) > width:
            return '…' + self.desc[len(self.desc) - width:]

    def progress_bar_str(self, value: float, width: int):
        progress = min(1.0, max(0.0, value))
        whole_width = math.floor(progress * width)
        remainder_width = (progress * width) % 1
        part_width = math.floor(remainder_width * 8)
        part_char = self.style['head'][part_width]
        if (width - whole_width - 1) < 0:
            part_char = ""
        line = "|" + self.style['completed'] * whole_width + part_char + " " * (width - whole_width - 1) + "|"
        return line
