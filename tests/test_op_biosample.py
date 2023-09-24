import unittest

import pandas as pd

from oncoexporter.cda import CdaBiosampleFactory

cols = ['specimen_id', 'specimen_associated_project',
       'days_to_collection', 'primary_disease_type', 'anatomical_site',
       'source_material_type', 'specimen_type', 'derived_from_specimen',
       'derived_from_subject', 'subject_id', 'researchsubject_id']


class TestMakeBiosample(unittest.TestCase):

    def setUp(self) -> None:
        self.factory = CdaBiosampleFactory()

    def test_create_biosample(self):
        vals = [
            'PDC000219.P067.P067 - 2 - 1',
            'PDC000219;PDC000220',
            'NaN',
            'Lung Adenocarcinoma',
            None,
            None,
            'aliquot',
            'PDC000220.P067.P067-2',
            'Academia Sinica LUAD - 100.P067',
            'Academia Sinica LUAD - 100.P067',
            'PDC000219.P067'
        ]
        row = pd.Series({key: val for key, val in zip(cols, vals)})
        biosample = self.factory.from_cancer_data_aggregator(row)
        
        self.assertEqual(biosample.id, "PDC000219.P067.P067 - 2 - 1")

        self.assertEqual(biosample.sample_type.id, "NCIT:C25414")
        self.assertEqual(biosample.sample_type.label, "Aliquot")

        self.assertEqual(biosample.taxonomy.id, "NCBITaxon:9606")
        self.assertEqual(biosample.taxonomy.label, "Homo sapiens")

        self.assertEqual(biosample.histological_diagnosis.id, "NCIT:C3512")
        self.assertEqual(biosample.histological_diagnosis.label, "Lung Adenocarcinoma")

        self.assertEqual(biosample.individual_id, "Academia Sinica LUAD - 100.P067")

        self.assertEqual(biosample.derived_from_id, "PDC000220.P067.P067-2")
        