import phenopackets as PPkt
import pandas as pd

from .mapper.op_mapper import OpMapper
from .mapper.op_diagnosis_mapper import OpDiagnosisMapper
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
        """

        """
        super().__init__()
        if op_mapper is None:
            self._opMapper = OpDiagnosisMapper()
        else:
            self._opMapper = op_mapper

    def to_ga4gh(self, row):
        """Convert a row from the CDA subject table into an Individual message (GA4GH Phenopacket Schema)

        The row is a pd.core.series.Series and contains the columns. TODO check if up to date.
        ['diagnosis_id', 'diagnosis_identifier', 'primary_diagnosis',
        'age_at_diagnosis', 'morphology', 'stage', 'grade',
        'method_of_diagnosis', 'subject_id', 'researchsubject_id']
        :param row: a row from the CDA subject table
        """
        if not isinstance(row, pd.core.series.Series):
            raise ValueError(f"Invalid argument. Expected pandas series but got {type(row)}")

        disease = PPkt.Disease()

        disease.term.CopyFrom(self._parse_diagnosis_into_ontology_term(
            primary_diagnosis=row["primary_diagnosis"],
            primary_diagnosis_condition=row["primary_diagnosis_condition"],
            primary_diagnosis_site=row["primary_diagnosis_site"]
        ))
        return disease

    def _parse_diagnosis_into_ontology_term(self,
                                            primary_diagnosis: str,
                                            primary_diagnosis_condition: str,
                                            primary_diagnosis_site=str) -> PPkt.OntologyClass:

        # primary_diagnosis,primary_diagnosis_condition,primary_diagnosis_site,id,label
        # ,,Lung,NCIT:C3200,Lung Neoplasm
        # Adenocarcinoma,Lung Adenocarcinoma,Lung,NCIT:C3512,Lung Adenocarcinoma
        # Acantholytic squamous cell carcinoma,Lung Squamous Cell Carcinoma,Lung,NCIT:C3493,Lung Squamous Cell Carcinoma
        # "Adenocarcinoma, NOS",Lung Adenocarcinoma,Lung,NCIT:C3512,Lung Adenocarcinoma
        # Squamous Cell Carcinoma,Lung Squamous Cell Carcinoma,Lung,NCIT:C3493,Lung Squamous Cell Carcinoma
        # "Clear cell adenocarcinoma, NOS",Lung Adenocarcinoma,Lung,NCIT:C45516,Lung Adenocarcinoma
        # Squamous Cell Carcinoma,Lung Adenocarcinoma,Lung,NCIT:C9133,Lung Adenosquamous Carcinoma
        # Adenosquamous carcinoma,Lung Adenocarcinoma,Lung,NCIT:C9133,Lung Adenosquamous Carcinoma

        ontology_term = PPkt.OntologyClass()
        ontology_term.id ='NCIT:C3262'
        ontology_term.label = 'Neoplasm'
        if primary_diagnosis == "" and primary_diagnosis_condition == "" and primary_diagnosis_site == "Lung":
            ontology_term.id = 'NCIT:C3200'
            ontology_term.label = 'Lung Neoplasm'
        elif primary_diagnosis == "Adenocarcinoma" and primary_diagnosis_condition == "Lung Adenocarcinoma" and primary_diagnosis_site == "Lung":
            ontology_term.id = 'NCIT:C3512'
            ontology_term.label = 'Lung Adenocarcinoma'
        elif primary_diagnosis == "Acantholytic squamous cell carcinoma" and primary_diagnosis_condition == "Lung Squamous Cell Carcinoma" and primary_diagnosis_site == "Lung":
            ontology_term.id = 'NCIT:C3493'
            ontology_term.label = 'Lung Squamous Cell Carcinoma'
        elif primary_diagnosis == "Adenocarcinoma, NOS" and primary_diagnosis_condition == "Lung Adenocarcinoma" and primary_diagnosis_site == "Lung":
            ontology_term.id = 'NCIT:C3512'
            ontology_term.label = 'Lung Adenocarcinoma'
        elif primary_diagnosis == "Squamous Cell Carcinoma" and primary_diagnosis_condition == "Lung Squamous Cell Carcinoma" and primary_diagnosis_site == "Lung":
            ontology_term.id = 'NCIT:C3493'
            ontology_term.label = 'Lung Squamous Cell Carcinoma'
        elif primary_diagnosis == "Clear cell adenocarcinoma, NOS" and primary_diagnosis_condition == "Lung Adenocarcinoma" and primary_diagnosis_site == "Lung":
            ontology_term.id = 'NCIT:C45516'
            ontology_term.label = 'Lung Adenocarcinoma'
        elif primary_diagnosis == "Squamous Cell Carcinoma" and primary_diagnosis_condition == "Lung Adenocarcinoma" and primary_diagnosis_site == "Lung":
            ontology_term.id = 'NCIT:C9133'
            ontology_term.label = 'Lung Adenosquamous Carcinoma'
        elif primary_diagnosis == "Adenosquamous carcinoma" and primary_diagnosis_condition == "Lung Adenocarcinoma" and primary_diagnosis_site == "Lung":
            ontology_term.id = 'NCIT:C9133'
            ontology_term.label = 'Lung Adenosquamous Carcinoma'
        return ontology_term
