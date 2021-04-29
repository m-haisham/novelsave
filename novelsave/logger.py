import logging
from datetime import datetime
from pathlib import Path


class NovelLogger:
    instance = None

    def __init__(self, path, console=None):
        self.path = path
        self.console = console
        self._logger = None

    def create_logger(self):
        with self.console.line('Initializing logger, ', hide_plain=True) as line:
            logfilename = f"{datetime.today().strftime('%Y-%m-%d')}.log"
            logfile = self.path / Path('logs') / logfilename
            logfile.parent.mkdir(parents=True, exist_ok=True)

            line.write(f'created file {logfilename}, ')

            logger = logging.getLogger('novel-logger')
            logger.setLevel(logging.DEBUG)

            # setting stream handler
            sh = logging.StreamHandler(logfile.open('a'))

            formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
            sh.setFormatter(formatter)

            logger.addHandler(sh)

            # alerting
            if self.console and not self.console.plain:
                self.console.info('Logger initialised.')

        return logger

    def info(self, s):
        self.logger.info(s)

    def error(self, s):
        self.logger.error(s)

    @property
    def logger(self):
        if self._logger is None:
            self._logger = self.create_logger()

        return self._logger
