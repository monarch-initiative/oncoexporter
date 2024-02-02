import typing

from collections import defaultdict
from importlib.resources import open_text

import pandas as pd
import phenopackets as pp

from .op_mapper import OpMapper


def get_cda_key(primary_diagnosis, primary_diagnosis_condition, primary_diagnosis_site):
    """
    We use the combination of the three arguments to determine the NCIT diagnosis term as precisely as possible
    This function combines the three arguments to generate a key that is used as a hashkey
    for ncit_map in `OpDiagnosisMapper`.
    """
    key = f"{primary_diagnosis}-{primary_diagnosis_condition}-{primary_diagnosis_site}"
    return key.replace(" ", "_")


def prepare_ncit_map(ncit_map_df: pd.DataFrame) -> typing.Mapping[str, pp.OntologyClass]:
    ncit_map = {}
    for _, row in ncit_map_df.iterrows():
        primary_diagnosis = row["primary_diagnosis"]
        primary_diagnosis_condition = row["primary_diagnosis_condition"]
        primary_diagnosis_site = row["primary_diagnosis_site"]
        NCIT_id = str(row["NCIT_id"])  # enforce string because empty cell can be represented as float.NaN
        NCIT_label = row["NCIT_label"]
        if NCIT_id is None or not NCIT_id.startswith("NCIT"):
            continue

        key = get_cda_key(primary_diagnosis, primary_diagnosis_condition, primary_diagnosis_site)
        oterm = pp.OntologyClass()
        oterm.id = NCIT_id
        oterm.label = NCIT_label
        ncit_map[key] = oterm
    return ncit_map


def prepare_uberon(uberon_df: pd.DataFrame) -> typing.Mapping[str, pp.OntologyClass]:
    uberon_map = {}

    for _, row in uberon_df.iterrows():
        uberon_label = str(row["uberon_label"])
        uberon_id = row["uberon_id"]
        NCIT_id = row["NCIT_id"]
        NCIT_label = row["NCIT_label"]
        synonyms = str(row["synonyms"])
        oterm = pp.OntologyClass()
        oterm.id = NCIT_id
        oterm.label = NCIT_label
        uberon_map[uberon_label] = oterm
        fields = synonyms.split(";")
        for f in fields:
            f = f.strip()
            uberon_map[f] = oterm

    return uberon_map


class OpDiagnosisMapper(OpMapper):

    @staticmethod
    def default_mapper():
        # Use the mapping tables bundled in the package.
        module = 'oncoexporter.ncit_mapping_files'
        with open_text(module, 'cda_to_ncit_map.tsv') as fh:
            ncit_map_df = pd.read_csv(fh, sep='\t')
        ncit_map = prepare_ncit_map(ncit_map_df)

        with open_text(module, 'uberon_to_ncit_diagnosis.tsv') as fh:
            uberon_df = pd.read_csv(fh, sep='\t')
        uberon_map = prepare_uberon(uberon_df)

        return OpDiagnosisMapper(ncit_map, uberon_map)

    def __init__(self, ncit_map: typing.Mapping[str, pp.OntologyClass],
                 uberon_map: typing.Mapping[str, pp.OntologyClass]):
        """
        Our strategy is to map the three fields
        primary_diagnosis	primary_diagnosis_condition	primary_diagnosis_site	to a single string that we use
        as the key to a map whose values are the corresponding NCIT terms. If we cannot find an entry in this
        map, then we use the primary_diagnosis_site field (e.g., uterus) to get a more generic NCIT term,
        e.g., Uterine Neoplasm.

        NCIT:id	NCIT:label	Comment
        """
        super().__init__(('primary_diagnosis', 'primary_diagnosis_condition', 'primary_diagnosis_site'))

        self._ncit_map = ncit_map
        self._uberon_map = uberon_map
        self._warning_count_d = defaultdict(int)

    def get_ontology_term(self, row: pd.Series) -> typing.Optional[pp.OntologyClass]:
        primary_diagnosis = row["primary_diagnosis"]
        primary_diagnosis_condition = row["primary_diagnosis_condition"]
        primary_diagnosis_site = row["primary_diagnosis_site"]
        key = get_cda_key(primary_diagnosis, primary_diagnosis_condition, primary_diagnosis_site)
        if key in self._ncit_map:
            return self._ncit_map.get(key)
        error_key = f"{primary_diagnosis}---{primary_diagnosis_condition}---{primary_diagnosis_site}"
        self._warning_count_d[error_key] += 1
        if primary_diagnosis_site in self._uberon_map:
            return self._uberon_map.get(primary_diagnosis_site)
        print(f"[ERROR] Could not find NCIT term for {primary_diagnosis}-{primary_diagnosis_condition}-{primary_diagnosis_site}")
        # Return the most general NCIT neoplasm term
        oterm = pp.OntologyClass()
        oterm.id = "NCIT:C3262"
        oterm.label = "Neoplasm"
        return oterm

    def get_error_df(self):
        errors = []
        for k, v in self._warning_count_d.items():
            fields = k.split("---")
            if len(fields) != 3:
                print(f"Malformed warning {k}")
            d = {
                "primary_diagnosis": fields[0],
                "primary_diagnosis_condition": fields[1],
                "primary_diagnosis_site": fields[2],
                "count": str(v),
            }
            errors.append(d)

        return pd.DataFrame(errors)
