from pathlib import Path

from requests import Session

from novelsave.core.services.cloud.filehost import BaseCloudFileHost


class AnonFilesHost(BaseCloudFileHost):
    def name(self):
        return "anonfiles"

    def upload(self, file_path: Path, description: str) -> str:
        with Session() as session:
            with open(file_path, "rb") as fp:
                response = session.post(
                    "https://api.anonfiles.com/upload",
                    files={"file": fp},
                    stream=True,
                )

            response.raise_for_status()
            return response.json()["data"]["file"]["url"]["full"]
