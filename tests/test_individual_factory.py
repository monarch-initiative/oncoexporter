import unittest
import os
import pandas as pd
from c2p import IndividualFactory


class TestCaseParse(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        data = ['CGCI.HTMCP-03-06-02007',	
                "[{'system': 'GDC', 'field_name': 'case.submitter_id', 'value': 'HTMCP-03-06-02007'}]",
                'Homo sapiens',
                'female',
                'black or african american',
                'not reported',
                'NaN',
                "['CGCI-HTMCP-CC']",
                "Alive", 
                "NaN",	
                "None"]

        # create a series from the list
        my_series = pd.Series(data)


