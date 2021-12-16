from pathlib import Path

from novelsave.core.services.cloud.filehost import BaseCloudFileHost
from novelsave.exceptions import NoneFileHostException


class NoneFilesHost(BaseCloudFileHost):
    def __init__(self, message: str = None):
        self.message = message or "File host service not chosen"

    def name(self):
        return ""

    def upload(self, file_path: Path, description: str) -> str:
        raise NoneFileHostException(self.message)
