from queue import Queue

from .action import ActionThread
from .atomic import AtomicInt


class ConcurrentActions:
    def __init__(self, count, task):
        self.queue_in = Queue()
        self.queue_out = Queue()

        self.remaining_count = AtomicInt(0)

        self.threads = [
            ActionThread(
                task,
                self.queue_in,
                self.queue_out,
                on_complete=self.remaining_count.decrement,
                name=f'action_thread_{i}',
            )
            for i in range(count)
        ]

    def add(self, *args, block=False):
        self.queue_in.put(args, block=block)

    def start(self):
        self.remaining_count.set(self.queue_in.qsize())

        for thread in self.threads:
            thread.start()

    @property
    def done(self):
        return self.remaining_count.get_noblock() == 0 and self.queue_out.qsize() == 0
