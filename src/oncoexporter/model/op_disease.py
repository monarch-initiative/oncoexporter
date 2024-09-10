from .op_message import OpMessage
import phenopackets as PPKt
from typing import List

class OpDisease(OpMessage):
    """OncoPacket representing the disease diagnosis

    This class should not be used by client code. It provides a DTO-like object to hold data that should be
    instantiated by various factory methods, and it can return a GA4GH Individual message

    :param  disease_term: An Ontology class that represents the disease diagnosis (corresponds to the term field in GA4GH Disease)
    :type disease_term: PPKt.OntologyClass
    :param excluded:   Flag to indicate whether the disease was explicitly excluded (default: false).
    :type excluded: bool
    :param iso8601duration_onset_age:  age of onset of the disease, enocded as an iso8601 duration
    :type iso8601duration_onset_age: str
    :param iso8601duration_resolution_age:age of resolution of the disease, enocded as an iso8601 duration
    :type iso8601duration_resolution_age: str
    :param disease_stage_term_list:List of terms representing the disease stage e.g. AJCC stage group.
    :type disease_stage_term_list:List[PPKt.OntologyClass]
    :param clinical_tnm_finding_list:List of terms representing the tumor TNM
    :type clinical_tnm_finding_list:List[PPKt.OntologyClass]
    :param primary_site: the primary site of disease
    :type primary_site:PPKt.OntologyClass
    :param laterality: Right/left (site of disease)
    :type laterality: PPKt.OntologyClass
    """
    def __init__(self, disease_term:PPKt.OntologyClass,
                excluded:bool=None,
                iso8601duration_onset_age:str=None,
                iso8601duration_resolution_age: str = None,
                disease_stage_term_list:List[PPKt.OntologyClass]=None,
                clinical_tnm_finding_list:List[PPKt.OntologyClass]=None,
                primary_site:PPKt.OntologyClass=None,
                laterality:str=None) -> None:
        """Constructor
        """
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
            if len(disease_stage_term_list) == 0:
                raise ValueError(f"If passed, argument \"disease_stage_term_list\" cannot be an empty list")
            for term in disease_stage_term_list:
                disease_obj.disease_stage.append(term)
        if clinical_tnm_finding_list is not None:
            if not isinstance(clinical_tnm_finding_list, list):
                raise ValueError(f"If passed, argument \"clinical_tnm_finding_list\" must be a list but was {type(clinical_tnm_finding_list)}")
            if len(clinical_tnm_finding_list) == 0:
                raise ValueError(f"If passed, argument \"clinical_tnm_finding_list\" cannot be an empty list")
            for term in clinical_tnm_finding_list:
                disease_obj.clinical_tnm_finding.append(term)
        if primary_site is not None:
            disease_obj.primary_site.CopyFrom(primary_site)
        if laterality is not None:
            disease_obj.laterality.CopyFrom(laterality)
        self._disease = disease_obj


    def to_ga4gh(self) -> PPKt.Disease:
        """_summary_

        :returns: A GA4GH protobof message representing the disease
        :rtype: PPKt.Disease
        """
        return self._disease
