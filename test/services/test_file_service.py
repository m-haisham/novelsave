import unittest

import tempfile
import shutil
from pathlib import Path

from novelsave.services.file_service import FileService


class TestFileService(unittest.TestCase):

    temp_dir = Path(tempfile.gettempdir())
    file_service = FileService(temp_dir)

    def test_get_relative(self):
        r_path = 'ns_test_dir/atc_file.html'
        path = self.file_service._get_relative(r_path)

        # test path was created correctly
        self.assertEqual(self.temp_dir / r_path, path)

        # test parent directory was created
        self.assertTrue(path.parent.exists())
        self.assertTrue(path.parent.is_dir())

        # cleanup: remove created dir
        shutil.rmtree(path.parent)

    def test_write_str(self):
        r_path = 'ns_test_dir/atc_file.html'
        data = '<h1>testing data</h1>'
        self.file_service.write_str(r_path, data)

        path = self.temp_dir / r_path

        # test file was created
        self.assertTrue(path.exists(), 'path does not exist')
        self.assertTrue(path.is_file(), 'path is not a file')

        # test content was written to file
        with path.open('r') as f:
            self.assertEqual(data, f.read())

        # cleanup: remove created dir
        shutil.rmtree(path.parent)

    def test_write_bytes(self):
        r_path = 'ns_test_dir/atc_file.html'
        data = b'<h1>testing data</h1>'
        self.file_service.write_bytes(r_path, data)

        path = self.temp_dir / r_path

        # test file was created
        self.assertTrue(path.exists(), 'path does not exist')
        self.assertTrue(path.is_file(), 'path is not a file')

        # test content was written to file
        with path.open('rb') as f:
            self.assertEqual(data, f.read())

        # cleanup: remove created dir
        shutil.rmtree(path.parent)

    def test_read_str(self):
        r_path = 'ns_test_dir/atc_file.html'
        data = '<h1>testing data read</h1>'
        path = self.temp_dir / r_path

        # create file and write data
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w') as f:
            f.write(data)

        # read and test written data
        read_data = self.file_service.read_str(r_path)
        self.assertEqual(data, read_data)

        # cleanup: remove created dir
        shutil.rmtree(path.parent)

    def test_read_str_no_file(self):
        # non existent file
        with self.assertRaises(FileNotFoundError):
            self.file_service.read_str('ns_ne_dir/non.html')

        # throw when its not a file
        dir = 'ns_ne_nfile'
        path = self.temp_dir / dir
        path.mkdir(parents=True, exist_ok=True)
        with self.assertRaises(FileNotFoundError):
            self.file_service.read_str(dir)

        # cleanup: remove created dir
        shutil.rmtree(path)

    def test_read_bytes(self):
        r_path = 'ns_test_dir/atc_file.html'
        data = b'<h1>testing data read</h1>'
        path = self.temp_dir / r_path

        # create file and write data
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('wb') as f:
            f.write(data)

        # read and test written data
        read_data = self.file_service.read_bytes(r_path)
        self.assertEqual(data, read_data)

        # cleanup: remove created dir
        shutil.rmtree(path.parent)

    def test_read_bytes_no_file(self):
        # non existent file
        with self.assertRaises(FileNotFoundError):
            self.file_service.read_bytes('ns_ne_dir/non.html')

        # throw when its not a file
        dir = 'ns_ne_nfile'
        path = self.temp_dir / dir
        path.mkdir(parents=True, exist_ok=True)
        with self.assertRaises(FileNotFoundError):
            self.file_service.read_bytes(dir)

        # cleanup: remove created dir
        shutil.rmtree(path)
