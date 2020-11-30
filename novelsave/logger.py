from datetime import datetime
import logging
from pathlib import Path


class NovelLogger:
    instance = None

    def __init__(self, path):
        self.path = path
        self._logger = None

    def create_logger(self):
        logfile = self.path / Path('logs') / f"{datetime.today().strftime('%Y-%m-%d')}.log"
        logfile.parent.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger('novel-logger')
        logger.setLevel(logging.DEBUG)

        # setting stream handler
        formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')

        sh = logging.StreamHandler(logfile.open('a'))
        sh.setFormatter(formatter)

        logger.addHandler(sh)

        return logger

    @property
    def logger(self):
        if self._logger is None:
            self._logger = self.create_logger()

        return self._logger
