import time

from novelsave.ui import Loader

if __name__ == '__main__':
    total = 2

    with Loader('hi', value=0, total=total) as brush:
        for i in range(total):
            time.sleep(1)
            brush.update(brush.value + 1)

        brush.value = -1
        while True:
            pass