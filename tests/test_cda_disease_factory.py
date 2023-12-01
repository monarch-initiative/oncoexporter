import unittest
import os
from typing import List

import pandas as pd
from parameterized import parameterized
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

        cls.disease_objs = {}
        for i, row in cls.stage_values_test_df.iterrows():
            cls.disease_objs[row['subject_id_rs']] = cls.factory.to_ga4gh(row)

    def test_disease_stage_is_ontology_term(self):
        self.assertEqual(self.disease_objs['s1'].disease_stage[0].__class__,
                         PPKt.OntologyClass)

    @parameterized.expand([
        ('s1', ('NCIT:C27975', 'Stage IA')),         # IA == stage IA
        ('s2', ('NCIT:C27976', 'Stage IB')),         # IB == stage IB
        ('s3', ('NCIT:C27967', 'Stage IIA')),        # IIA == stage IIA
        ('s4', ('NCIT:C27968', 'Stage IIB')),        # IIB == stage IIB
        ('s5', ('NCIT:C27977', 'Stage IIIA')),       # IIIA == stage IIIA
        ('s6', ('NCIT:C27978', 'Stage IIIB')),       # IIIB == stage IIIB
        ('s7', ('NCIT:C27971', 'Stage IV')),        # IV == stage IV
        ('s8', ('NCIT:C27975', 'Stage IA')),         # Stage IA
        ('s9', ('NCIT:C27976', 'Stage IB')),         # Stage IB
        ('s10', ('NCIT:C27967', 'Stage IIA')),       # Stage IIA
        ('s11', ('NCIT:C27968', 'Stage IIB')),       # Stage IIB
        ('s12', ('NCIT:C27977', 'Stage IIIA')),      # Stage IIIA
        ('s13', ('NCIT:C92207', 'Stage Unknown')),  # None == Stage Unknown = C92207
        ('s14', ('NCIT:C27966', 'Stage I')),        # Stage I
        ('s15', ('NCIT:C28054', 'Stage II'))        # Stage II
    ])
    def test_correct_stage_parsing(self, subject_id, expected_ncit_ontology):
        this_row = self.stage_values_test_df[
            self.stage_values_test_df['subject_id_rs'] == subject_id].iloc[0]
        disease_obj = self.factory.to_ga4gh(this_row)

        expected_oc = PPKt.OntologyClass()
        expected_oc.id = expected_ncit_ontology[0]
        expected_oc.label = expected_ncit_ontology[1]

        # check that full ontology term is there, both id and label
        self.assertTrue(
            any([this_term == expected_oc for this_term in disease_obj.disease_stage]),
            msg = f"Expected ontology term {expected_oc.id} {expected_oc.label}\n" +
            f" not found in disease_obj.disease_stage terms:\n" +
            "\n".join([this_term.id + " " + this_term.label for this_term in disease_obj.disease_stage]) +
            f"while parsing this row\n{this_row}"
        )
