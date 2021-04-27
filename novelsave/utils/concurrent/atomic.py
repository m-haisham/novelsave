from threading import Lock


class Atomic:
    def __init__(self, initial):
        self._lock = Lock()
        self.value = initial

    def set(self, value):
        with self._lock:
            self.value = value

    def get(self):
        with self._lock:
            return self.value

    def get_noblock(self):
        return self.value


class AtomicInt(Atomic):
    def __init__(self, initial):
        super(AtomicInt, self).__init__(initial)

        assert type(initial) == int, '"initial" value must be an int'

    def increment(self, by=1):
        with self._lock:
            self.value += by

    def decrement(self, by=1):
        with self._lock:
            self.value -= by
