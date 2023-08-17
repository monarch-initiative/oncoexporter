from .message_factory import MessageFactory
import phenopackets as PPkt
import pandas as pd


class C2pIndividual:
    """
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
        self._id = id
        # todo add check for date_of_birth, leaving out for now
        self._iso8601duration = iso8601duration
        if sex == 'M':
            self._sex = PPkt.MALE
        elif sex == 'F':
             self._sex = PPkt.FEMALE
        else:
            self._sex = PPkt.UNKNOWN_SEX
        if taxonomy == 'Homo sapiens':
            pass # TODO
        else:
            raise ValueError(f"Unknown species {taxonomy}")


        


    def to_ga4gh(self):
        individual =  PPkt.Individual()
        individual.id = self._id
        if self._iso8601duration is not None:
            individual.time_at_last_encounter.age.iso8601duration = self._iso8601duration
        individual.sex = self._sex
        return individual




class IndividualFactory(MessageFactory):
    """
    Create GA4GH individual messages from other data sources. Each data source performs ETL to
    create an instance of the C2pIndivual class and then returns a GA4GH Individual object.
    """
    def __init__(self) -> None:
        super().__init__()
    


    def from_cancer_data_aggregator(self, row):
        """
        core.series.Series
        Index(['subject_id', 'subject_identifier', 'species', 'sex', 'race',
       'ethnicity', 'days_to_birth', 'subject_associated_project',
       'vital_status', 'days_to_death', 'cause_of_death'],
        dtype='object')
        """
        if not isinstance(row, pd.core.series.Series):
            raise ValueError(f"Invalid argument. Expected pandas series but got {type(row)}")
        row = row.astype(str)
        subject_id = row['subject_id']
        subject_identifier = row['subject_identifier']
        species = row['species']
        sex = row['sex']
        race = row['race']
        ethnicity = row['ethnicity']
        days_to_birth = row['days_to_birth']
        subject_associated_project = row['subject_associated_project']
        vital_status = row['vital_status']
        days_to_death = row['days_to_death']
        cause_of_death = row['cause_of_death']
        # TODO vital status
        # TODO isoduration
        return C2pIndividual(id=subject_id, sex=sex, taxonomy=species)
