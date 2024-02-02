from typing import Optional

from .op_mapper import OpMapper
import pandas as pd
import phenopackets as PPkt


class OpUberonMapper(OpMapper):
    """
    A simple mapper for string representing anatomical locations to UBERON terms.

    TODO -- replace this with file based version covering all of the strings we need in CDA
    """

    def __init__(self):
        """
        This is a simple map from the 'primary_diagnosis_site = row["primary_diagnosis_site"]' field of the diagnosis row
        """
        super().__init__(('primary_diagnosis_site',))
        self._uberon_label_to_id = {
            'lung': 'UBERON:0002048',
            "uterine cervix": "UBERON:0000002",
            "uterus": "UBERON:0000995",
            "body of uterus": "UBERON:0009853",
            "lower respiratory tract": "UBERON:0001558"
        }
        self._site_to_uberon_label_d = {
            "Lung": "lung",
            "Lung, NOS": "lung",
            "Cervix uteri": "uterine cervix",
            "Cervix Uteri": "uterine cervix",
            "Cervix Uteri, Unknown": "uterine cervix",
            "Cervix": "uterine cervix",
            "Uterus, NOS": "uterus",
            "Corpus uteri": "body of uterus",
            "Corpus Uteri": "body of uterus",
            "Corpus Uteri, Unknown": "body of uterus",
            "Uterus": "uterus",
            "Bronchus and lung": "lower respiratory tract",
            "Lung/Bronchus": "lower respiratory tract",
            "Lung/Bronchus, Unknown": "lower respiratory tract",
        }

    def get_ontology_term(self, row: pd.Series) -> Optional[PPkt.OntologyClass]:
        primary_site = row["primary_diagnosis_site"]


        if primary_site in self._site_to_uberon_label_d:
            # get standard label and UBEROBN id
            ontology_term = PPkt.OntologyClass()
            ontology_term.id = self._uberon_label_to_id.get(self._site_to_uberon_label_d.get(primary_site))
            ontology_term.label = self._site_to_uberon_label_d.get(primary_site)
            return ontology_term
        else:
            # TODO -- more robust error handling in final release, but for development fail early
            raise ValueError(f"Could not find UBERON term for primary_site=\"{primary_site}\"")

