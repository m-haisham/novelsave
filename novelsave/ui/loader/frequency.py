class Frequency:
    timer: float
    _frequency: int

    def __init__(self, frequency):
        self.set(frequency)

    def set(self, value):
        self._frequency = value
        self.timer = 1 / value
