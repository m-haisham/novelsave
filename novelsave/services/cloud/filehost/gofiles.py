from pathlib import Path

from requests import Session

from novelsave.core.services.cloud.filehost import BaseCloudFileHost


class GoFilesHost(BaseCloudFileHost):
    def name(self):
        return "gofile"

    def upload(self, file_path: Path, description: str) -> str:
        with Session() as sess:
            response = sess.get("https://api.gofile.io/getServer")
            response.raise_for_status()

            server = response.json()["data"]["server"]
            with open(file_path, "rb") as fp:
                response = sess.post(
                    f"https://{server}.gofile.io/uploadFile",
                    data={"description": description},
                    files={"upload_file": fp},
                    stream=True,
                )

            response.raise_for_status()
            return response.json()["data"]["directLink"]
