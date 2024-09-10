import itertools

import pandas as pd
import phenopackets as pp


from .mapper.op_mapper import OpMapper
from .mapper.op_disease_stage_mapper import OpDiseaseStageMapper
from .mapper.op_uberon_mapper import OpUberonMapper
from .cda_factory import CdaFactory


class CdaDiseaseFactory(CdaFactory):
    """
    `CdaDiseaseFactory` uses both the `diagnosis` and `researchsubject` tables to format the information
    about the disease diagnosis into the Disease element of the Phenopacket Schema.

    Note, `CdaDiseaseFactory` interprets the `age_at_diagnosis` as the age of onset.

    - 'primary_diagnosis'
    - 'primary_diagnosis_site'
    - 'primary_diagnosis_condition'
    - 'stage'
    - 'age_at_diagnosis'

    :param disease_term_mapper: an :class:`OpMapper` for finding the disease term in the row fields.
    """

    def __init__(self, disease_term_mapper: OpMapper):
        self._disease_term_mapper = disease_term_mapper
        self._stage_mapper = OpDiseaseStageMapper()
        self._uberon_mapper = OpUberonMapper()

        self._required_fields = tuple(set(itertools.chain(
            self._disease_term_mapper.get_fields(),
            self._stage_mapper.get_fields(),
            self._uberon_mapper.get_fields(),
            ('age_at_diagnosis',),
        )))
        # todo -- add in ICCDO Mapper


    def to_ga4gh(self, row: pd.Series) -> pp.Disease:
        """
        Convert a row of the table obtained by merging CDA `diagnosis` and `researchsubject` tables into a Disease
         message of the Phenopacket Schema.

        The row is expected to contain the following columns:
        - 'stage'
        - 'primary_diagnosis_condition'
        - 'primary_diagnosis_site'
        - 'primary_diagnosis'
        - 'age_at_diagnosis'

        :param row: a :class:`pd.Series` with a row from the merged CDA table.
        """
        if not isinstance(row, pd.Series):
            raise ValueError(f"Invalid argument. Expected pandas Series but got {type(row)}")

        if any(field not in row for field in self._required_fields):
            #missing = row.index.difference(self._required_fields) # this gets items in row not in _required_fields but we want the opposite
            missing = []
            print(row.index)
            for i in self._required_fields:
                print('i:', i)
                if i not in row.index:
                    print('not in row.index')
                    missing.append(i)

            raise ValueError(f'Required field(s) are missing: {missing}')
            
        # This is the component we build here.
        disease = pp.Disease()

        term = self._disease_term_mapper.get_ontology_term(row=row)
        if term is None:
            # `term` is a required field.
            raise ValueError(f'Could not parse `term` from the row {row}')
        disease.term.CopyFrom(term)

        # We will interpret age_at_diagnosis as age of onset
        
        # raise ValueError(f"days argument must be an int or a str but was {type(days)}")
        # ValueError: days argument must be an int or a str but was <class 'pandas._libs.missing.NAType'>
        iso8601_age_of_onset = self.days_to_iso(str(row['age_at_diagnosis']))
        if iso8601_age_of_onset is not None:
            disease.onset.age.iso8601duration = iso8601_age_of_onset

        # Deal with stage
        stage = self._stage_mapper.get_ontology_term(row=row)
        if stage is not None:
            disease.disease_stage.append(stage)

        primary_site = self._uberon_mapper.get_ontology_term(row)
        if primary_site is not None:
            disease.primary_site.CopyFrom(primary_site)

        # Deal with morphology - clinical_tnm_finding_list seems like the most
        # appropriate place to put this
        # TODO -- work out where this goes. I do not think the ICDO will give us TNM
        # clinical_tnm_finding_list = None #self._parse_morphology_into_ontology_term(row)

        return disease
