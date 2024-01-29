import unittest
import os
import pandas as pd
import phenopackets as PPKt
import pytest

from oncoexporter.cda import CdaDiseaseFactory

# has ten lines
MERGED_DIAG_RESEARCH_DF_FILE = os.path.join(os.path.dirname(__file__), 'data', 'merged_diagnosis_researchsubject_tiny.tsv')

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


class TestCdaDiseaseFactoryTiny(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        df = pd.read_csv(MERGED_DIAG_RESEARCH_DF_FILE, sep="\t")
        diagnosis_id_to_row_d = {}
        for _, row in df.iterrows():
            diagnosis_id = row["diagnosis_id"]
            diagnosis_id_to_row_d[diagnosis_id] = row
        cls._row_d = diagnosis_id_to_row_d

    def test_that_we_ingested_ten_lines(self):
        """simple sanity check for parse
        """
        expected_lines_in_merged_diagnosis_researchsubject_tiny = 10
        parsed_lines = len(self._row_d)
        self.assertEqual(expected_lines_in_merged_diagnosis_researchsubject_tiny, parsed_lines)

    def test_row_1(self):
        """
        CDDP_EAGLE-1.CDDP-ABK3.CDDP-ABK3_diagnosis	[{'system': 'GDC', 'field_name': 'case.diagnoses.diagnosis_id', 'value': '4d75dd99-1c6d-5793-a187-952e1c97dd8d'}, {'system': 'GDC', 'field_name': 'case.diagnoses.submitter_id', 'value': 'CDDP-ABK3_diagnosis'}]	Adenocarcinoma, NOS	73.0	8140/3		not reported	Surgical Resection	CDDP_EAGLE.CDDP-ABK3	CDDP_EAGLE-1.CDDP-ABK3	[{'system': 'GDC', 'field_name': 'case.case_id', 'value': '292b1b0d-3f37-413f-ad95-e99f8afe16e0'}, {'system': 'GDC', 'field_name': 'case.submitter_id', 'value': 'CDDP-ABK3'}]	CDDP_EAGLE-1	Adenomas and Adenocarcinomas	Bronchus and lung	CDDP_EAGLE.CDDP-ABK3pytest
        """
        row = self._row_d.get("CDDP_EAGLE-1.CDDP-ABK3.CDDP-ABK3_diagnosis")
        self.assertIsNotNone(row)
        factory = CdaDiseaseFactory()
        ga4gh_disease = factory.to_ga4gh(row=row)
        self.assertIsNotNone(ga4gh_disease)
        disease_term = ga4gh_disease.term
        self.assertEqual("Lung Adenocarcinoma", disease_term.label)
        self.assertEqual("NCIT:C3512", disease_term.id)
        # 73.0 age at diagnosis
        age_at_diagnosis = ga4gh_disease.onset.age.iso8601duration
        self.assertEqual("P2M13D", age_at_diagnosis)
        # Bronchus and Lung -- we map to "lower respiratory tract": "UBERON:0001558"
        primary_site = ga4gh_disease.primary_site
        self.assertIsNotNone(primary_site)
        self.assertEqual("lower respiratory tract", primary_site.label)
        self.assertEqual("UBERON:0001558", primary_site.id)

