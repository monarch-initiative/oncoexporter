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

    TODO: The field list below may be inaccurate. Check!

    We need these fields from the `diagnosis` table:

        - diagnosis_id: identifier
        - diagnosis_identifier: a structured field that can have information from GDC
        - primary_diagnosis: the main cancer diagnosis of this individual
        - age_at_diagnosis: the number of days of life on day when the cancer diagnosis was made.
        - morphology: ICD-O codes representing the cancer diagnosis
        - stage: cancer stage
        - grade: cancer grade
        - method_of_diagnosis: free text with entries such as 'Biospy'
        - subject_id: key to the subject table
        - researchsubject_id: key to the researchsubject table

    The required fields from the `researchsubject` table include:

        - researchsubject_id: identifier
        - researchsubject_identifier: a structured field that can have information from GDC
        - member_of_research_project: unclear
        - primary_diagnosis_condition: unclear difference to primary_diagnosis above
        - primary_diagnosis_site: anatomical site of tumor
        - subject_id: key to the subject table

    :param disease_term_mapper: an :class:`OpMapper` for finding the disease term in the row fields.
    """

    def __init__(self, disease_term_mapper: OpMapper):
        self._disease_term_mapper = disease_term_mapper
        self._stage_mapper = OpDiseaseStageMapper()
        self._uberon_mapper = OpUberonMapper()

        self._required_fields = tuple(itertools.chain(
            self._disease_term_mapper.get_fields(),
            self._stage_mapper.get_fields(),
            self._uberon_mapper.get_fields()
        ))
        # todo -- add in ICCDO Mapper


    def to_ga4gh(self, row: pd.Series) -> pp.Disease:
        """
        Convert a row of the table obtained by merging CDA `diagnosis` and `researchsubject` tables into a Disease
         message of the Phenopacket Schema.

        The row is expected to contain the following columns:
        - 'subject_id',
        - 'researchsubject_id'
        - 'diagnosis_id',
        - 'diagnosis_identifier',
        - 'primary_diagnosis',
        - 'age_at_diagnosis',
        - 'morphology',
        - 'stage',
        - 'grade',
        - 'method_of_diagnosis',

        :param row: a :class:`pd.Series` with a row from the merged CDA table.
        """
        if not isinstance(row, pd.Series):
            raise ValueError(f"Invalid argument. Expected pandas Series but got {type(row)}")

        if any(field not in row for field in self._required_fields):
            missing = row.index.difference(self._required_fields)
            raise ValueError(f'Required field(s) are missing: {missing.values}')

        # This is the component we build here.
        disease = pp.Disease()

        term = self._disease_term_mapper.get_ontology_term(row=row)
        if term is None:
            # `term` is a required field.
            raise ValueError(f'Could not parse `term` from the row {row}')
        disease.term.CopyFrom(term)

        # We will interpret age_at_diagnosis as age of onset
        iso8601_age_of_onset = self.days_to_iso(row['age_at_diagnosis'])
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
