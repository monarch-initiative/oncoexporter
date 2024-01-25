import os

from .op_mapper import OpMapper
from typing import Optional
import phenopackets as PPkt

class OpCauseOfDeathMapper(OpMapper):

    def get_ontology_term(self, row) -> Optional[PPkt.OntologyClass]:
        oterm = PPkt.OntologyClass()
        cause_of_death = row["cause_of_death"]
        if cause_of_death == "Cancer Related":
            oterm.id = "NCIT:C156427"
            oterm.label = "Cancer-Related Death"
            return oterm
        else:
            return None
