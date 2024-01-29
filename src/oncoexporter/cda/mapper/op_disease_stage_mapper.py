import os

from .op_mapper import OpMapper
from typing import Optional
import pandas as pd
from collections import defaultdict
import phenopackets as PPkt

class OpDiseaseStageMapper(OpMapper):

    def __init__(self):
        """
        This is a simple map from the 'stage' field of the diagnosis row
        """
        super().__init__()

    def get_ontology_term(self, row:pd.Series) -> Optional[PPkt.OntologyClass]:
        stage_str = row["stage"]
        ncit_label_to_id_d = {'Stage I': 'NCIT:C27966',
                            'Stage IA':'NCIT:C27975',
                            'Stage IB': 'NCIT:C27976',
                            'Stage II':'NCIT:C28054',
                            'Stage IIA':'NCIT:C27967',
                            'Stage IIB':'NCIT:C27968',
                            'Stage III':'NCIT:C27970',
                            'Stage IIIA': 'NCIT:C27977',
                            'Stage IIIB': 'NCIT:C27978',
                            'Stage IV': 'NCIT:C27971'
                            }
        stage_d = {'Stage I': 'Stage I',
                'Stage 1': 'Stage I',
                'stage I': 'Stage I',
                'stage 1': 'Stage I',
                'IA':'Stage IA',
                'Stage IA':'Stage IA',
                'stage IA':'Stage IA',
                'IB':'Stage IB',
                'Stage IB':'Stage IB',
                'stage IB':'Stage IB',
                'Stage II':'Stage II',
                'Stage 2':'Stage II',
                'stage 2':'Stage II',
                'stage II':'Stage II',
                'IIA':'Stage IIA',
                'Stage IIA':'Stage IIA',
                'stage IIA':'Stage IIA',
                'IIB':'Stage IIB',
                'Stage IIB':'Stage IIB',
                'stage IIB':'Stage IIB',
                'Stage 3':'Stage III',
                'stage 3':'Stage III',
                'Stage III':'Stage III',
                'stage III':'Stage III',
                'IIIA':'Stage IIIA',
                'Stage IIIA':'Stage IIIA',
                'Stage 3A':'Stage IIIA',
                'stage 3A':'Stage IIIA',
                'IIIB':'Stage IIIB',
                'Stage IIIB':'Stage IIIB',
                'Stage 3B':'Stage IIIB',
                'stage 3B':'Stage IIIB',
                'IV':'Stage IV',
                'Stage 4':'Stage IV',
                'Stage IV':'Stage IV',
                'stage IV':'Stage IV'
                }
        ontology_term = PPkt.OntologyClass()
        if stage_str in stage_d:
            # get standard label and NCIT id
            stage_label = stage_d.get(stage_str)
            stage_id = ncit_label_to_id_d.get(stage_label)
            ontology_term.id = stage_id
            ontology_term.label = stage_label
        else:
            ontology_term.id ='NCIT:C92207'  # Stage unknown
            ontology_term.label = 'Stage Unknown'
        return ontology_term