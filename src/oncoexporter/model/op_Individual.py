import phenopackets as PPkt
import pandas as pd
from .op_message import OpMessage

class OpIndividual(OpMessage):
    """OncoPacket Individual
    This class should not be used by client code. It provides a DTO-like object to hold
    data that should be instantiated by various factory methods, and it can return
    a GA4GH Individual message


    :param id: the individual identifier (application-specific)
    :type id: str
    :param alternate_ids: list of alternative identifiers, optional
    :type alternate_ids: list
    :param date_of_birth: date of birth of the individual (optional, should not be used without data privacy protection)
    :type date_of_birth: timestamp, optional
    :param iso8601duration: age represented as an ISO 8601 Period, e.g., P42Y5M would be 42 years and 5 months
    :type iso8601duration: str
    :param vital_status: An object representing the Vital status of the individual, optional
    :type vital_status: PPkt.VitalStatus
    :param karyotypic_sex: the chromosomal sex (karyotypic sex), of the individual, e.g., XY or XX or XXY, optional
    :param karyotypic_sex: str (must correspond to the enumerotion in the Phenopacket Schema)
    :param gender: the self-described gender of the individual, optional
    :param taxonomy: Ontology term representing the species of the individual
    :type taxonomy: PPKt.OntologyClass
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
        """Constructor method
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
        """Transform the data in the onject into a GA4GH Phenopacket Individual
        :return: An message corresponding to the GA4GH Phenopacket Individual
        :rtype: PPkt.Individual
        """
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
