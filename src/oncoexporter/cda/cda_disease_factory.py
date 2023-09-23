import phenopackets as PPkt
import pandas as pd

from ..model.op_Individual import OpIndividual
from .op_mapper import OpMapper
from .cda_factory import CdaFactory

class CdaDiseaseFactory(CdaFactory):
    """
        Create GA4GH Disease messages from CDA (Cancer Data Aggregator). The relevant table in the
        CDA is diagnosis - 'diagnosis_id', 'diagnosis_identifier', 'primary_diagnosis',
       'age_at_diagnosis', 'morphology', 'stage', 'grade',
       'method_of_diagnosis', 'subject_id', 'researchsubject_id'.
        """

    def __init__(self, op_mapper=None) -> None:
        """
        :param OpMapper: An object that is able to map free text to Ontology terns
        """
        super().__init__()
        if op_mapper is None:
            self._opMapper = OpMapper()
        else:
            self._opMapper = op_mapper

    def from_cancer_data_aggregator(self, row):
        """
        convert a row from the CDA subject table into an Individual message (GA4GH Phenopacket Schema)
        The row is a pd.core.series.Series and contains the columns
        ['diagnosis_id', 'diagnosis_identifier', 'primary_diagnosis',
       'age_at_diagnosis', 'morphology', 'stage', 'grade',
       'method_of_diagnosis', 'subject_id', 'researchsubject_id']
       :param row: a row from the CDA subject table
        """
        if not isinstance(row, pd.core.series.Series):
            raise ValueError(f"Invalid argument. Expected pandas series but got {type(row)}")
        column_names = ['diagnosis_id', 'diagnosis_identifier', 'primary_diagnosis',
       'age_at_diagnosis', 'morphology', 'stage', 'grade',
       'method_of_diagnosis', 'subject_id', 'researchsubject_id_di',
       'researchsubject_id_rs', 'researchsubject_identifier',
       'member_of_research_project', 'primary_diagnosis_condition',
       'primary_diagnosis_site']
        diagnosis_id, diagnosis_identifier, primary_diagnosis, age_at_diagnosis, morphology, stage, grade, \
           method_of_diagnosis, subject_id, researchsubject_id_di, \
        researchsubject_id_rs, researchsubject_identifier, member_of_research_project, primary_diagnosis_condition, primary_diagnosis_site \
            = self.get_items_from_row(row, column_names)

        disease = PPkt.Disease()
        disease.term.id = 'fake'
        disease.term.label = 'fake'
        return disease
