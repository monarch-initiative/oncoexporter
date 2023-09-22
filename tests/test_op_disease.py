import pandas as pd
from unittest import TestCase
import phenopackets as PPkt
from src.oncopacket.model import OpIndividual
from src.oncopacket.cda import CdaDiseaseFactory


class OpDiseaseTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        data = ["CGCI-HTMCP-CC.HTMCP-03-06-02003.HTMCP-03-06-02003_diagnosis",
                "[{'system': 'GDC', 'field_name': 'case.diagnoses.diagnosis_id', 'value': '1ffb1fc3-b47f-5934-9927-1a5156e159d8'},{'system': 'GDC', 'field_name': 'case.diagnoses.submitter_id', 'value': 'HTMCP-03-06-02003_diagnosis'}]",
                "Squamous cell carcinoma, nonkeratinizing, NOS",
                "NaN",
                "8072/3",
                "None",
                "G2",
                "Biopsy",
                "CGCI.HTMCP-03-06-02003",
                "CGCI-HTMCP-CC.HTMCP-03-06-02003"]
        cls._column_names = ['diagnosis_id', 'diagnosis_identifier', 'primary_diagnosis',
                             'age_at_diagnosis', 'morphology', 'stage', 'grade',
                             'method_of_diagnosis', 'subject_id', 'researchsubject_id']
        cls._series = pd.Series(data, index=cls._column_names)

    def test_creation(self):
        dfact = CdaDiseaseFactory()
        self.assertIsNotNone(dfact)
        ga4gh_disease = dfact.from_cancer_data_aggregator(self._series)
        self.assertIsNotNone(ga4gh_disease)

    def test_id(self):
        dfact = CdaDiseaseFactory()
        ga4gh_disease = dfact.from_cancer_data_aggregator(self._series)
        expected_id = 'CGCI.HTMCP-03-06-02007'
        self.assertEqual(expected_id, ga4gh_disease.id)
