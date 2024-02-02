import typing

import pandas as pd
from .op_mapper import OpMapper
import phenopackets as pp


class OpCauseOfDeathMapper(OpMapper):
    """
    `OpCauseOfDeathMapper` checks if the `cause_of_death` field indicates cancer-related death
    and returns `Cancer-Related Death` (NCIT:C156427) if it does.
    """

    def __init__(self):
        super().__init__(('cause_of_death',))

    def get_ontology_term(self, row: pd.Series) -> typing.Optional[pp.OntologyClass]:
        cause_of_death = row["cause_of_death"]
        if cause_of_death == "Cancer Related":
            oterm = pp.OntologyClass()
            oterm.id = "NCIT:C156427"
            oterm.label = "Cancer-Related Death"
            return oterm
        else:
            return None
