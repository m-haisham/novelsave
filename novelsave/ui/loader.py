import math
import shutil
import sys


class Loader:
    _width: int

    def __init__(self, desc: str = None, target=sys.stdout, draw=True):
        self.desc = desc
        self._target = target
        self._text_only = not self._target.isatty()

        if draw:
            if desc:
                self._update(0)
            self.update = self._update
        else:
            self.update = lambda *args, **kwargs: None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.update(1.0)

        if not self._text_only:
            self._update_width()
            # self._target.write(f'\033[2K\033[1G{self.desc_str(self._width - 2)}')
            self._target.write('\n')

        self._target.flush()

    def _update_width(self):
        self._width, _ = shutil.get_terminal_size((80, 20))

    def _update(self, value: float, desc: str = None):
        self._update_width()
        if desc is not None:
            self.desc = desc

        if self._width < 12:
            # No percent string
            desc_str = ''
            percent_str = ''
            bar_str = self.progress_bar_str(value, self._width - 2)
        elif self._width < 40:
            # No padding and desc at smaller size
            desc_str = ''
            percent_str = "{:6.2f} %".format(value * 100)
            bar_str = self.progress_bar_str(value, self._width - 12) + ' '
        else:
            # Standard progress bar desc and label
            desc_length = max(15, math.floor(self._width / 3))

            desc_str = self.desc_str(desc_length)
            percent_str = "{:6.2f} %".format(value * 100) + " "
            bar_str = " " + self.progress_bar_str(value, self._width - desc_length - 14) + ' '

        if self._text_only:
            self._target.write(f'{bar_str}{percent_str}{desc_str}\n')
            self._target.flush()
        else:
            self._target.write(f'\033[G{bar_str}{percent_str}{desc_str}')
            self._target.flush()

    def desc_str(self, width: int) -> str:
        width = width - 1

        if not self.desc:
            return ''
        if len(self.desc) <= width:
            return self.desc
        elif len(self.desc) > width:
            return '…' + self.desc[len(self.desc) - width:]

    def progress_bar_str(self, value: float, width: int):
        progress = min(1, max(0, value))
        whole_width = math.floor(progress * width)
        remainder_width = (progress * width) % 1
        part_width = math.floor(remainder_width * 8)
        part_char = [" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉"][part_width]
        if (width - whole_width - 1) < 0:
            part_char = ""
        line = "|" + "█" * whole_width + part_char + " " * (width - whole_width - 1) + "|"
        return line
