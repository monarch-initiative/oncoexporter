from typing import List, Optional

import phenopackets as PPkt
import pandas as pd
import os

import requests
import csv
import warnings

from oncoexporter.model.op_disease import OpDisease

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
                 icdo_to_ncit_map_url='https://evs.nci.nih.gov/ftp1/NCI_Thesaurus/Mappings/ICD-O-3_Mappings/ICD-O-3.1-NCIt_Morphology_Mapping.txt',
                 key_column='ICD-O Code'
                 ) -> None:
        """

        """
        super().__init__()
        if op_mapper is None:
            self._opMapper = OpDiagnosisMapper()
        else:
            self._opMapper = op_mapper
       # self._icdo_to_ncit = self.load_icdo_to_ncit_tsv()
            #self._download_and_icdo_to_ncit_tsv(icdo_to_ncit_map_url, key_column=key_column)


    def load_icdo_to_ncit_tsv(self, overwrite:bool=False, local_dir:str=None):
        """
        Download if necessary the NCIT ICD-O mapping file and store it in the package ncit_files folder
        :param overwrite: whether to overwrite an existing file (otherwise we skip downloading)
        :type overwrite: bool
        :param local_dir: Path to a directory to write downloaded file
        """
        key_column = 'ICD-O Code'
        # When we get here, either we have just downloaded the ICD-O file or it was already available locally.
        # stream = pkg_resources.resource_stream("", icd_path)
        icd_path = self._icdo_to_ncit_path
        df = pd.read_csv(icd_path, encoding='latin-1')
        result_dict = {}
        if key_column not in df.columns:
            raise ValueError(f"Couldn't find key_column {key_column} in fieldnames "
                          f"{df.columns} of file at {icd_path}")
        for idx, row in df.iterrows():
            key = row[key_column]
            if key:
                result_dict[key] = row
        print(f"Loaded ICD-O dictionary with {len(result_dict)} items")
        return result_dict


    def _download_and_icdo_to_ncit_tsv(self, url: str, key_column: str) -> dict:
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

    def temp_get_load_icdo_to_ncit_tsv(self):
        return self._icdo_to_ncit

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

        disease_term = self._parse_diagnosis_into_ontology_term(
            primary_diagnosis=row["primary_diagnosis"],
            primary_diagnosis_condition=row["primary_diagnosis_condition"],
            primary_diagnosis_site=row["primary_diagnosis_site"]
        )
        ## Collect other pieces of data to add to the constructor on the next line

        # Deal with stage
        stage_term_list = self._parse_stage_into_ontology_terms(row['stage'])

        # Deal with morphology - clinical_tnm_finding_list seems like the most
        # appropriate place to put this
        clinical_tnm_finding_list = self._parse_morphology_into_ontology_term(row)

        diseaseModel = OpDisease(disease_term=disease_term,
                                 disease_stage_term_list=stage_term_list,
                                 clinical_tnm_finding_list=clinical_tnm_finding_list)
        return diseaseModel.to_ga4gh()

    def _parse_morphology_into_ontology_term(self, row) -> Optional[List[PPkt.OntologyClass]]:
        if row['morphology'] in self._icdo_to_ncit:
            ncit_record = self._icdo_to_ncit.get(row['morphology'])
            ontology_term = PPkt.OntologyClass()
            if 'NCIt Code (if present)' not in ncit_record:
                warnings.warn(f"Couldn't find 'NCIt Code (if present)' entry in record for ICD-O code {row['morphology']}")
                return None
            elif ncit_record['NCIt Code (if present)'] == '':
                warnings.warn(f"Found empty 'NCIt Code (if present)' entry in record for ICD-O code {row['morphology']}")
                return None
            else:
                ontology_term.id = "NCIT:" + ncit_record['NCIt Code (if present)']
            if 'NCIt PT string (Preferred term)' in ncit_record: # else maybe don't raise a fuss
                ontology_term.label = ncit_record['NCIt PT string (Preferred term)']
            return [ontology_term]
        else:
            return None

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

    def _parse_stage_into_ontology_terms(self, stage_str: str) -> List[PPkt.OntologyClass]:
        ontology_term = PPkt.OntologyClass()
        ontology_term.id ='NCIT:C92207'  # Stage unknown
        ontology_term.label = 'Stage Unknown'

        if stage_str in ['Stage I', 'Stage 1', 'stage 1', 'stage I']:
            ontology_term.id = 'NCIT:C27966'
            ontology_term.label = 'Stage I'
        elif stage_str in ['IA', 'Stage IA', 'stage IA']:
            ontology_term.id = 'NCIT:C27975'
            ontology_term.label = 'Stage IA'
        elif stage_str in ['IB', 'Stage IB', 'stage IB']:
            ontology_term.id = 'NCIT:C27976'
            ontology_term.label = 'Stage IB'
        elif stage_str in ['Stage II', 'Stage 2', 'stage 2', 'stage II']:
            ontology_term.id = 'NCIT:C28054'
            ontology_term.label = 'Stage II'
        elif stage_str in ['IIA', 'Stage IIA', 'stage IIA']:
            ontology_term.id = 'NCIT:C27967'
            ontology_term.label = 'Stage IIA'
        elif stage_str in ['IIB', 'Stage IIB', 'stage IIB']:
            ontology_term.id = 'NCIT:C27968'
            ontology_term.label = 'Stage IIB'
        elif stage_str in ['Stage 3', 'stage 3']:
            ontology_term.id = 'NCIT:C27970'
            ontology_term.label = 'Stage III'
        elif stage_str in ['IIIA', 'Stage IIIA', 'Stage 3A', 'stage 3A']:
            ontology_term.id = 'NCIT:C27977'
            ontology_term.label = 'Stage IIIA'
        elif stage_str in ['IIIB', 'Stage IIIB', 'Stage 3B', 'stage 3B']:
            ontology_term.id = 'NCIT:C27978'
            ontology_term.label = 'Stage IIIB'
        elif stage_str in ['IV', 'Stage 4']:
            ontology_term.id = 'NCIT:C27971'
            ontology_term.label = 'Stage IV'
        return [ontology_term]
