import unittest

import tempfile
import shutil
from pathlib import Path

from novelsave.services.file_service import FileService


class TestFileService(unittest.TestCase):

    temp_dir = Path(tempfile.gettempdir())
    data_division = {'.html': 'web'}
    file_service = FileService()

    def test_write_str(self):
        path = Path('ns_test_dir/atc_file.html')
        path.parent.mkdir(parents=True, exist_ok=True)

        data = '<h1>testing data</h1>'
        self.file_service.write_str(path, data)

        # test file was created
        self.assertTrue(path.exists(), 'path does not exist')
        self.assertTrue(path.is_file(), 'path is not a file')

        # test content was written to file
        with path.open('r') as f:
            self.assertEqual(data, f.read())

        # cleanup: remove created dir
        shutil.rmtree(path.parent)

    def test_write_bytes(self):
        path = Path('ns_test_dir/atc_file.html')
        path.parent.mkdir(parents=True, exist_ok=True)

        data = b'<h1>testing data</h1>'
        self.file_service.write_bytes(path, data)

        # test file was created
        self.assertTrue(path.exists(), 'path does not exist')
        self.assertTrue(path.is_file(), 'path is not a file')

        # test content was written to file
        with path.open('rb') as f:
            self.assertEqual(data, f.read())

        # cleanup: remove created dir
        shutil.rmtree(path.parent)

    def test_read_str(self):
        path = Path('ns_test_dir/atc_file.html')
        path.parent.mkdir(parents=True, exist_ok=True)

        data = '<h1>testing data read</h1>'

        # create file and write data
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w') as f:
            f.write(data)

        # read and test written data
        read_data = self.file_service.read_str(path)
        self.assertEqual(data, read_data)

        # cleanup: remove created dir
        shutil.rmtree(path.parent)

    def test_read_str_no_file(self):
        # non existent file
        with self.assertRaises(FileNotFoundError):
            self.file_service.read_str(Path('ns_ne_dir/non.html'))

        # throw when its not a file
        dir = Path('ns_ne_n_file')
        path = self.temp_dir / dir
        path.mkdir(parents=True, exist_ok=True)
        with self.assertRaises(FileNotFoundError):
            self.file_service.read_str(dir)

        # cleanup: remove created dir
        shutil.rmtree(path)

    def test_read_bytes(self):
        path = Path('ns_test_dir/atc_file.html')
        data = b'<h1>testing data read</h1>'

        # create file and write data
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('wb') as f:
            f.write(data)

        # read and test written data
        read_data = self.file_service.read_bytes(path)
        self.assertEqual(data, read_data)

        # cleanup: remove created dir
        shutil.rmtree(path.parent)

    def test_read_bytes_no_file(self):
        # non existent file
        with self.assertRaises(FileNotFoundError):
            self.file_service.read_bytes(Path('ns_ne_dir/non.html'))

        # throw when its not a file
        dir = Path('ns_ne_n_file')
        path = self.temp_dir / dir
        path.mkdir(parents=True, exist_ok=True)
        with self.assertRaises(FileNotFoundError):
            self.file_service.read_bytes(dir)

        # cleanup: remove created dir
        shutil.rmtree(path)
