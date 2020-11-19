import json
from queue import Queue
from threading import Thread, Lock

from typing import TypeVar, Callable

IOCommand = TypeVar('IOCommand')


class IOThread(Thread):
    """
    Takes an io command and processes it accordingly

    takes input of format: [Tuple[IOCommand, Path, str]]
    gives output of format: [Tuple[IOCommand, Union[str, None], Union[Exception, None]]]

    in case of an error, provided data is returned alongside the error object
    """

    READ: IOCommand = 0
    WRITE: IOCommand = 1

    def __init__(
            self,
            queue_in: Queue,  # [Tuple[IOCommand, Path, str]]
            queue_out: Queue,  # [Tuple[IOCommand, Path, Union[Exception, None], Union[str, None]]]
            to_dict: Callable,
            from_dict: Callable,
            start: bool = False,
            **kwargs
    ):
        super(IOThread, self).__init__(daemon=True, **kwargs)

        self.mutex = Lock()
        self.data = {}

        self.queue_in = queue_in
        self.queue_out = queue_out
        self.to_dict = to_dict
        self.from_dict = from_dict

        if start:
            self.start()

    def run(self) -> None:
        # this is a worker thread that would run forever
        while True:
            command, path, obj = self.queue_in.get()

            try:
                if command == IOThread.READ:
                    with path.open('r') as f:
                        json_data = json.load(f)

                    with self.mutex:
                        self.data[path.name] = self.from_dict(json_data)

                    self.queue_out.put((command, path, None))

                elif command == IOThread.WRITE:
                    with path.open('w') as f:
                        json.dump(self.to_dict(obj), f)

                    with self.mutex:
                        self.data[path.name] = obj

                    self.queue_out.put((command, path, None))
                else:
                    self.queue_out.put(
                        (command, path, TypeError(f"Unknown command: '{command}'; must be of {list(range(4))}:WRITE")))

            # catch any and all exceptions so that thread wont stall
            except Exception as e:
                self.queue_out.put((command, path, e))

            # must be punctual
            self.queue_in.task_done()
