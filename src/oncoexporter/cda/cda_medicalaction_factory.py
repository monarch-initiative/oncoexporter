import typing
import pandas as pd
import phenopackets as pp

Progressive_Disease = pp.OntologyClass(id='NCIT:C142356', label='iRECIST Confirmed Progressive Disease')
Complete_Response = pp.OntologyClass(id='NCIT:C142357', label='iRECIST Complete Response')
Treatment_Ongoing = pp.OntologyClass(id='NCIT:C185657', label='Interim Response')
NONE = pp.OntologyClass(id='NCIT:C142359', label='iRECIST Stable Disease')
UNKNOWN = pp.OntologyClass(id='NCIT:C17998', label='Unknown')

CARBOPLATIN = pp.OntologyClass(id='NCIT:C1282', label='Carboplatin')
PACLITAXEL = pp.OntologyClass(id='NCIT:C1411', label='Paclitaxel')
PEMETREXED = pp.OntologyClass(id='NCIT:C61614', label='Pemetrexed')
AFATINIB = pp.OntologyClass(id='NCIT:C669409', label='Afatinib')
CYCLOPHOSPHAMIDE = pp.OntologyClass(id='NCIT:C405', label='Cyclophosphamide')
CISPLATIN = pp.OntologyClass(id='NCIT:C376', label='Cisplatin')
DOXORUBICIN = pp.OntologyClass(id='NCIT:C456', label='Doxorubicin')
BEVACIZUMAB = pp.OntologyClass(id='NCIT:C2039', label='Bevacizumab')
IFOSFAMIDE = pp.OntologyClass(id='NCIT:C564', label='Ifosfamide')
ETOPOSIDE = pp.OntologyClass(id='NCIT:C491', label='Etoposide')
ZOLEDRONIC_ACID= pp.OntologyClass(id='NCIT:C1699', label='Zoledronic Acid')
ERLOTINIB = pp.OntologyClass(id='NCIT:C65530', label='Erlotinib')
PEMBROLIZUMAB = pp.OntologyClass(id='NCIT:C106432', label='Pembrolizumab')
DOCETAXEL = pp.OntologyClass(id='NCIT:C1526', label='Docetaxel')
VINCREISTINE = pp.OntologyClass(id='NCIT:C933', label='Vincristine')
Not_Otherwise_Specified = pp.OntologyClass(id='NCIT:C19594', label='Not Otherwise Specified')
UNKNOWN = pp.OntologyClass(id='NCIT:C17998', label='Unknown')





def make_cda_medicalaction(row: pd.Series) -> pp.MedicalAction:
    medicalaction = pp.MedicalAction()

    treatment_type = row["treatment_type"]
    if treatment_type == "Chemotherapy":
        # Use the GA4GHTreatment message
        # therapeutic_agent -> treatment agent
        treatment_agent = _map_therapeutic_agent(row['therapeutic_agent'])
        # radiation = _map_radiation(row['therapeutic_agent'])
        if treatment_agent is not None:
            treatment = pp.Treatment()
            treatment.agent.CopyFrom(treatment_agent)
            medicalaction.treatment.CopyFrom(treatment)
    elif "Radiation Therapy, NOS" == treatment_type:
        ## Use GA4GH RadiationTherapy object
        pass


    # treatment_outcome -> response_to_treatment
    response_to_treatment = _map_response_to_treatment(row['treatment_outcome'])
    if response_to_treatment is not None:
        medicalaction.response_to_treatment.CopyFrom(response_to_treatment)

    return medicalaction


def _map_response_to_treatment(val: typing.Optional[str]=None) -> typing.Optional[pp.OntologyClass]:
    if val is not None:
        val = val.lower()
        if val == "progressive disease":
            return Progressive_Disease
        elif val == "complete response":
            return Complete_Response
        elif val == "treatment ongoing":
            return Treatment_Ongoing
        elif val == "none":
            return NONE
        elif val == "unknown":
            return UNKNOWN
        else:
            return None
    else:
        return None



def _map_response_to_treatment(val: typing.Optional[str]=None) -> typing.Optional[pp.OntologyClass]:
    if val is not None:
        val = val.lower()
        if val == "carboplatin":
            return CARBOPLATIN
        elif val == "paclitaxel":
            return PACLITAXEL
        elif val == "pemetrexed":
            return PEMETREXED
        elif val == "afatinib":
            return AFATINIB
        elif val == "cyclophosphamide":
            return CYCLOPHOSPHAMIDE
        elif val == "cisplatin":
            return CISPLATIN
        elif val == "doxorubicin":
            return DOXORUBICIN
        elif val == "bevacizumab":
            return BEVACIZUMAB
        elif val == "ifosfamide":
            return IFOSFAMIDE
        elif val == "etopside":
            return ETOPOSIDE
        elif val == "zoledronic acid":
            return ZOLEDRONIC_ACID
        elif val == "erlotinib":
            return ERLOTINIB
        elif val == "pembrolizumab":
            return PEMBROLIZUMAB
        elif val == "docetaxel":
            return DOCETAXEL
        elif val == "vincreistine":
            return VINCREISTINE
        elif val == "not otherwise specified":
            return Not_Otherwise_Specified
        elif val == "unknown":
            return UNKNOWN
        else:
            return None
    else:
        return None
