import subprocess
from pathlib import Path
from typing import List

from loguru import logger

from novelsave.core.services import BaseCalibreService
from novelsave.exceptions import RequirementException, ToolException


class CalibreService(BaseCalibreService):

    def ebook_convert(self, input_file: Path, output_file: Path, pass_args: List[str] = None):
        if not input_file.exists() or not input_file.is_file():
            raise FileNotFoundError(f"File cannot be found (file='{input_file}')")

        if pass_args is None:
            pass_args = []

        args = [
            'ebook-convert',
            input_file,
            output_file,
            *pass_args,
        ]

        logger.debug("Calling calibre commandline tool (tool='ebook-convert').")

        try:
            subprocess.run(args, capture_output=True, check=True)
        except (OSError, FileNotFoundError) as e:
            logger.exception(e)
            raise RequirementException(
                "Could not find any matching file for 'ebook-convert'.\n"
                "Make sure 'Calibre' is installed and added to path (https://calibre-ebook.com/download)."
            )
        except subprocess.CalledProcessError:
            raise ToolException("Command did not finish correctly (command='ebook-convert').")
