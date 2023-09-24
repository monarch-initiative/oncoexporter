from .op_message import OpMessage

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

    def __init__(self, disease_term_id,
                 disease_term_label,
                 excluded:bool=None,
                 iso8601duration_onset_age:str=None,
                 iso8601duration_resolution_age: str = None,
                 disease_stage_term_id:str=None,
                 disease_stage_term_label:str=None,
                 clinical_tnm_finding_list:list=None,
                 primary_site_id:str=None,
                 primary_site_label: str = None,
                 laterality:str=None) -> None:
        pass