import typing

import pandas as pd
import phenopackets as pp

HOMO_SAPIENS = pp.OntologyClass(id='NCBITaxon:9606', label='Homo sapiens')
LUNG = pp.OntologyClass(id='UBERON:0002048', label='lung')
LUNG_ADENOCARCINOMA = pp.OntologyClass(id='NCIT:C3512', label='Lung Adenocarcinoma')
LUNG_SQUAMOUS_CELL_CARCINOMA = pp.OntologyClass(id='NCIT:C3493', label='Lung Squamous Cell Carcinoma')

"""CDA	Phenopacket
	
anatomical_site	sampled_tissue
source_material_type	material_sample
specimen_type	
derived_from_specimen	derived_from_id
derived_from_subject	
days_to_collection + age_at_diagnosis (diag table)	time_of_collection
primary_disease_type	histological_diagnosis
"""

def make_cda_biosample(row: pd.Series) -> pp.Biosample:
    biosample = pp.Biosample()
    # anatomical_site -> sampled_tissue
    sampled_tissue = _map_anatomical_site(row['anatomical_site'])
    if sampled_tissue is not None:
        biosample.sampled_tissue = sampled_tissue

    biosample.taxonomy.CopyFrom(HOMO_SAPIENS)

    # primary_disease_type -> histological_diagnosis
    histological_diagnosis = _map_primary_disease_type(row['primary_disease_type'])
    if histological_diagnosis is not None:
        biosample.histological_diagnosis.CopyFrom(histological_diagnosis)

    return biosample


def _map_anatomical_site(val: typing.Optional[str]) -> typing.Optional[pp.OntologyClass]:
    if val is None:
        return None
    if val.lower() == 'lung':
        return LUNG
    else:
        return None

def _map_primary_disease_type(val: typing.Optional[str]=None) -> typing.Optional[pp.OntologyClass]:
    if val is not None:
        val = val.lower()
        if val == 'lung adenocarcinoma':
            return LUNG_ADENOCARCINOMA
        elif val == 'lung squamous cell carcinoma':
            return LUNG_SQUAMOUS_CELL_CARCINOMA
        else:
            return None
    else:
        return None
    