WIDTH: int = 5
CURSOR_WIDTH: int = 3
FILL: str = '='
EMPTY: str = ' '

PREFIX: str = '['
POSTFIX: str = ']'

CHECK = '✓'
CROSS = '✗'


class LoaderBar:

    def __init__(self):
        self._indefinite = []
        self.indefinite_index = 0

        self.generate()

    def generate(self):
        """
        :return: recreate bar
        """
        self._indefinite = []

        # all the generation math
        snake = list((FILL * CURSOR_WIDTH) + (EMPTY * (WIDTH * 2)))
        fallout_start = CURSOR_WIDTH - 1
        fallout_end = WIDTH + CURSOR_WIDTH - 1

        i = 0
        while True:
            segment = snake[fallout_start:fallout_end]
            self._indefinite.append(f"{PREFIX}{''.join(segment)}{POSTFIX}")

            if all(bit == EMPTY for bit in segment):
                break

            # crawl forward
            bit = snake.pop(-1)
            snake.insert(0, bit)

            i += 1

        reverse = reversed(self._indefinite[:-1])
        empty_state = self._indefinite[-1]

        # self._indefinite += reverse
        self._indefinite.append(empty_state)

        self.indefinite_index = len(self._indefinite) - 1

    def indefinite(self, increment=True):
        """
        :param increment: whether to return the next slice
        :return: return slice corresponding to next slice
        """
        if increment:
            self.indefinite_index = (self.indefinite_index + 1) % len(self._indefinite)
        return self._indefinite[self.indefinite_index]

    def definite(self, value: float) -> str:
        """
        :param value: float between 0 (inclusive) and 1 (inclusive)
        :return: string denoting the amount loaded
        """
        value = max(0.0, value)
        value = min(1.0, value)
        filled = int(value * WIDTH)
        return f'{PREFIX}{FILL * filled}{EMPTY * (WIDTH - filled)}{POSTFIX}'

    def update(self, value: int):
        """
        :param value: less than 0 for indefnite, and between 0 (incluslive) and 1 (inclusive) for definite
        :return: progress bar slice
        """
        if value < 0:
            return self.indefinite()
        else:
            return self.definite(value)

    def end(self, error=False):
        return f'{PREFIX}{CROSS if error else CHECK}{POSTFIX}'
