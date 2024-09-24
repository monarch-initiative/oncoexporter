import itertools

import pandas as pd
import phenopackets as pp
import re

from .mapper.op_mapper import OpMapper
from .mapper.op_disease_stage_mapper import OpDiseaseStageMapper
from .mapper.op_uberon_mapper import OpUberonMapper
from .cda_factory import CdaFactory
from ._gdc import GdcService


class CdaDiseaseFactory(CdaFactory):
    """
    `CdaDiseaseFactory` uses both the `diagnosis` and `researchsubject` tables to format the information
    about the disease diagnosis into the Disease element of the Phenopacket Schema.

    Note, `CdaDiseaseFactory` interprets the `age_at_diagnosis` as the age of onset.

    - 'primary_diagnosis'
    - 'primary_diagnosis_site'
    - 'primary_diagnosis_condition'
    - 'stage' (For GDC entries, we have to get the stage from the GDC API, as diagnosis.tumor_stage, which CDA gets from GDC, is empty)
    - 'age_at_diagnosis'

    :param disease_term_mapper: an :class:`OpMapper` for finding the disease term in the row fields.
    (called in mapper._configure.py)
    """

    def __init__(self, disease_term_mapper: OpMapper):
        self._gdc_service = GdcService()
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
            #print(row.index)
            for i in self._required_fields:
                print('i:', i)
                if i not in row.index:
                    print('not in row.index')
                    missing.append(i)

            raise ValueError(f'Required field(s) are missing: {missing}')
            
        # This is the component we build here.
        disease = pp.Disease()

        # map the disease term to NCIT
        term = self._disease_term_mapper.get_ontology_term(row=row)
        if term is None:
            # `term` is a required field.
            raise ValueError(f'Could not parse `term` from the row {row}')
        disease.term.CopyFrom(term)

        # We will interpret age_at_diagnosis as age of onset
        iso8601_age_of_onset = self.days_to_iso(str(row['age_at_diagnosis']))
        if iso8601_age_of_onset is not None:
            disease.onset.age.iso8601duration = iso8601_age_of_onset

        '''
        Deal with stage
         add stage if from GDC: diagnoses.tumor_stage is not filled in in GDC, so tumor_stage coming from CDA is empty
            can use diagnoses.ajcc_pathologic_stage instead (other alternatives are diagnoses.ajcc_clinical_stage, diagnoses.ann_arbor_pathologic_stage,
            diagnoses.ann_arbor_clinical_stage, but ajcc_pathologic_stage is the most prevalent in GDC) 
        
            Note: only selecting the stage from the 1st diagnosis out of potentially 4:
            diagnoses.0.diagnosis_id	diagnoses.1.diagnosis_id	diagnoses.2.diagnosis_id	diagnoses.3.diagnosis_id	
        '''
        #print("\n\nrow[subject_id]",row['subject_id'])
        #print("row:", list(row))
        #print("cda stage:", row["stage"]) # empty if coming from GDC
        stage_str = ''

        if row["stage"] == '': # probably should put in a check for data source here
            subj_id = re.sub("^[^.]+\.", "", row["subject_id"]) # remove initial data source label
            gdc_stage = self._gdc_service.fetch_stage(subj_id) # returns a string
            stage_str = gdc_stage
        else:
            stage_str = row["stage"]

        # map to ontology:
        stage = self._stage_mapper.get_ontology_term(stage_str=stage_str) # returns ontology_term = PPkt.OntologyClass()
        if stage is not None:
            disease.disease_stage.append(stage) # list, so use append instead of CopyFrom
        ###
        
        # map primary site to uberon        
        primary_site = self._uberon_mapper.get_ontology_term(row)
        if primary_site is not None:
            disease.primary_site.CopyFrom(primary_site)

        # Deal with morphology - clinical_tnm_finding_list seems like the most
        # appropriate place to put this
        # TODO -- work out where this goes. I do not think the ICDO will give us TNM
        # clinical_tnm_finding_list = None #self._parse_morphology_into_ontology_term(row)

        return disease
