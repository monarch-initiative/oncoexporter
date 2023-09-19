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
        if vital_status == "Alive":
            self._vital_status = PPkt.VitalStatus()
            self._vital_status.status = PPkt.VitalStatus.ALIVE
        else:
            self._vital_status = None

    def to_ga4gh(self):
        individual =  PPkt.Individual()
        individual.id = self._id
        if self._iso8601duration is not None:
            individual.time_at_last_encounter.age.iso8601duration = self._iso8601duration
        individual.sex = self._sex
        if self._taxonomy is not None:
            individual.taxonomy.CopyFrom(self._taxonomy)
        if self._vital_status is not None:
            individual.vital_status.CopyFrom(self._vital_status)
        return individual


class IndividualFactory(MessageFactory):
    """
    Create GA4GH individual messages from other data sources. Each data source performs ETL to
    create an instance of the C2pIndivual class and then returns a GA4GH Individual object.
    """
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def days_to_iso(days: int):
        """
        Convert the number of days of life into an ISO 8601 period representing the age of an individual
        (e.g., P42Y7M is 42 years and 7 months).
        # FYI this exists:
        # https://pypi.org/project/iso8601/

        :param days: number of days of life (str or int)
        """
        if isinstance(days, str):
            days = int(str)
        if not isinstance(days, int):
            raise ValueError(f"days argument must be int or str but was {type(days)}")
        # slight simplification
        days_in_year = 365.2425
        y = int(days/days_in_year)
        days = days - int(y*days_in_year)
        m = int(days/12)
        days = days - int(m*12)
        w = int(days/7)
        days = days - int(w*7)
        d = days
        iso = "P"
        if y > 0:
            iso = f"{iso}{y}Y"
        if m > 0:
            iso = f"{iso}{m}M"
        if w > 0:
            iso = f"{iso}{w}W"
        if d > 0:
            iso = f"{iso}{d}D"
        return iso


    @staticmethod
    def days_to_iso(days:int):
        """
        Convert the number of days of life into an ISO 8601 period representing the age of an individual
        (e.g., P42Y7M is 42 years and 7 months).
        # FYI this exists:
        # https://pypi.org/project/iso8601/

        :param days: number of days of life (str or int)
        """
        if isinstance(days, str):
            days = int(str)
        if not isinstance(days, int):
            raise ValueError(f"days argument must be int or str but was {type(days)}")
        # slight simplification
        days_in_year = 365.2425
        y = int(days/days_in_year)
        days = days - int(y*days_in_year)
        m = int(days/12)
        days = days - int(m*12)
        w = int(days/7)
        days = days - int(w*7)
        d = days
        iso = "P"
        if y > 0:
            iso = f"{iso}{y}Y"
        if m > 0:
            iso = f"{iso}{m}M"
        if w > 0:
            iso = f"{iso}{w}W"
        if d > 0:
            iso = f"{iso}{d}D"
        return iso


    @staticmethod
    def process_vital_status():
        return None

    def from_cancer_data_aggregator(self, row):
        """
        convert a row from the CDA subject table into an Individual message (GA4GH Phenopacket Schema)
        The row is a pd.core.series.Series and contains the columns
        ['subject_id', 'subject_identifier', 'species', 'sex', 'race',
       'ethnicity', 'days_to_birth', 'subject_associated_project',
       'vital_status', 'days_to_death', 'cause_of_death']
       :param row: a row from the CDA subject table
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
        # a valid date looks like this: '-15987.0'
        if days_to_birth.startswith("-"):
            days_to_birth = days_to_birth[1:]
        iso_age = None
        try:
            # we need to parse '15987.0' first as a float and then transform to int
            d_to_b = int(float(days_to_birth))
            iso_age = IndividualFactory.days_to_iso(days=d_to_b)
        except:
            pass
        subject_associated_project = row['subject_associated_project']

        # status_object = process_vital_status(row)
        #
        # if status_object is not None:
        #     vital_status = status_object.vital_status
        #     days_to_death = status_object.days_to_death
        #     cause_of_death = status_object.cause_of_death

        # TODO figure out where to store project data
        c2pi = C2pIndividual(id=subject_id, iso8601duration=iso_age, sex=sex, taxonomy=species)
        return c2pi.to_ga4gh()
