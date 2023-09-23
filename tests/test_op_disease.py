import pandas as pd
from unittest import TestCase

import phenopackets as PPkt
import pytest

from src.oncoexporter.model import OpIndividual
from src.oncoexporter.cda import CdaDiseaseFactory


class OpDiseaseTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        data_1 = ["PDC000220.P065.P065-DX",
                  "[{'system': 'PDC', 'field_name': 'Diagnosis.diagnosis_id', 'value': '24b7022a-8beb-11ea-b1fd-0aad30af8a83'}, {'system': 'PDC', 'field_name': 'Diagnosis.diagnosis_submitter_id', 'value': 'P065-DX'}]",
                  "None",
                  "NaN",
                  "None",
                  "None",
                  "None",
                  "None",
                  "Academia Sinica LUAD-100.P065",
                  "PDC000220.P065",
                  "PDC000219.P065",
                  "[{'system': 'PDC', 'field_name': 'Case.case_id', 'value': '24b3ad62-8beb-11ea-b1fd-0aad30af8a83'}, {'system': 'PDC', 'field_name': 'Case.case_submitter_id', 'value': 'P065'}]",
                  "PDC000219",
                  "None",
                  "Lung"]
        cls._column_names = ['diagnosis_id', 'diagnosis_identifier', 'primary_diagnosis',
                             'age_at_diagnosis', 'morphology', 'stage', 'grade',
                             'method_of_diagnosis', 'subject_id', 'researchsubject_id_di',
                             'researchsubject_id_rs', 'researchsubject_identifier',
                             'member_of_research_project', 'primary_diagnosis_condition',
                             'primary_diagnosis_site']
        assert len(data_1) == len(cls._column_names)
        cls._series = pd.Series(data_1, index=cls._column_names)

    def _create_series(self, primary_diagnosis=None,
                       age_at_diagnosis=None,
                       morphology=None,
                       stage=None,
                       grade=None):
        series = self._series.copy()
        if primary_diagnosis is not None:
            series["primary_diagnosis"] = primary_diagnosis
        if age_at_diagnosis is not None:
            series["age_at_diagnosis"] = age_at_diagnosis
        if morphology is not None:
            series["morphology"] = morphology
        if stage is not None:
            series["stage"] = stage
        if grade is not None:
            series["grade"] = grade
        return series

    def test_creation(self):
        dfact = CdaDiseaseFactory()
        self.assertIsNotNone(dfact)
        ga4gh_disease = dfact.from_cancer_data_aggregator(self._series)
        self.assertIsNotNone(ga4gh_disease)

    def test_ontology_class_id(self):
        dfact = CdaDiseaseFactory()
        ga4gh_disease = dfact.from_cancer_data_aggregator(self._series)
        self.assertNotEquals(ga4gh_disease.term.id, '')
        self.assertNotEquals(ga4gh_disease.term.label, '')

    def test_parsing_disease_into_ontology_classes(self):
        data = get_disease_test_data()
        for d in data:
            dfact = CdaDiseaseFactory()
            this_series = self._series.copy()
            this_series['primary_diagnosis'] = d['primary_diagnosis']
            this_series['primary_diagnosis_condition'] = d['primary_diagnosis_condition']
            this_series['primary_diagnosis_site'] = d['primary_diagnosis_site']
            ga4gh_disease = dfact.from_cancer_data_aggregator(this_series)
            self.assertEqual(d['id'], ga4gh_disease.term.id)
            self.assertEqual(d['label'], ga4gh_disease.term.label)
            pass


def get_disease_test_data():
    data = [
        {
            "primary_diagnosis": "",
            "primary_diagnosis_condition": "Lung",
            "primary_diagnosis_site": "",
            "id": "NCIT:C3200",
            "label": "Lung Neoplasm",
        },
        {
            "primary_diagnosis": "Adenocarcinoma",
            "primary_diagnosis_condition": "Lung Adenocarcinoma",
            "primary_diagnosis_site": "Lung",
            "id": "NCIT:C3512",
            "label": "Lung Adenocarcinoma",
        },
        {
            "primary_diagnosis": "Acantholytic squamous cell carcinoma",
            "primary_diagnosis_condition": "Lung Squamous Cell Carcinoma",
            "primary_diagnosis_site": "Lung",
            "id": "NCIT:C3493",
            "label": "Lung Squamous Cell Carcinoma",
        },
        {
            "primary_diagnosis": "Adenocarcinoma, NOS",
            "primary_diagnosis_condition": "Lung Adenocarcinoma",
            "primary_diagnosis_site": "Lung",
            "id": "NCIT:C3512",
            "label": "Lung Adenocarcinoma",
        },
        {
            "primary_diagnosis": "Squamous Cell Carcinoma",
            "primary_diagnosis_condition": "Lung Squamous Cell Carcinoma",
            "primary_diagnosis_site": "Lung",
            "id": "NCIT:C3493",
            "label": "Lung Squamous Cell Carcinoma",
        },
        {
            "primary_diagnosis": "Clear cell adenocarcinoma, NOS",
            "primary_diagnosis_condition": "Lung Adenocarcinoma",
            "primary_diagnosis_site": "Lung",
            "id": "NCIT:C45516",
            "label": "Lung Adenocarcinoma",
        },
        {
            "primary_diagnosis": "Squamous Cell Carcinoma",
            "primary_diagnosis_condition": "Lung Adenocarcinoma",
            "primary_diagnosis_site": "Lung",
            "id": "NCIT:C9133",
            "label": "Lung Adenosquamous Carcinoma",
        },
        {
            "primary_diagnosis": "Adenosquamous carcinoma",
            "primary_diagnosis_condition": "Lung Adenocarcinoma",
            "primary_diagnosis_site": "Lung",
            "id": "NCIT:C9133",
            "label": "Lung Adenosquamous Carcinoma",
        },
    ]
    return data
