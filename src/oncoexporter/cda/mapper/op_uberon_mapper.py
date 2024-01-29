import os

from .op_mapper import OpMapper
from typing import Optional
import pandas as pd
from collections import defaultdict
import phenopackets as PPkt

class OpUberonMapper(OpMapper):
    """A simple mapper for string represeintg anatomical locations to UBERON terms

    TODO -- replace this with file based version covering all of the strings we need in CDA
    """

    def __init__(self):
        """
        This is a simple map from the 'primary_diagnosis_site = row["primary_diagnosis_site"]' field of the diagnosis row
        """
        super().__init__()


    def get_ontology_term(self, row:pd.Series) -> Optional[PPkt.OntologyClass]:
        primary_site = row["primary_diagnosis_site"]
        uberon_label_to_id_d = {'lung': 'UBERON:0002048',
                            "uterine cervix":"UBERON:0000002",
                            "uterus":"UBERON:0000995",
                            "body of uterus":"UBERON:0009853",
                            "lower respiratory tract": "UBERON:0001558"
                            }

        site_to_uberon_label_d = {
            "Lung":"lung",
            "Cervix uteri":"uterine cervix",
            "Cervix":"uterine cervix",
            "Uterus, NOS":"uterus",
            "Corpus uteri":"body of uterus",
            "Uterus":"uterus",
            "Bronchus and lung":"lower respiratory tract"
        }

        ontology_term = PPkt.OntologyClass()
        if primary_site in site_to_uberon_label_d:
            # get standard label and UBEROBN id
            uberon_label = site_to_uberon_label_d.get(primary_site)
            uberon_id = uberon_label_to_id_d.get(uberon_label)
            ontology_term.id = uberon_id
            ontology_term.label = uberon_label
            return ontology_term
        else:
            # TODO -- more robust error handling in final release, but for development fail early
            raise ValueError(f"Could not find UBERON term for primary_site=\"{primary_site}\"")

