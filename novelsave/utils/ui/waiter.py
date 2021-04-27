class Waiter:
    CHECK = '✓'
    CROSS = '✗'
    HOURGLASS = '⌛'

    def __init__(self, message):
        self.message = message

        print(f'\r {Waiter.HOURGLASS} {message}', end='')

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()

    def end(self):
        self._delete_line()
        print(f'\r{Waiter.CHECK} {self.message}')

    def _delete_line(self):
        print('\033[2K\033[1G', end='')
