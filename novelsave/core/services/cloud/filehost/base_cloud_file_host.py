from abc import ABC, abstractmethod
from pathlib import Path


class BaseCloudFileHost(ABC):
    @abstractmethod
    def name(self):
        """Name of the cloud file hosting service"""

    @abstractmethod
    def upload(self, file_path: Path, description: str) -> str:
        """
        Upload the file at the given path and return the web address

        :param file_path: The file to be uploaded
        :type file_path: Path

        :param description: A short definition of file being uploaded
        :type description: str

        :returns: The web address of the uploaded file
        :rtype: str

        :raises: requests.HttpError if upload fails
        """
