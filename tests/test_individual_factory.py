import unittest
import os
import pandas as pd
from c2p import IndividualFactory


class TestCaseParse(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        data = ['CGCI.HTMCP-03-06-02007',	
                "[{'system': 'GDC', 'field_name': 'case.submitter_id', 'value': 'HTMCP-03-06-02007'}]",
                'Homo sapiens',
                'female',
                'black or african american',
                'not reported',
                'NaN',
                "['CGCI-HTMCP-CC']",
                "Alive", 
                "NaN",	
                "None"]
        column_names = ['subject_id', 'subject_identifier', 'species', 'sex', 'race',
       'ethnicity', 'days_to_birth', 'subject_associated_project',
       'vital_status', 'days_to_death', 'cause_of_death']
        cls._series = pd.Series(data, index=column_names)

    def test_creation(self):
        ifact = IndividualFactory()
        self.assertIsNotNone(ifact)
        ga4gh_indi = ifact.from_cancer_data_aggregator(self._series)
        self.assertIsNotNone(ga4gh_indi)
    
    def test_id(self):
        ifact = IndividualFactory()
        ga4gh_indi = ifact.from_cancer_data_aggregator(self._series)
        expected_id = 'CGCI.HTMCP-03-06-02007'
        self.assertEquals(expected_id, ga4gh_indi.id)



