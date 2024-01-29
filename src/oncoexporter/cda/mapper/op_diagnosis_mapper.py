import os

from .op_mapper import OpMapper
from typing import Optional
import pandas as pd
from collections import defaultdict
import phenopackets as PPkt

class OpDiagnosisMapper(OpMapper):

    def __init__(self):
        """
        Our strategy is to map the three fields
        primary_diagnosis	primary_diagnosis_condition	primary_diagnosis_site	to a single string that we use
        as the key to a map whose values are the corresponding NCIT terms. If we cannot find an entry in this
        map, then we use the primary_diagnosis_site field (e.g., uterus) to get a more generic NCIT term, e.g.,
        Uterine Neoplasm.

        NCIT:id	NCIT:label	Comment
        """
        super().__init__()
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        grandparent_dir = os.path.dirname(parent_dir)
        great_gp_dir = os.path.dirname(grandparent_dir)
        data_directory = "ncit_mapping_files"
        # This file lives at src/oncoexporter/ncit_mapping_files/cda_to_ncit_map.tsv
        cda_to_ncit_map = "cda_to_ncit_map.tsv"
        fname = os.path.join(great_gp_dir, data_directory, cda_to_ncit_map)
        if not os.path.isfile(fname):
            raise ValueError(f"Could not find necessary input file {fname} - expecting to find \"src/oncoexporter/ncit_mapping_files/cda_to_ncit_map.tsv\"")
        self._ncit_map = {}
        ncit_map_df = pd.read_csv(fname, sep="\t")
        for _, row in ncit_map_df.iterrows():
            primary_diagnosis = row["primary_diagnosis"]
            primary_diagnosis_condition  = row["primary_diagnosis_condition"]
            primary_diagnosis_site  = row["primary_diagnosis_site"]
            NCIT_id  = str(row["NCIT_id"]) # enforce string because empty cell can be represented as float.NaN
            NCIT_label  = row["NCIT_label"]
            if  NCIT_id is None or not NCIT_id.startswith("NCIT"):
                continue
            oterm = PPkt.OntologyClass()
            oterm.id=NCIT_id
            oterm.label = NCIT_label
            key = self._get_cda_key(primary_diagnosis, primary_diagnosis_condition, primary_diagnosis_site)
            self._ncit_map[key] = oterm
        self._uberon_map = {}
        uberon_to_ncit_map = "uberon_to_ncit_diagnosis.tsv"
        uberon_fname = os.path.join(great_gp_dir, data_directory, uberon_to_ncit_map)
        uberon_df = pd.read_csv(uberon_fname, sep="\t")
        for _, row in uberon_df.iterrows():
            uberon_label = str(row["uberon_label"])
            uberon_id = row["uberon_id"]
            NCIT_id = row["NCIT_id"]
            NCIT_label = row["NCIT_label"]
            synonyms = str(row["synonyms"])
            oterm = PPkt.OntologyClass()
            oterm.id = NCIT_id
            oterm.label = NCIT_label
            self._uberon_map[uberon_label] = oterm
            fields = synonyms.split(";")
            for f in fields:
                f = f.strip()
                self._uberon_map[f] = oterm
        self._warning_count_d = defaultdict(int)

    def _get_cda_key(self, primary_diagnosis, primary_diagnosis_condition, primary_diagnosis_site):
        """
        We use the combination of the three arguments to determine the NCIT diagnosis term as precisely as possible
        This function combines the three arguments to generate a key that is used as a hashkey for self._ncit_map
        """
        key = f"{primary_diagnosis}-{primary_diagnosis_condition}-{primary_diagnosis_site}"
        key = key.replace(" ", "_")
        return key

    def get_ontology_term(self, row:pd.Series) -> Optional[PPkt.OntologyClass]:
        primary_diagnosis = row["primary_diagnosis"]
        primary_diagnosis_condition = row["primary_diagnosis_condition"]
        primary_diagnosis_site = row["primary_diagnosis_site"]
        key = self._get_cda_key(primary_diagnosis, primary_diagnosis_condition, primary_diagnosis_site)
        if key in self._ncit_map:
            return self._ncit_map.get(key)
        error_key = f"{primary_diagnosis}---{primary_diagnosis_condition}---{primary_diagnosis_site}"
        self._warning_count_d[error_key] += 1
        if primary_diagnosis_site in self._uberon_map:
            return self._uberon_map.get(primary_diagnosis_site)
        print(f"[ERROR] Could not find NCIT term for {primary_diagnosis}-{primary_diagnosis_condition}-{primary_diagnosis_site}")
        ## Return the most general NCIT neoplasm term
        oterm = PPkt.OntologyClass()
        oterm.id = "NCIT:C3262"
        oterm.label = "Neoplasm"
        return oterm


    def get_error_df(self):
        errors = []
        for k, v in self._warning_count_d.items():
            fields = k.split("---")
            if len(fields) != 3:
                print(f"Malformed warning {k}")
            d = {"primary_diagnosis" : fields[0],
                "primary_diagnosis_condition": fields[1],
                "primary_diagnosis_site" :fields[2],
                "count": str(v)}
            errors.append(d)
        return pd.DataFrame(errors)