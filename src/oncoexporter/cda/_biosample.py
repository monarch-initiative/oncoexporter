import typing

import pandas as pd
import phenopackets as pp

HOMO_SAPIENS = pp.OntologyClass(id='NCBITaxon:9606', label='Homo sapiens')
LUNG = pp.OntologyClass(id='UBERON:0002048', label='lung')

LUNG_ADENOCARCINOMA = pp.OntologyClass(id='NCIT:C3512', label='Lung Adenocarcinoma')
LUNG_SQUAMOUS_CELL_CARCINOMA = pp.OntologyClass(id='NCIT:C3493', label='Lung Squamous Cell Carcinoma')

BLOOD_DERIVED_NORMAL = pp.OntologyClass(id='NCIT:C17610', label='Blood Derived Sample')
NORMAL_ADJACENT_TISSUE = pp.OntologyClass(id='NCIT:C164032', label='Tumor-Adjacent Normal Specimen')
PRIMARY_SOLID_TUMOR = pp.OntologyClass(id='NCIT:C162622', label='Tumor Segment')
PRIMARY_TUMOR = pp.OntologyClass(id='NCIT:C162622', label='Tumor Segment')
SOLID_TISSUE_NORMAL = pp.OntologyClass(id='NCIT:C164014', label='Solid Tissue Specimen')
TUMOR = pp.OntologyClass(id='NCIT:C18009', label='Tumor Tissue')

ANALYTE = pp.OntologyClass(id='NCIT:C128639', label='Analyte')
ALIQUOT = pp.OntologyClass(id='NCIT:C25414', label='Aliquot')
PORTION = pp.OntologyClass(id='NCIT:C103166', label='Portion or Totality')
SAMPLE = pp.OntologyClass(id='NCIT:C70699', label='Sample')
SLIDE = pp.OntologyClass(id='NCIT:C165218', label='Diagnostic Slide')

"""CDA	Phenopacket
	
anatomical_site	sampled_tissue
source_material_type	material_sample
specimen_type	sample_type
derived_from_specimen	derived_from_id
derived_from_subject	individual_id
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

"""
Specimen_type:		
analyte	NCIT:C128639	Analyte
aliquot	NCIT:C25414	Aliquot
Portion	NCIT:C103166	Portion or Totality
sample	NCIT:C70699	Biospecimen
slide	NCIT:C165218	Diagnostic Slide
"""

def make_cda_biosample(row: pd.Series) -> pp.Biosample:
    biosample = pp.Biosample()

    biosample.id = row['specimen_id']

    # anatomical_site -> sampled_tissue
    sampled_tissue = _map_anatomical_site(row['anatomical_site'])
    if sampled_tissue is not None:
        biosample.sampled_tissue = sampled_tissue

    biosample.taxonomy.CopyFrom(HOMO_SAPIENS)

    # primary_disease_type -> histological_diagnosis
    histological_diagnosis = _map_primary_disease_type(row['primary_disease_type'])
    if histological_diagnosis is not None:
        biosample.histological_diagnosis.CopyFrom(histological_diagnosis)

    # derived_from_specimen -> derived_from_id
    if row['derived_from_specimen'] is not None:
        biosample.derived_from_id = row['derived_from_specimen']

    material_sample = _map_source_material_type(row['source_material_type'])
    if material_sample is not None:
        biosample.material_sample.CopyFrom(material_sample)

    sample_type = _map_specimen_type(row['specimen_type'])
    if sample_type is not None:
        biosample.sample_type.CopyFrom(sample_type)

    if row['derived_from_subject'] is not None:
        biosample.individual_id = row['derived_from_subject']

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
    
def _map_specimen_type(val: typing.Optional[str]=None) -> typing.Optional[pp.OntologyClass]:
    if val is not None:
        val = val.lower()
        if val == "analyte":
            return ANALYTE
        elif val == "aliquot":
            return ALIQUOT
        elif val == "portion":
            return PORTION
        elif val == "sample":
            return SAMPLE
        elif val == "slide":
            return SLIDE
        else:
            return None
    else:
        return None
    

def _map_source_material_type(val: typing.Optional[str]=None) -> typing.Optional[pp.OntologyClass]:
    if val is not None:
        val = val.lower()
        if val == "blood derived normal":
            return BLOOD_DERIVED_NORMAL
        elif val == "normal adjacent tissue":
            return NORMAL_ADJACENT_TISSUE
        elif val == "primary solid tumor":
            return PRIMARY_SOLID_TUMOR
        elif val == "primary tumor":
            return PRIMARY_TUMOR
        elif val == "solid tissue normal":
            return SOLID_TISSUE_NORMAL
        elif val == "tumor":
            return TUMOR
        else:
            return None
    else:
        return None
