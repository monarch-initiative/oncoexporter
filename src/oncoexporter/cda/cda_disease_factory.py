from typing import List, Optional

import phenopackets as PPkt
import pandas as pd
import os



from oncoexporter.model.op_disease import OpDisease

from .mapper.op_mapper import OpMapper
from .mapper.iso8601_mapper import Iso8601Mapper
from .mapper.op_diagnosis_mapper import OpDiagnosisMapper
from .mapper.op_disease_stage_mapper import OpDiseaseStageMapper
from .mapper.op_uberon_mapper import OpUberonMapper
from .cda_factory import CdaFactory


class CdaDiseaseFactory(CdaFactory):
    """The CDA diagnosis and researchsubject tables are merged to retrieve all needed information about the disease diagnosis.

    This class expects to get rows from the merged table (merged in CdaDiseaseFactory) and returns GA4GH Disease messages.

    The fields in 'diagnosis' are

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

    The fields in researchsubject are

        - researchsubject_id: identifier
        - researchsubject_identifier: a structured field that can have information from GDC
        - member_of_research_project: unclear
        - primary_diagnosis_condition: unclear difference to primary_diagnosis above
        - primary_diagnosis_site: anatomical site of tumor
        - subject_id: key to the subject table

    :param op_mapper: An object that is able to map free text to Ontology terns
    :type op_mapper: OpMapper
    """

    def __init__(self, op_mapper:OpMapper=None) -> None:
        """Constructor
        """
        super().__init__()
        if op_mapper is None:
            self._opMapper = OpDiagnosisMapper()
        else:
            self._opMapper = op_mapper
        self._stageMapper = OpDiseaseStageMapper()
        self._uberonMaper = OpUberonMapper()
        self._iso_age_mapper = Iso8601Mapper()
        # todo -- add in ICCDO Mapper


    def to_ga4gh(self, row):
        """Convert a row from the CDA subject table into an Individual message (GA4GH Phenopacket Schema)

        The row is a pd.core.series.Series and contains the columns. TODO check if up to date.
        ['diagnosis_id', 'diagnosis_identifier', 'primary_diagnosis',
        'age_at_diagnosis', 'morphology', 'stage', 'grade',
        'method_of_diagnosis', 'subject_id', 'researchsubject_id']
        :param row: a row from the CDA subject table
        """
        if not isinstance(row, pd.Series):
            raise ValueError(f"Invalid argument. Expected pandas series but got {type(row)}")
        disease_term = self._opMapper.get_ontology_term(row=row)
        ## Collect other pieces of data to add to the constructor on the next line

        # We will interpret age_at_diagnosis as age of onset
        iso8601_age_of_onset = self._iso_age_mapper.from_days(row['age_at_diagnosis']

        # Deal with stage
        stage_term = self._stageMapper.get_ontology_term(row=row)
        stage_term_list = [stage_term] # required to be list by API-TODO is this necessary


        primary_site = self._uberonMaper.get_ontology_term(row)

        # Deal with morphology - clinical_tnm_finding_list seems like the most
        # appropriate place to put this
        # TODO -- work out where this goes. I do not think the ICDO will give us TNM
        clinical_tnm_finding_list = None #self._parse_morphology_into_ontology_term(row)

        diseaseModel = OpDisease(disease_term=disease_term,
                                disease_stage_term_list=stage_term_list,
                                clinical_tnm_finding_list=clinical_tnm_finding_list,
                                iso8601duration_onset_age=iso8601_age_of_onset,
                                primary_site=primary_site)

        return diseaseModel.to_ga4gh()





