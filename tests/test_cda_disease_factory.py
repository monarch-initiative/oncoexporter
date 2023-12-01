import unittest
import os
import pandas as pd
from parameterized import parameterized
import phenopackets as PPKt
from oncoexporter.cda import CdaDiseaseFactory


MERGED_DIAG_RESEARCH_DF_FILE = os.path.join(os.path.dirname(__file__), 'data', 'merged_diagnosis_researchsubject_tiny.tsv')
ALL_STAGE_VALUES_TEST_DF_FILE = os.path.join(os.path.dirname(__file__), 'data', 'merged_diagnosis_researchsubject_unique_stages_lung_cervix.tsv')

# Global variables for NCIT ontology terms
STAGE_IA = ('NCIT:C27975', 'Stage IA')
STAGE_IB = ('NCIT:C27976', 'Stage IB')
STAGE_IIA = ('NCIT:C27967', 'Stage IIA')
STAGE_IIB = ('NCIT:C27968', 'Stage IIB')
STAGE_IIIA = ('NCIT:C27977', 'Stage IIIA')
STAGE_IIIB = ('NCIT:C27978', 'Stage IIIB')
STAGE_IV = ('NCIT:C27971', 'Stage IV')
STAGE_UNKNOWN = ('NCIT:C92207', 'Stage Unknown')
STAGE_I = ('NCIT:C27966', 'Stage I')
STAGE_II = ('NCIT:C28054', 'Stage II')

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
        ('s1', STAGE_IA),
        ('s2', STAGE_IB),
        ('s3', STAGE_IIA),
        ('s4', STAGE_IIB),
        ('s5', STAGE_IIIA),
        ('s6', STAGE_IIIB),
        ('s7', STAGE_IV),
        ('s8', STAGE_IA),
        ('s9', STAGE_IB),
        ('s10', STAGE_IIA),
        ('s11', STAGE_IIB),
        ('s12', STAGE_IIIA),
        ('s13', STAGE_UNKNOWN),
        ('s14', STAGE_I),
        ('s15', STAGE_II)
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
