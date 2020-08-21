import time
from threading import Thread, Event

from .bar import LoaderBar
from .frequency import Frequency
from .line import Line


class BrushThread(Thread):
    stop_reason: str

    def __init__(self, desc: str, value=-1, total=1, frequency=10):

        # thread options
        super(BrushThread, self).__init__()
        self.setDaemon(True)
        self._stop_event = Event()

        # drawing options
        self._desc = desc
        self.frequency = Frequency(frequency)
        self.value = value
        self.total = total

        self.bar = LoaderBar()

    def run(self) -> None:
        while True:
            self._draw()

            # if thread stopped, draw a completer depending on exception status
            if self._stop_event.is_set():
                Line.delete()

                prefix = f' [{self.stop_reason}]' if self._stop_event is None else ''
                print(f'\r{self.bar.end(self._stop_event is None)}{prefix} {self._desc}')
                return

            time.sleep(self.frequency.timer)

    def _draw(self, increment=True):
        if self.value < 0:
            print(f'\r{self.bar.indefinite(increment)} {self._desc}', end='')
        else:
            print(f'\r{self.bar.definite(self.value / self.total)} {self._desc}', end='')

    def update(self, value):
        self.value = value

    def stop(self, reason=None):
        """ Stop drawing """
        self._stop_event.set()
        self.stop_reason = str(reason)

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, value):
        self._desc = value

        Line.delete()
        self._draw(increment=False)

    def print(self, s):
        Line.delete()
        print(f'\r{s}')
