import unittest
import os
import pandas as pd

from oncoexporter.cda import CdaDiseaseFactory


DATAFRAME_FILE = os.path.join(os.path.dirname(__file__), 'data', 'merged_diagnosis_researchsubject_tiny.tsv')



class TestCdaDiseaseFactory(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.factory = CdaDiseaseFactory()
        cls._df = pd.read_csv(DATAFRAME_FILE, sep="\t")
        print(cls._df.head())


    def test_something(self):
        print("?")
        print(self._df.head())
        self.assertTrue(1)
