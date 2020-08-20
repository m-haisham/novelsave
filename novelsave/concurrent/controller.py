from queue import Queue

from .action import ActionThread
from .atomic import AtomicInt


class ConcurrentActionsController:
    def __init__(self, count, task):
        self.queue_in = Queue()
        self.queue_out = Queue()

        # used to tell when all tasks done
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
        """
        put params to queue, equivalent to adding a task

        :param args: params for the task
        :param block: whether to do the operating while blocking
        """
        self.queue_in.put(args, block=block)

    def start(self):
        """
        start the tasks
        """
        self.remaining_count.set(self.queue_in.qsize())

        for thread in self.threads:
            thread.start()

    @property
    def done(self):
        """
        :return: whether all the tasks are done
        """
        return self.remaining_count.get_noblock() == 0 and self.queue_out.qsize() == 0
