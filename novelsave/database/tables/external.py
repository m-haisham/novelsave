from pathlib import Path
from queue import Queue
from typing import List, TypeVar, Callable

from .iothread import IOThread
from .multi import MultiClassTable
from ...logger import NovelLogger

T = TypeVar('T')


class MultiClassExternalTable(MultiClassTable):
    PATH_KEY = 'PATH'

    def __init__(
            self,
            db,
            path,
            table: str,
            cls: T,
            fields: List[str],
            identifier: str,
            naming_scheme: Callable[[T], str],
    ):
        super(MultiClassExternalTable, self).__init__(db, table, cls, fields, identifier)

        self.path = path / Path(table)
        self.path.mkdir(parents=True, exist_ok=True)

        self.naming_scheme = naming_scheme

        # initialize iothread
        self.queue_in = Queue()
        self.queue_out = Queue()
        self.iothread = \
            IOThread(self.queue_in, self.queue_out, self._to_dict, self._from_dict, start=True, name='IOThread')

        self._load()

    def put(self, obj):
        name = self.naming_scheme(obj)
        path = self.path / Path(f'{name}.json')
        self.queue_in.put((IOThread.WRITE, path, obj))

    def put_all(self, objs: List):
        for obj in objs:
            self.put(obj)

    def all(self) -> List:
        """
        :return: return full data, including from the external files
        """
        self.flush()

        with self.iothread.mutex:
            return list(self.iothread.data.values())

    def flush(self):
        """
        wait until all operations are done and process outputs

        :return: None
        """
        while not self.tasks_done():
            command, path, error = self.queue_out.get()

            if error:
                NovelLogger.instance.logger.error(f'{"READ" if command == IOThread.READ else "WRITE"}: {path} - {repr(error)}')

            self.queue_out.task_done()

    def _load(self):
        """
        add tasks to load all the files from disk
        """
        for file in self.path.glob('./*.json'):
            self.queue_in.put((IOThread.READ, file, None))

    def tasks_done(self):
        """
        :return: whether all the tasks are tasks_done
        """
        with self.queue_in.all_tasks_done:
            q_in = self.queue_in.unfinished_tasks == 0

        with self.queue_out.all_tasks_done:
            q_out = self.queue_out.unfinished_tasks == 0

        return q_in and q_out
