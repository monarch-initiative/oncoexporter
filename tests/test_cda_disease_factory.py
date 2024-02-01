import os

import pandas as pd
import phenopackets as PPKt
import pytest

from oncoexporter.cda import CdaDiseaseFactory


MERGED_DIAG_RESEARCH_DF_FILE = os.path.join(os.path.dirname(__file__), 'data', 'merged_diagnosis_researchsubject_tiny.tsv')
ALL_STAGE_VALUES_TEST_DF_FILE = os.path.join(os.path.dirname(__file__), 'data', 'merged_diagnosis_researchsubject_unique_stages_lung_cervix.tsv')

# Global variables for NCIT ontology terms
STAGE_I = ('NCIT:C27966', 'Stage I')
STAGE_IA = ('NCIT:C27975', 'Stage IA')
STAGE_IB = ('NCIT:C27976', 'Stage IB')
STAGE_II = ('NCIT:C28054', 'Stage II')
STAGE_IIA = ('NCIT:C27967', 'Stage IIA')
STAGE_IIB = ('NCIT:C27968', 'Stage IIB')
STAGE_IIIA = ('NCIT:C27977', 'Stage IIIA')
STAGE_IIIB = ('NCIT:C27978', 'Stage IIIB')
STAGE_IV = ('NCIT:C27971', 'Stage IV')
STAGE_UNKNOWN = ('NCIT:C92207', 'Stage Unknown')


class TestCdaDiseaseFactory:

    @pytest.fixture(scope='class')
    def factory(self) -> CdaDiseaseFactory:
        return CdaDiseaseFactory()

    @pytest.fixture
    def stage_values_test_df(self) -> pd.DataFrame:
        return pd.read_csv(ALL_STAGE_VALUES_TEST_DF_FILE, sep="\t")

    @pytest.fixture
    def disease_objs(self, factory, stage_values_test_df):
        disease_objs = {}
        for i, row in stage_values_test_df.iterrows():
            disease_objs[row['subject_id_rs']] = factory.to_ga4gh(row)
        return disease_objs

    def test_disease_stage_is_ontology_term(self, disease_objs):
        assert isinstance(disease_objs['s1'].disease_stage[0], PPKt.OntologyClass)

    @pytest.mark.parametrize('subject_id, expected_ncit_ontology', [
        ('s1', STAGE_IA),  # IA
        ('s2', STAGE_IB),  # IB
        ('s3', STAGE_IIA),  # IIA
        ('s4', STAGE_IIB),  # IIB
        ('s5', STAGE_IIIA),  # IIIA
        ('s6', STAGE_IIIB),  # IIIB
        ('s7', STAGE_IV),  # IV
        ('s8', STAGE_IA),  # Stage IA
        ('s9', STAGE_IB),  # Stage IB
        ('s10', STAGE_IIA),  # Stage IIA
        ('s11', STAGE_IIB),  # Stage IIB
        ('s12', STAGE_IIIA),  # Stage IIIA
        ('s13', STAGE_UNKNOWN),  # None
        ('s14', STAGE_I),  # Stage I
        ('s15', STAGE_II)  # Stage II
    ])
    def test_correct_stage_parsing(self, subject_id, expected_ncit_ontology,
                                   stage_values_test_df, factory):
        this_row = stage_values_test_df[stage_values_test_df['subject_id_rs'] == subject_id].iloc[0]
        disease_obj = factory.to_ga4gh(this_row)

        expected_oc = PPKt.OntologyClass()
        expected_oc.id = expected_ncit_ontology[0]
        expected_oc.label = expected_ncit_ontology[1]

        # check that full ontology term is there, both id and label
        assert any([this_term == expected_oc for this_term in disease_obj.disease_stage]), \
            f"Expected ontology term {expected_oc.id} {expected_oc.label}\n" \
            + f" not found in disease_obj.disease_stage terms:\n" \
            + "\n".join([this_term.id + " " + this_term.label for this_term in disease_obj.disease_stage]) \
            + f"while parsing this row\n{this_row}"
