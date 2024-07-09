import os
from collections import defaultdict

import pandas as pd
import phenopackets as pp

import pytest


from oncoexporter.cda import CdaDiseaseFactory
from oncoexporter.cda.mapper import OpDiagnosisMapper


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

    @pytest.fixture
    def factory(self) -> CdaDiseaseFactory:
        return CdaDiseaseFactory(disease_term_mapper=OpDiagnosisMapper.multitissue_mapper())

    @pytest.fixture
    def row(self) -> pd.Series:
        return pd.Series({
            'researchsubject_id': 'CPTAC-3.C3L-04759',
            'diagnosis_id': 'CPTAC-3.C3L-04759.C3L-04759-DIAG',
            'diagnosis_identifier': "[{'system': 'GDC', 'field_name': 'case.diagnoses.diagnosis_id', 'value': '6a88dd2b-dc9b-41e1-9de3-b856f1f243d1'}, {'system': 'GDC', 'field_name': 'case.diagnoses.submitter_id', 'value': 'C3L-04759-DIAG'}]",
            'primary_diagnosis': 'Adenocarcinoma',
            'age_at_diagnosis': '24773.0',
            'morphology': '8140/3',
            'stage': '',
            'grade': 'G2',
            'method_of_diagnosis': '',
            'subject_id_di': 'CPTAC.C3L-04759',
            'subject_id_rs': 'CPTAC.C3L-04759',
            'researchsubject_identifier': "[{'system': 'GDC', 'field_name': 'case.case_id', 'value': '3f92c203-a319-46a6-a627-8027070961fc'}, {'system': 'GDC', 'field_name': 'case.submitter_id', 'value': 'C3L-04759'}]",
            'member_of_research_project': 'CPTAC-3',
            'primary_diagnosis_condition': 'Lung Adenocarcinoma',
            'primary_diagnosis_site': 'Lung',
        })

    def test_parse_ok_row(self, factory: CdaDiseaseFactory,
                          row: pd.Series):
        disease = factory.to_ga4gh(row)

        assert disease is not None

        assert disease.term.label == 'Lung Adenocarcinoma'
        assert disease.term.id == 'NCIT:C3512'

        assert disease.onset.age.iso8601duration == 'P24773D'

        assert disease.primary_site.label == 'lung'
        assert disease.primary_site.id == 'UBERON:0002048'

        assert len(disease.disease_stage) == 1
        assert disease.disease_stage[0].label == 'Stage Unknown'
        assert disease.disease_stage[0].id == 'NCIT:C92207'

        # TODO: these assertions were previously part of the test suite.
        #  However, I am unsure if the TNM info is present in the `row` content.
        #  Reassess and re-enable if yes.
        # assert len(disease.clinical_tnm_finding) == 1
        # assert disease.clinical_tnm_finding[0].id == 'NCIT:C9305'
        # assert disease.clinical_tnm_finding[0].id == 'Malignant Neoplasm'


    class TestStage:

        @pytest.fixture
        def stage_values_test_df(self) -> pd.DataFrame:
            return pd.read_csv(ALL_STAGE_VALUES_TEST_DF_FILE, sep="\t")

        @pytest.fixture
        def disease_objs(self, factory: CdaDiseaseFactory,
                         stage_values_test_df: pd.DataFrame):
            # make a defaultdict
            disease_objs = defaultdict()
            for i, row in stage_values_test_df.iterrows():
                disease_objs[row['subject_id']] = factory.to_ga4gh(row)
            return disease_objs

        def test_disease_stage_is_ontology_term(self, disease_objs):
            assert isinstance(disease_objs['s1'].disease_stage[0], pp.OntologyClass)

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

            expected_oc = pp.OntologyClass()
            expected_oc.id = expected_ncit_ontology[0]
            expected_oc.label = expected_ncit_ontology[1]

            # check that full ontology term is there, both id and label
            assert any([this_term == expected_oc for this_term in disease_obj.disease_stage]), \
                f"Expected ontology term {expected_oc.id} {expected_oc.label}\n" \
                + f" not found in disease_obj.disease_stage terms:\n" \
                + "\n".join([this_term.id + " " + this_term.label for this_term in disease_obj.disease_stage]) \
                + f"while parsing this row\n{this_row}"
