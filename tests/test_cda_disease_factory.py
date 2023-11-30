import unittest
import os
import pandas as pd
import phenopackets as PPKt

from oncoexporter.cda import CdaDiseaseFactory


MERGED_DIAG_RESEARCH_DF_FILE = os.path.join(os.path.dirname(__file__), 'data', 'merged_diagnosis_researchsubject_tiny.tsv')
ALL_STAGE_VALUES_TEST_DF_FILE = os.path.join(os.path.dirname(__file__), 'data', 'merged_diagnosis_researchsubject_unique_stages_lung_cervix.tsv')

class TestCdaDiseaseFactory(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.factory = CdaDiseaseFactory()
        cls.merged_diag_research_test_df = pd.read_csv(MERGED_DIAG_RESEARCH_DF_FILE, sep="\t")
        cls.stage_values_test_df = pd.read_csv(ALL_STAGE_VALUES_TEST_DF_FILE, sep="\t")

    def test_correct_stage_parsing(self):
        # maybe this should be a parameterized test, but I don't see an elegant way of
        # doing that

        correct_stage_by_row = [
            'NCIT:C27966',  # IA == stage I
            'NCIT:C27966',  # IB == stage I
            'NCIT:C28054',  # IIA == stage II
            'NCIT:C28054',  # IIB == stage II
            'NCIT:C27970',  # IIIA == stage III
            'NCIT:C27970',  # IIIB == stage III
            'NCIT:C27971',  # IV == stage IV
            'NCIT:C27966',  # Stage IA == stage I
            'NCIT:C27966',  # Stage IB
            'NCIT:C28054',  # Stage IIA
            'NCIT:C28054',  # Stage IIB
            'NCIT:C27970',  # Stage IIIA
            'NCIT:C92207',  # None == cancer stage unknown = C92207
            'NCIT:C27966',  # Stage I
            'NCIT:C28054',  # Stage II
         ]
        for i, row in self.stage_values_test_df.iterrows():
            disease_obj = self.factory.to_ga4gh(row)
            disease_stage_ids = [o.id for o in disease_obj.disease_stage]
            self.assertTrue(correct_stage_by_row[i] in disease_stage_ids,
                       f"Couldn't find expected stage "
                       f"NCIT id {correct_stage_by_row[i]} "
                       f"in disease_obj.disease_stage IDs {disease_stage_ids} ")
