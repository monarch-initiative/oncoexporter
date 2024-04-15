from typing import Optional

from .op_mapper import OpMapper
import pandas as pd
import phenopackets as PPkt


class OpUberonMapper(OpMapper):
    """
    A simple mapper for string representing anatomical locations to UBERON terms.

    TODO -- replace this with file based version covering all of the strings we need in CDA
    """

    def __init__(self):
        """
        This is a simple map from the 'primary_diagnosis_site = row["primary_diagnosis_site"]' field of the diagnosis row
        """
        super().__init__(('primary_diagnosis_site',))
        self._uberon_label_to_id = {
            'lung': 'UBERON:0002048',
            "uterine cervix": "UBERON:0000002",
            "uterus": "UBERON:0000995",
            "body of uterus": "UBERON:0009853",
            "lower respiratory tract": "UBERON:0001558",
            'breast': 'UBERON:0000310',
            'bone marrow': 'UBERON:0002371',
            'bone': 'UBERON:0002481',
            'brain': 'UBERON:0000955',
            'colon': 'UBERON:0001155',
            'heart': 'UBERON:0000948',
            'kidney': 'UBERON:0002113',
            'adrenal gland': 'UBERON:0002369',
            'liver': 'UBERON:0002107',
            'pancreas': 'UBERON:0001264',
            'skin': 'UBERON:0002097',
            'thyroid gland': 'UBERON:0002046'
        }
        self._site_to_uberon_label_d = {
            "Lung": "lung",
            "Lung, NOS": "lung",
            "Cervix uteri": "uterine cervix",
            "Cervix Uteri": "uterine cervix",
            "Cervix Uteri, Unknown": "uterine cervix",
            "Cervix": "uterine cervix",
            "Uterus, NOS": "uterus",
            "Corpus uteri": "body of uterus",
            "Corpus Uteri": "body of uterus",
            "Corpus Uteri, Unknown": "body of uterus",
            "Uterus": "uterus",
            "Bronchus and lung": "lower respiratory tract",
            "Bronchus and Lung": "lower respiratory tract",
            "Lower lobe, lung": "lower respiratory tract",
            "Overlapping lesion of lung": "lower respiratory tract",
            "Lung/Bronchus": "lower respiratory tract",
            "Lung/Bronchus, Unknown": "lower respiratory tract",
            "Breast": "breast", 
            "Breast, NOS": "breast",
            "Breast, Unknown": "breast",
            "Bone marrow": "bone marrow", 
            "Bone Marrow": "bone marrow",
            "Bones, joints and articular cartilage of other and unspecified sites": "bone",
            "Bones, joints and articular cartilage of limbs": "bone",
            "Bones of skull and face and associated joints (excludes mandible C41.1)": "bone",
            "Long bones of lower limb and associated joints": "bone",
            "Long bones of upper limb, scapula and  associated joints": 'bone',
            "Pelvic bones, sacrum, coccyx and associated joints": "bone",
            "Bone, NOS" : 'bone',
            "Bone": "bone",
            "Bones": "bone",
            "Brain": "brain",
            "Brain, NOS": "brain",
            "Brain, Unknown": "brain",
            "Overlapping lesion of brain and central nervous system": "brain",
            "Overlapping lesion of brain": "brain",
            "Brain stem": "brain",
            "Colon": "colon",
            "Colon, NOS": "colon",
            "Colon, Unknown": "colon",
            "Heart, mediastinum, and pleura": "heart",
            "Connective, subcutaneous and other soft tissues of thorax (excludes thymus C37.9, heart and mediastinum C38._)": "heart",
            "Kidney": "kidney",
            "Kidney, NOS": "kidney",
            "Kidney, Unknown": "kidney",
            "Renal pelvis": "kidney",
            "Renal Pelvis": "kidney",
            "Adrenal gland": "adrenal gland",
            "Adrenal Gland": "adrenal gland",
            "Adrenal gland, NOS": "adrenal gland",
            "Adrenal gland, Unknown": "adrenal gland",
            "Liver and intrahepatic bile ducts": "liver",
            "Liver": "liver",
            "Intrahepatic bile ducts": "liver",
            "Pancreas": "pancreas",
            "Pancreas, NOS": "pancreas",
            "Pancreas, Unknown": "pancreas",
            "Pancreatic duct": "pancreas",
            "Skin": "skin",
            "Skin, NOS": "skin",
            "Skin, Unknown": "skin",
            "Connective, subcutaneous and other soft tissues": "skin",
            "Connective, subcutaneous and other soft tissues of pelvis": "skin",
            "Connective, subcutaneous and other soft tissues of lower limb and hip": "skin",
            "Connective, subcutaneous and other soft tissues, NOS": "skin",
            "Connective, subcutaneous and other soft tissues of upper limb and shoulder": "skin",
            "Connective, subcutaneous and other soft tissues of head, face, and neck (excludes connective tissue of orbit C69.6 and nasal cartilage C30.0)": "skin",
            "Skin of scalp and neck": "skin",
            "Skin of lower limb and hip": "skin",
            "Connective, subcutaneous and other soft tissues of abdomen": "skin",
            "Connective, subcutaneous and other soft tissues of trunk, NOS": "skin",
            "Skin, NOS (excludes skin of labia majora C51.0, skin of vulva C51.9, skin of penis C60.9 and skin of scrotum C63.2)": "skin",
            "Thyroid gland": "thyroid gland",
            "Thyroid Gland": "thyroid gland",
            "Thyroid gland, NOS": "thyroid gland",
            "Thyroid gland, Unknown": "thyroid gland",
            "Thyroid Gland, Unknown": "thyroid gland",
        }

    def get_ontology_term(self, row: pd.Series) -> Optional[PPkt.OntologyClass]:
        primary_site = row["primary_diagnosis_site"]


        if primary_site in self._site_to_uberon_label_d:
            # get standard label and UBEROBN id
            ontology_term = PPkt.OntologyClass()
            ontology_term.id = self._uberon_label_to_id.get(self._site_to_uberon_label_d.get(primary_site))
            ontology_term.label = self._site_to_uberon_label_d.get(primary_site)
            return ontology_term
        else:
            # TODO -- more robust error handling in final release, but for development fail early
            raise ValueError(f"Could not find UBERON term for primary_site=\"{primary_site}\"")
