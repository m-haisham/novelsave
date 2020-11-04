from queue import Queue
from threading import Thread


class ActionThread(Thread):
    def __init__(self, target, feed_in: Queue, feed_out: Queue, on_complete, **kwargs):
        super(ActionThread, self).__init__(daemon=True, **kwargs)

        self.target = target
        self.feed_in = feed_in
        self.feed_out = feed_out
        self.on_complete = on_complete

    def run(self) -> None:
        while self.feed_in.qsize() != 0:
            # run task using params from feeder
            # push output to feed out sink
            ipt = self.feed_in.get()
            self.feed_out.put(
                self.target(*ipt[0], **ipt[1])
            )

            # call that a task has been done
            self.on_complete()
