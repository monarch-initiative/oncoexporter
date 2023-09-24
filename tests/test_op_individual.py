import pandas as pd
from unittest import TestCase
import phenopackets as PPkt
from oncoexporter.cda import CdaIndividualFactory


class OpIndividualTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        data = ['CGCI.HTMCP-03-06-02007',
                "[{'system': 'GDC', 'field_name': 'case.submitter_id', 'value': 'HTMCP-03-06-02007'}]",
                'Homo sapiens',
                'female',
                'black or african american',
                'not reported',
                '-15987.0',
                "['CGCI-HTMCP-CC']",
                "Alive",
                "NaN",
                "None"]
        cls._column_names = ['subject_id', 'subject_identifier', 'species', 'sex', 'race',
                        'ethnicity', 'days_to_birth', 'subject_associated_project',
                        'vital_status', 'days_to_death', 'cause_of_death']
        cls._series = pd.Series(data, index=cls._column_names)

    def test_creation(self):
        ifact = CdaIndividualFactory()
        self.assertIsNotNone(ifact)
        ga4gh_indi = ifact.from_cancer_data_aggregator(self._series)
        self.assertIsNotNone(ga4gh_indi)

    def test_id(self):
        ifact = CdaIndividualFactory()
        ga4gh_indi = ifact.from_cancer_data_aggregator(self._series)
        expected_id = 'CGCI.HTMCP-03-06-02007'
        self.assertEqual(expected_id, ga4gh_indi.id)

    def test_iso_age(self):
        """
        CDA provides age as number of days. The conversion to an ISO period depends on actual birth month etc, but
        is approximately correct.
        """
        ifact = CdaIndividualFactory()
        ga4gh_indi = ifact.from_cancer_data_aggregator(self._series)
        expected_iso = 'P43Y9M'
        calculated_iso = ga4gh_indi.time_at_last_encounter.age.iso8601duration
        self.assertEqual(expected_iso, calculated_iso)

    def test_taxonomy(self):
        ifact = CdaIndividualFactory()
        ga4gh_indi = ifact.from_cancer_data_aggregator(self._series)
        taxonomy = ga4gh_indi.taxonomy
        self.assertIsNotNone(taxonomy)
        self.assertEqual("NCBITaxon:9606", taxonomy.id)
        self.assertEqual("homo sapiens sapiens", taxonomy.label)

    def test_alive_vital_status(self):
        ifact = CdaIndividualFactory()
        ga4gh_indi = ifact.from_cancer_data_aggregator(self._series)
        vs = ga4gh_indi.vital_status
        self.assertIsNotNone(vs)
        self.assertEqual(PPkt.VitalStatus.ALIVE, vs.status)

    def test_deceased_vital_status(self):
        data = ['CGCI.HTMCP-03-06-02007',
                "[{'system': 'GDC', 'field_name': 'case.submitter_id', 'value': 'HTMCP-03-06-02007'}]",
                'Homo sapiens',
                'female',
                'black or african american',
                'not reported',
                '-15987.0',
                "['CGCI-HTMCP-CC']",
                "Dead",
                "343",
                "Cancer Related"]
        series =  pd.Series(data, index=self._column_names)
        ifact = CdaIndividualFactory()
        ga4gh_indi = ifact.from_cancer_data_aggregator(series)
        vs = ga4gh_indi.vital_status
        self.assertIsNotNone(vs)
        self.assertEqual(PPkt.VitalStatus.DECEASED, vs.status)
