

import unittest
from oncoexporter.cda.mapper.iso8601_mapper import Iso8601Mapper


class TestIsoAgeMapper(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.age_mapper = Iso8601Mapper()

    def test_73_days(self):
        iso8601 = self.age_mapper.from_days(73.0)
        self.assertEqual("P2M13D", iso8601)

