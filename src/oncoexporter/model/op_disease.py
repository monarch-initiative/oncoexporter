from .op_message import OpMessage
import phenopackets as PPKt
from typing import List

class OpDisease(OpMessage):
    """OncoPacket Individual
        This class should not be used by client code. It provides a DTO-like object to hold
        data that should be instantiated by various factory methods, and it can return
        a GA4GH Individual message
        THe fields of GA4GHDisease are:
        term 	OntologyClass 	REQUIRED.
        excluded 	boolean 	0..1 	Flag to indicate whether the disease was observed or not.
        onset 	TimeElement 	0..1 	an element representing the age of onset of the disease
        resolution 	TimeElement 	0..1 	an element representing the age of resolution (abatement) of the disease
        disease_stage 	OntologyClass (List) 	0..* 	List of terms representing the disease stage e.g. AJCC stage group.
        clinical_tnm_finding 	OntologyClass (List) 	0..* 	List of terms representing the tumor TNM score
        primary_site 	OntologyClass 	0..1 	the primary site of disease
        laterality OntologyClass
        """

    def __init__(self, disease_term:PPKt.OntologyClass,
                excluded:bool=None,
                iso8601duration_onset_age:str=None,
                iso8601duration_resolution_age: str = None,
                disease_stage_term_list:List[str]=None,
                disease_stage_term_label:str=None,
                clinical_tnm_finding_list:list=None,
                primary_site_id:str=None,
                primary_site_label: str = None,
                laterality:str=None) -> None:

        disease_obj = PPKt.Disease()
        disease_obj.term.CopyFrom(disease_term)
        if excluded is not None:
            disease_obj.excluded = excluded
        if iso8601duration_onset_age is not None:
            disease_obj.onset.age.iso8601duration = iso8601duration_onset_age
        if iso8601duration_resolution_age is not None:
            disease_obj.resolution.age.iso8601duration = iso8601duration_resolution_age
        if disease_stage_term_list is not None:
            if not isinstance(disease_stage_term_list, list):
                raise ValueError(f"If passed, argument \"disease_stage_term_list\" must be a list but was {type(disease_stage_term_list)}")
        if disease_stage_term_list and len(disease_stage_term_list) == 0:
            raise ValueError(f"If passed, argument \"disease_stage_term_list\" cannot be an empty list")


        self._disease = disease_obj





    def to_ga4gh(self):
        return self._disease
