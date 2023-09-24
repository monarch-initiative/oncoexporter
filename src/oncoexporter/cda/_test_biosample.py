import unittest

import pandas as pd

from ._biosample import make_cda_biosample

cols = ['specimen_id', 'specimen_associated_project',
       'days_to_collection', 'primary_disease_type', 'anatomical_site',
       'source_material_type', 'specimen_type', 'derived_from_specimen',
       'derived_from_subject', 'subject_id', 'researchsubject_id']


class TestMakeBiosample(unittest.TestCase):

    def test_bla(self):
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
            'Academia',
            'Sinica',
            'LUAD - 100.',
            'P067',
            'PDC000219.P067'
        ]
        row = pd.Series({key: val for key, val in zip(cols, vals)})
        biosample = make_cda_biosample(row)
        print(biosample)
