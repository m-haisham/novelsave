import unittest

from novelsave.exceptions import SourceNotAvailableException
from novelsave.services import SourceService
from novelsave.services.source_service import require_source


class TestSourceService(unittest.TestCase):
    source_service: SourceService

    def setUp(self):
        self.source_service = SourceService(novel_url='')

    def test_require_source_throws(self):
        """exception must be thrown when source is not available"""
        test_function = require_source(lambda self_: None)

        with self.assertRaises(SourceNotAvailableException):
            test_function(self.source_service)

    def test_require_source_no_throw(self):
        """exception should not be thrown when source is something"""
        test_function = require_source(lambda self_: None)
        self.source_service.source = None

        try:
            test_function(self.source_service)
        except SourceNotAvailableException:
            self.fail('exception should not be raised')
