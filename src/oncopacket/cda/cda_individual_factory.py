import phenopackets as PPkt
import pandas as pd

from ..model.op_Individual import OpIndividual


class CdaIndividualFactory():
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
            iso_age = CdaIndividualFactory.days_to_iso(days=d_to_b)
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
        c2pi = OpIndividual(id=subject_id, iso8601duration=iso_age, sex=sex, taxonomy=species)
        return c2pi.to_ga4gh()
