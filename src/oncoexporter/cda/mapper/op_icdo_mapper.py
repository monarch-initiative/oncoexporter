import csv
import requests
import typing
import warnings

import pandas as pd
import phenopackets as pp

from .op_mapper import OpMapper

icdo_to_ncit_map_url='https://evs.nci.nih.gov/ftp1/NCI_Thesaurus/Mappings/ICD-O-3_Mappings/ICD-O-3.1-NCIt_Morphology_Mapping.txt',
key_column='ICD-O Code'


class OpICDOMapper(OpMapper):

    def __init__(self):
        """
        This is a simple map from the 'stage' field of the diagnosis row
        """
        super().__init__(())
        self._icdo_to_ncit = {}

    def get_ontology_term(self, row: pd.Series) -> typing.Optional[pp.OntologyClass]:
        # TODO: implement!
        raise NotImplementedError


    def load_icdo_to_ncit_tsv(self, overwrite:bool=False, local_dir:str=None):
        """
        Download if necessary the NCIT ICD-O mapping file and store it in the package ncit_mapping_files folder
        :param overwrite: whether to overwrite an existing file (otherwise we skip downloading)
        :type overwrite: bool
        :param local_dir: Path to a directory to write downloaded file

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
        """
        pass

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


    def _parse_morphology_into_ontology_term(self, row) -> typing.Optional[typing.List[pp.OntologyClass]]:
        if row['morphology'] in self._icdo_to_ncit:
            ncit_record = self._icdo_to_ncit.get(row['morphology'])
            ontology_term = pp.OntologyClass()
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