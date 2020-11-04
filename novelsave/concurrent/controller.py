from queue import Queue

from .action import ActionThread


class ConcurrentActionsController:
    def __init__(self, count, task):
        self.queue_in = Queue()
        self.queue_out = Queue()

        self.threads = [
            ActionThread(
                task,
                self.queue_in,
                self.queue_out,
                on_complete=self.queue_in.task_done,
                name=f'action_thread_{i}',
            )
            for i in range(count)
        ]

    def add(self, *args, block=False, **kwargs):
        """
        put params to queue, equivalent to adding a task

        :param args: params for the task
        :param block: whether to do the operating while blocking
        """
        self.queue_in.put((args, kwargs), block=block)

    def start(self):
        """
        start the tasks
        """
        for thread in self.threads:
            thread.start()

    @property
    def done(self):
        """
        :return: whether all the tasks are done
        """
        with self.queue_in.all_tasks_done:
            q_in = self.queue_in.unfinished_tasks == 0

        with self.queue_out.all_tasks_done:
            q_out = self.queue_out.unfinished_tasks == 0

        return q_in and q_out

    def iter(self):
        """
        :return: generator that returns all the outputs
        """
        # start all the threads
        self.start()

        # wait for outputs from each thread
        while not self.done:
            yield self.queue_out.get()
            self.queue_out.task_done()
