import unittest
import pandas as pd

from oncoexporter.cda.mapper.op_diagnosis_mapper import OpDiagnosisMapper




class OpDiagnosisMapperTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls._op_dx_mapper = OpDiagnosisMapper()

    def test_acantholytic(self):
        column_names = ["primary_diagnosis", "primary_diagnosis_condition", "primary_diagnosis_site"]
        data = ["Acantholytic squamous cell carcinoma", "Lung Squamous Cell Carcinoma", "Lung"]
        series = pd.Series(data, column_names)
        oterm = self._op_dx_mapper.get_ontology_term(row=series)
        self.assertIsNotNone(oterm)
        self.assertEqual("NCIT:C3493", oterm.id)
        self.assertEqual("Lung Squamous Cell Carcinoma", oterm.label)


    def test_lung_adenocarcinoma(self):
        """
        Adenocarcinoma	Lung Adenocarcinoma	Lung	NCIT:C3512	Lung Adenocarcinoma
        """
        column_names = ["primary_diagnosis", "primary_diagnosis_condition","primary_diagnosis_site"]
        data = ["Adenocarcinoma", "Lung Adenocarcinoma", "Lung"]
        series = pd.Series(data, column_names)
        oterm = self._op_dx_mapper.get_ontology_term(row=series)
        self.assertIsNotNone(oterm)
        self.assertEqual("NCIT:C3512", oterm.id)
        self.assertEqual("Lung Adenocarcinoma", oterm.label)


    def test_scc_lung(self):
        column_names = ["primary_diagnosis", "primary_diagnosis_condition", "primary_diagnosis_site"]
        data = ["Squamous Cell Carcinoma", "Lung Squamous Cell Carcinoma", "Lung"]
        series = pd.Series(data, column_names)
        oterm = self._op_dx_mapper.get_ontology_term(row=series)
        self.assertIsNotNone(oterm)
        self.assertEqual("NCIT:C3493", oterm.id)
        self.assertEqual("Lung Squamous Cell Carcinoma", oterm.label)



