from threading import Thread
from queue import Queue


class ActionThread(Thread):
    def __init__(self, target, feed_in: Queue, feed_out: Queue, on_complete, **kwargs):
        super(ActionThread, self).__init__(daemon=True, **kwargs)

        self.target = target
        self.feed_in = feed_in
        self.feed_out = feed_out
        self.on_complete = on_complete

    def run(self) -> None:
        while self.feed_in.qsize() != 0:
            self.feed_out.put(
                self.target(*self.feed_in.get())
            )

            self.on_complete()