import phenopackets as PPkt
import pandas as pd
from .op_message import OpMessage

class OpIndividual(OpMessage):
    """OncoPacket Individual
    This class should not be used by client code. It provides a DTO-like object to hold
    data that should be instantiated by various factory methods, and it can return
    a GA4GH Individual message
    """
    def __init__(self, id,
                 alternate_ids = [],
                 date_of_birth=None,
                 iso8601duration=None,
                 vital_status=None,
                 sex=None,
                 karyotypic_sex=None,
                 gender=None,
                 taxonomy=None) -> None:
        """
        :param id: the individual identifier (application-specific)

        """
        self._id = id
        # todo add check for date_of_birth, leaving out for now
        self._iso8601duration = iso8601duration
        male_sex = {"m", "male"}
        female_sex = {"f",  "female",}
        if sex.lower() in male_sex:
            self._sex = PPkt.MALE
        elif sex.lower() in female_sex:
             self._sex = PPkt.FEMALE
        else:
            self._sex = PPkt.UNKNOWN_SEX
        if taxonomy == 'Homo sapiens':
            self._taxonomy = PPkt.OntologyClass()
            self._taxonomy.id = "NCBITaxon:9606"
            self._taxonomy.label = "homo sapiens sapiens"
        elif taxonomy is not None:
            raise ValueError(f"Unknown species {taxonomy}")
        else:
            self._taxonomy = None
        self._vital_status = vital_status


    def to_ga4gh(self):
        individual =  PPkt.Individual()
        individual.id = self._id
        if self._iso8601duration is not None:
            individual.time_at_last_encounter.age.iso8601duration = self._iso8601duration
        individual.sex = self._sex
        if self._taxonomy is not None:
            individual.taxonomy.CopyFrom(self._taxonomy)
        if self._vital_status is not None:
            individual.vital_status.status = self._vital_status.status
        return individual
