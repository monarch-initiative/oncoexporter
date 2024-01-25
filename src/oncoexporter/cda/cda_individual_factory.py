import typing

import phenopackets as PPkt
import pandas as pd

from  .mapper.op_cause_of_death_mapper import OpCauseOfDeathMapper
from .cda_factory import CdaFactory


class CdaIndividualFactory(CdaFactory):
    """
    `CdaIndividualFactory` creates a GA4GH individual messages from a row of the CDA *subject* table.

    The structure of the CDA subject table is as follows:

        - subject_id (*)
        - subject_identifier
        - species
        - sex (*)
        - race
        - ethnicity
        - days_to_birth (*)
        - subject_associated_project
        - vital_status (*)
        - days_to_death (*)
        - cause_of_death (*)

    (*) indicates a used field.
    """

    def __init__(self) -> None:
        self._cause_of_death_mapper = OpCauseOfDeathMapper()
        self._male_sex = {'m', 'male'}
        self._female_sex = {'f', 'female'}

    def _process_vital_status(self, row: pd.Series):
        """
        :param row: a row from the CDA subject table
        :type row: pd.Series
        :returns: A vital status object with information about cause of death if applicable.
        :rtype: PPkt.VitalStatus
        """
        if not isinstance(row, pd.Series):
            raise ValueError(f"'row' argument must be pandas Series but was {type(row)}")
        vital_status = self.get_item(row, "vital_status")
        days_to_death = self.get_item(row, "days_to_death")
        if vital_status is None:
            return None
        valid_status = {"Alive", "Dead"}
        if vital_status not in valid_status:
            return None
        vstatus = PPkt.VitalStatus()
        if vital_status == "Alive":
            vstatus.status = PPkt.VitalStatus.ALIVE
        elif vital_status == "Dead":
            vstatus.status = PPkt.VitalStatus.DECEASED
        if days_to_death is not None:
            try:
                dtd = int(days_to_death)
                vstatus.survival_time_in_days = dtd
            except:
                # TODO: report?
                pass
        cause = self._cause_of_death_mapper.get_ontology_term(row)
        if cause is not None:
            vstatus.cause_of_death.CopyFrom(cause)
        return vstatus

    def to_ga4gh(self, row:pd.Series):
        """
        convert a row from the CDA subject table into an Individual message (GA4GH Phenopacket Schema)

        :param row: a row from the CDA subject table
        :type row: pd.Series
        :returns: A GA4GH Phenopacket Schema Individual object that corresponds to the subject in this row.
        :rtype: PPkt.Individual
        :raises ValueError: if the input is unparsable.
        """
        if not isinstance(row, pd.Series):
            raise ValueError(f"Invalid argument. Expected pandas series but got {type(row)}")
        row = row.astype(str)
        subject_id = row['subject_id']
        # subject_identifier = row['subject_identifier']
        # species = row['species']
        sex = row['sex']
        # race = row['race']
        # ethnicity = row['ethnicity']
        days_to_birth = row['days_to_birth']
        # a valid date looks like this: '-15987.0'
        if days_to_birth.startswith("-"):
            days_to_birth = days_to_birth[1:]
        iso_age = None
        vstat = None
        try:
            # we need to parse '15987.0' first as a float and then transform to int
            d_to_b = int(float(days_to_birth))
            iso_age = self.days_to_iso(days=d_to_b)
            vstat = self._process_vital_status(row)
        except Exception:
            # TODO: handle in a better way
            pass
        # subject_associated_project = row['subject_associated_project']


        individual = PPkt.Individual()
        individual.id = subject_id

        # time_at_last_encounter
        if iso_age is not None:
            individual.time_at_last_encounter.age.iso8601duration = iso_age

        # vital status
        if vstat is not None:
            individual.vital_status.CopyFrom(vstat)

        # sex
        if sex in self._male_sex:
            individual.sex = PPkt.MALE
        elif sex in self._female_sex:
            individual.sex = PPkt.FEMALE
        else:
            individual.sex = PPkt.UKNOWN_SEX

        # taxonomy, always Homo here
        individual.taxonomy.id = "NCBITaxon:9606"
        individual.taxonomy.label = "Homo sapiens"

        return individual
