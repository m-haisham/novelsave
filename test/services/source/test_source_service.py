import unittest

from novelsave.services.source import SourceGateway


class TestSourceService(unittest.TestCase):
    source_service: SourceGateway

    def setUp(self):
        self.source_service = SourceGateway(novel_url='')
