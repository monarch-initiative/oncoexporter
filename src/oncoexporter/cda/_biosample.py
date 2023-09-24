import typing

import pandas as pd
import phenopackets as pp

HOMO_SAPIENS = pp.OntologyClass(id='NCBITaxon:9606', label='Homo sapiens')
LUNG = pp.OntologyClass(id='UBERON:0002048', label='lung')

"""CDA	Phenopacket
	
anatomical_site	sampled_tissue
source_material_type	material_sample
specimen_type	
derived_from_specimen	derived_from_id
derived_from_subject	
days_to_collection + age_at_diagnosis (diag table)	time_of_collection
primary_disease_type	histological_diagnosis
"""

"""
source_material_type:		
Blood Derived Normal	NCIT:C17610	Blood Derived Sample
Normal Adjacent Tissue	NCIT:C164032	Tumor-Adjacent Normal Specimen
Primary solid Tumor	NCIT:C162622	Tumor Segment 
Primary Tumor	NCIT:C162622	Tumor Segment 
Solid Tissue Normal	NCIT:C164014	Solid Tissue Specimen
Tumor	NCIT:C18009	Tumor Tissue
"""

def make_cda_biosample(row: pd.Series) -> pp.Biosample:
    biosample = pp.Biosample()
    # anatomical_site -> sampled_tissue
    sampled_tissue = _map_anatomical_site(row['anatomical_site'])
    if sampled_tissue is not None:
        biosample.sampled_tissue = sampled_tissue

    biosample.taxonomy = HOMO_SAPIENS

    return biosample


def _map_anatomical_site(val: typing.Optional[str]) -> typing.Optional[pp.OntologyClass]:
    if val is None:
        return None
    if val.lower() == 'lung':
        return LUNG
    else:
        return None
