import unittest
import phenopackets as PPkt
import pandas as pd
from c2p import IndividualFactory


class TestCaseParse(unittest.TestCase):




    def test_taxonomy(self):
        ifact = IndividualFactory()
        ga4gh_indi = ifact.from_cancer_data_aggregator(self._series)
        taxonomy = ga4gh_indi.taxonomy
        self.assertIsNotNone(taxonomy)
        self.assertEquals("NCBITaxon:9606", taxonomy.id)
        self.assertEquals("homo sapiens sapiens", taxonomy.label)

    def test_alive_vital_status(self):
        ifact = IndividualFactory()
        ga4gh_indi = ifact.from_cancer_data_aggregator(self._series)
        vs = ga4gh_indi.vital_status
        self.assertIsNotNone(vs)
        self.assertEquals(PPkt.VitalStatus.ALIVE, vs.status)




