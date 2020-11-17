import json
from queue import Queue
from threading import Thread

from typing import TypeVar

IOCommand = TypeVar('IOCommand')


class IOThread(Thread):
    """
    Takes an io command and processes it accordingly

    takes input of format: [Tuple[IOCommand, Path, str]]
    gives output of format: [Tuple[IOCommand, Union[str, None], Union[Exception, None]]]

    in case of an error, provided data is returned alongside the error object
    """

    READ_JSON: IOCommand = 0
    WRITE_JSON: IOCommand = 1
    READ: IOCommand = 2
    WRITE: IOCommand = 3

    def __init__(
            self,
            queue_in: Queue,  # [Tuple[IOCommand, Path, str]]
            queue_out: Queue  # [Tuple[IOCommand, Union[Exception, None], Union[str, None]]]
    ):
        super(IOThread, self).__init__(daemon=True)
        self.queue_in = queue_in
        self.queue_out = queue_out

    def run(self) -> None:
        # this is a worker thread that would run forever
        while True:
            command, path, data = self.queue_in.get()

            try:
                if command == IOThread.READ_JSON:
                    with path.open('r') as f:
                        data = json.load(f)

                    self.queue_out.put((command, data, None))

                elif command == IOThread.WRITE_JSON:
                    with path.open('w') as f:
                        json.dump(data, f)

                    self.queue_out.put((command, None, None))

                elif command == IOThread.READ:
                    with path.open('r') as f:
                        data = f.read()

                    self.queue_out.put((command, data, None))

                elif command == IOThread.WRITE:
                    with path.open('w') as f:
                        f.write(data)

                    self.queue_out.put((command, None, None))
                else:
                    self.queue_out.put((command, data, TypeError(f"Unknown command: '{command}'; must be of {list(range(4))}:WRITE")))

            # catch any and all exceptions so that thread wont stall
            except Exception as e:
                self.queue_out.put((command, data, e))

            # must be punctual
            self.queue_in.task_done()
