import csv
import os
import platform
from importlib.resources import files

import requests


class CdaDownloader:

    def __init__(self):
        self.get_ncit_neoplasm_core()

    def download_if_needed(self, overwrite_downloads: bool):
        local_dir = self.get_local_share_directory()
        self._icdo_to_ncit_path = None
        self.load_icdo_to_ncit_tsv(overwrite=overwrite_downloads, local_dir=local_dir)

    def get_icdo_to_ncit_path(self):
        return self._icdo_to_ncit_path

    def load_icdo_to_ncit_tsv(self, overwrite: bool, local_dir: str):
        """
        Download if necessary the NCIT ICD-O mapping file and store it in the package ncit_mapping_files folder
        :param overwrite: whether to overwrite an existing file (otherwise we skip downloading)
        :type overwrite: bool
        :param local_dir: Path to a directory to write downloaded file
        """
        icdo_to_ncit_map_url = 'https://evs.nci.nih.gov/ftp1/NCI_Thesaurus/Mappings/ICD-O-3_Mappings/ICD-O-3.1-NCIt_Morphology_Mapping.txt'
        local_dir = self.get_local_share_directory()
        icd_path = os.path.join(local_dir, 'ICD-O-3.1-NCIt_Morphology_Mapping.txt')
        if not os.path.isfile(icd_path):
            print(f"[INFO] Downloading {icdo_to_ncit_map_url}")
            response = requests.get(icdo_to_ncit_map_url)
            response.raise_for_status()  # This will raise an error if the download failed
            tsv_data = csv.DictReader(response.text.splitlines(), delimiter='\t')
            with open(icd_path, 'w', newline='\n') as f:
                writer = csv.DictWriter(f, fieldnames=tsv_data.fieldnames)
                writer.writeheader()
                for row in tsv_data:
                    writer.writerow(row)
            print(f"[INFO] Downloaded {icdo_to_ncit_map_url}")
        self._icdo_to_ncit_path = icd_path

    def get_ncit_neoplasm_core(self):
        # Reads contents with UTF-8 encoding and returns str.
        neo_core = files('oncoexporter.ncit_mapping_files').joinpath('Neoplasm_Core.csv').read_text()
        print("NEO CORE", neo_core)

    def get_local_share_directory(self, local_dir=None):
        my_platform = platform.platform()
        my_system = platform.system()
        if local_dir is None:
            local_dir = os.path.join(os.path.expanduser('~'), ".oncoexporter")
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
            print(f"[INFO] Created new directory for oncoexporter at {local_dir}")
        return local_dir
