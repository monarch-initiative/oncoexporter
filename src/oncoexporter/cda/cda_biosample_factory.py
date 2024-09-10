import typing

import phenopackets as PPKt
import pandas as pd

from .cda_factory import CdaFactory

HOMO_SAPIENS = PPKt.OntologyClass(id='NCBITaxon:9606', label='Homo sapiens')
LUNG = PPKt.OntologyClass(id='UBERON:0002048', label='lung')

LUNG_ADENOCARCINOMA = PPKt.OntologyClass(id='NCIT:C3512', label='Lung Adenocarcinoma')
LUNG_SQUAMOUS_CELL_CARCINOMA = PPKt.OntologyClass(id='NCIT:C3493', label='Lung Squamous Cell Carcinoma')

BLOOD_DERIVED_NORMAL = PPKt.OntologyClass(id='NCIT:C17610', label='Blood Derived Sample')
NORMAL_ADJACENT_TISSUE = PPKt.OntologyClass(id='NCIT:C164032', label='Tumor-Adjacent Normal Specimen')
PRIMARY_SOLID_TUMOR = PPKt.OntologyClass(id='NCIT:C162622', label='Tumor Segment')
PRIMARY_TUMOR = PPKt.OntologyClass(id='NCIT:C162622', label='Tumor Segment')
SOLID_TISSUE_NORMAL = PPKt.OntologyClass(id='NCIT:C164014', label='Solid Tissue Specimen')
TUMOR = PPKt.OntologyClass(id='NCIT:C18009', label='Tumor Tissue')

ANALYTE = PPKt.OntologyClass(id='NCIT:C128639', label='Analyte')
ALIQUOT = PPKt.OntologyClass(id='NCIT:C25414', label='Aliquot')
PORTION = PPKt.OntologyClass(id='NCIT:C103166', label='Portion or Totality')
SAMPLE = PPKt.OntologyClass(id='NCIT:C70699', label='Sample')
SLIDE = PPKt.OntologyClass(id='NCIT:C165218', label='Diagnostic Slide')


class CdaBiosampleFactory(CdaFactory):
    """
    Class for creating a `Biosample` element from a row of the `specimen` CDA table.

    The class returns a GA4GH Biosample object that corresponds to a row of the speciment table.
    The CDA specimen table has the following fields.

        - specimen_id: identifier
        - specimen_identifier: structured field with additional information
        - specimen_associated_project: e.g., CGCI-HTMCP-CC
        - days_to_collection: age in days at time specimen was collected
        - primary_disease_type: to be clarified
        - anatomical_site: body location at which specimen was collected
        - source_material_type: todo
        - specimen_type: todo
        - derived_from_specimen: todo
        - derived_from_subject: todo
        - subject_id: todo
        - researchsubject_id: todo
    """

    def to_ga4gh(self, row) -> PPKt.Biosample:
        biosample = PPKt.Biosample()

        biosample.id = row['specimen_id']

        derived_from_subj = row['derived_from_subject']
        if derived_from_subj is not None:
            biosample.individual_id = derived_from_subj

        # TODO: Biosample time_of_collection: Age at time sample was collected
        #  -> need subject age + days to collection 
        #     perform this in cda_table_importer.py under "Retrieve GA4GH Biospecimen messages"
        days_to_collection = row['days_to_collection'] # number of days from index date to sample collection date
        if days_to_collection is not None:
            pass
            # need PPKt.iso8601duration where PPKt.OpIndividual.id = biosample.individual_id
            # days_to_coll_td = pd.Timedelta(days=days_to_collection)
            # time_of_coll = PPkt.iso8601duration + days_to_coll_td
            # biosample.time_of_collection = time_of_coll.isoformat()

        # derived_from_specimen -> derived_from_id 
        '''
        Under mapping specimen it says (for GDC): "'specimen_type' is "'sample' or 'portion' or 'slide' 
         or 'analyte' or 'aliquot'" and 
         'derived_from_specimen' is "'initial specimen' if specimen_type is 'sample'; 
         otherwise Specimen.id for parent Specimen record".

         Note: may want to add a check that specimen_type from CDA is 'sample' if derived_from is 'initial specimen'
        '''
        derived_from = row['derived_from_specimen']    
        if derived_from is not None:  
            if derived_from != 'initial specimen':  
                biosample.derived_from_id = derived_from

        # anatomical_site -> sampled_tissue
        sampled_tissue = _map_anatomical_site(row['anatomical_site'])
        if sampled_tissue is not None:
            biosample.sampled_tissue.CopyFrom(sampled_tissue)

        sample_type = _map_specimen_type(row['specimen_type'])
        if sample_type is not None:
            biosample.sample_type.CopyFrom(sample_type)

        biosample.taxonomy.CopyFrom(HOMO_SAPIENS)

        # primary_disease_type -> histological_diagnosis
        histological_diagnosis = _map_primary_disease_type(row['primary_disease_type'])
        if histological_diagnosis is not None:
            biosample.histological_diagnosis.CopyFrom(histological_diagnosis)

        material_sample = _map_source_material_type(row['source_material_type'])
        if material_sample is not None:
            biosample.material_sample.CopyFrom(material_sample)

        return biosample


def _map_anatomical_site(val: typing.Optional[str]) -> typing.Optional[PPKt.OntologyClass]:
    # not clear if we need a mapping from NCIt -> UBERON ?
    if val is None:
        return None
    if val.lower() == 'lung':
        return LUNG
    else:
        return None


def _map_primary_disease_type(val: typing.Optional[str]) -> typing.Optional[PPKt.OntologyClass]:
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

def _map_specimen_type(val: typing.Optional[str]) -> typing.Optional[PPKt.OntologyClass]:
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


def _map_source_material_type(val: typing.Optional[str]) -> typing.Optional[PPKt.OntologyClass]:
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
