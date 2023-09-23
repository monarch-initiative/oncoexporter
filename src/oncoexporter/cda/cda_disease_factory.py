import phenopackets as PPkt
import pandas as pd

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
