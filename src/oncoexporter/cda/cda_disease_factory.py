import phenopackets as PPkt
import pandas as pd
import requests
import csv
import warnings

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

    def __init__(self, op_mapper:OpMapper=None,
                 icdo_to_ncit_map_url='https://evs.nci.nih.gov/ftp1/NCI_Thesaurus/Mappings/ICD-O-3_Mappings/ICD-O-3.1-NCIt_Morphology_Mapping.txt'
                 ) -> None:
        """

        """
        super().__init__()
        if op_mapper is None:
            self._opMapper = OpDiagnosisMapper()
        else:
            self._opMapper = op_mapper
        self._icdo_to_ncit = self._download_and_icdo_to_ncit_tsv(icdo_to_ncit_map_url)

    def _download_and_icdo_to_ncit_tsv(self, url: str, key_column: str = 'ICD-O Code') -> dict:
        """
        Helper function to download a TSV file, parse it, and create a dict of dicts.
        """
        response = requests.get(url)
        response.raise_for_status()  # This will raise an error if the download failed

        tsv_data = csv.DictReader(response.text.splitlines(), delimiter='\t')

        result_dict = {}
        if key_column not in tsv_data.fieldnames:
            warnings.warn(f"Couldn't find key_column {key_column} in fieldnames "
                          f"{tsv_data.fieldnames} of file downloaded from {url}")
        for row in tsv_data:
            key = row.pop(key_column, None)
            if key:
                result_dict[key] = row

        return result_dict

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

    def _get_icdo_to_ncit(self, row):
        if row['morphology'] in self._icdo_to_ncit:
            return self._icdo_to_ncit[row['morphology']]

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
