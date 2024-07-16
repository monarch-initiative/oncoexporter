import typing
import warnings
from collections import defaultdict
from importlib.resources import open_text # deprecated
from importlib.resources import files

import pandas as pd
import phenopackets as pp

from .op_mapper import OpMapper


def get_cda_key(primary_diagnosis: str,
                primary_diagnosis_condition: str,
                primary_diagnosis_site: str,
                ):
    """
    We use the combination of the three arguments to determine the NCIT diagnosis term as precisely as possible
    This function combines the three arguments to generate a key that is used as a hashkey
    for ncit_map in `OpDiagnosisMapper`.
    """
    key = f"{primary_diagnosis.lower()}-{primary_diagnosis_condition.lower()}-{primary_diagnosis_site.lower()}"
    return key.replace(" ", "_")


def prepare_ncit_map(ncit_map_df: pd.DataFrame) -> typing.Mapping[str, pp.OntologyClass]:
    ncit_map = {}
    for _, row in ncit_map_df.iterrows():
        primary_diagnosis = row["primary_diagnosis"]
        primary_diagnosis_condition = row["primary_diagnosis_condition"]
        primary_diagnosis_site = row["primary_diagnosis_site"]
        NCIT_id = row["ncit_id"]
        NCIT_label = row["ncit_label"]
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
        uberon_label = str(row["uberon_label"]).lower()
        uberon_id = row["uberon_id"]

        oterm = pp.OntologyClass()
        oterm.id = row["NCIT_id"]
        oterm.label = row["NCIT_label"]

        uberon_map[uberon_label] = oterm

        for field in row["synonyms"].split(";"):
            field = field.strip().lower()
            if len(field) != 0:
                uberon_map[field] = oterm

    return uberon_map


# We treat the values as `str`s.
CONVERTERS = {
    'primary_diagnosis': str,
    'primary_diagnosis_condition': str,
    'primary_diagnosis_site': str,
    'ncit_id': str,
    'ncit_label': str,
}


class OpDiagnosisMapper(OpMapper):

    @staticmethod
    def multitissue_mapper():
        module_with_tissue_mapping_tables = 'oncoexporter.ncit_mapping_files.cda_to_ncit_tissue_wise_mappings'
        tissue_tables = (
            'cda_to_ncit_map_bone.csv',
            'cda_to_ncit_map_brain.csv',
            'cda_to_ncit_map_breast.csv',
            'cda_to_ncit_map_cervix.csv',
            'cda_to_ncit_map_colon.csv',
            'cda_to_ncit_map_heart.csv',
            'cda_to_ncit_map_kidney.csv',
            'cda_to_ncit_map_liver.csv',
            'cda_to_ncit_map_lung.csv',
            'cda_to_ncit_map_pancreas.csv',
            'cda_to_ncit_map_skin.csv',
            'cda_to_ncit_map_thyroid.csv',
        )
        frames = []
        for tissue in tissue_tables:
            #eml = files('email.tests.data').joinpath('message.eml').read_text()
            with open_text(module_with_tissue_mapping_tables, tissue) as fh:
                df = pd.read_csv(
                    fh,
                    converters=CONVERTERS,
                )
                frames.append(df)
        ncit_map_df = pd.concat(frames)
        ncit_map = prepare_ncit_map(ncit_map_df)

        module_with_uberon_table = 'oncoexporter.ncit_mapping_files'
        uberon_map = OpDiagnosisMapper._read_uberon_mappings(
            module_with_uberon_table,
            'uberon_to_ncit_diagnosis.tsv',
        )

        return OpDiagnosisMapper(ncit_map, uberon_map)

    @staticmethod
    def default_mapper():
        warnings.warn(
            'Use `multitissue_mapper()` instead',
            DeprecationWarning, stacklevel=2,
        )
        # Use the mapping tables bundled in the package.
        module = 'oncoexporter.ncit_mapping_files'
        # TODO: decide which file to use
        with open_text(module, 'cda_to_ncit_map_old.tsv') as fh:
            ncit_map_df = pd.read_csv(
                fh, sep='\t',
                converters=CONVERTERS,
            )
        ncit_map = prepare_ncit_map(ncit_map_df)

        uberon_map = OpDiagnosisMapper._read_uberon_mappings(module, 'uberon_to_ncit_diagnosis.tsv')

        return OpDiagnosisMapper(ncit_map, uberon_map)

    @staticmethod
    def _read_uberon_mappings(module: str, fname: str):
        with open_text(module, fname) as fh:
            uberon_df = pd.read_csv(fh, sep='\t')
        return prepare_uberon(uberon_df)

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
        self._compound_key_warning_count = defaultdict(int)
        self._primary_diagnosis_site_warning_count = defaultdict(int)

    def get_ontology_term(self, row: pd.Series) -> typing.Optional[pp.OntologyClass]:
        primary_diagnosis = replace_with_empty_str_if_none(row["primary_diagnosis"])
        primary_diagnosis_condition = replace_with_empty_str_if_none(row["primary_diagnosis_condition"])
        primary_diagnosis_site = replace_with_empty_str_if_none(row["primary_diagnosis_site"])
        print(primary_diagnosis, primary_diagnosis_condition, primary_diagnosis_site)
        
        # First, search using the composite key.
        key = get_cda_key(primary_diagnosis, primary_diagnosis_condition, primary_diagnosis_site)
        if key in self._ncit_map:
            return self._ncit_map.get(key)
        else:
            error_key = f"{primary_diagnosis}---{primary_diagnosis_condition}---{primary_diagnosis_site}"
            self._compound_key_warning_count[error_key] += 1

        # Next, lookup by the diagnosis site to provide at least a general neoplasm type.
        pds_lower = primary_diagnosis_site.lower()
        if pds_lower in self._uberon_map:
            return self._uberon_map.get(pds_lower)
        else:
            self._primary_diagnosis_site_warning_count[primary_diagnosis_site] += 1

        # Otherwise fall back to the most general NCIT neoplasm term.
        oterm = pp.OntologyClass()
        oterm.id = "NCIT:C3262"
        oterm.label = "Neoplasm"
        return oterm

    def get_error_df(self):
        errors = []
        for compound_key, count in self._compound_key_warning_count.items():
            fields = compound_key.split("---")
            if len(fields) != 3:
                print(f"Malformed warning {compound_key}")
            error = {
                "primary_diagnosis": fields[0],
                "primary_diagnosis_condition": fields[1],
                "primary_diagnosis_site": fields[2],
                "count": count,
            }
            errors.append(error)

        for primary_diagnosis_site, count in self._primary_diagnosis_site_warning_count.items():
            error = {
                'primary_diagnosis_site': primary_diagnosis_site,
                'count': count,
            }
            errors.append(error)

        return pd.DataFrame(errors)


def replace_with_empty_str_if_none(val: typing.Optional[str]) -> str:
    return val if val is not None else ''
