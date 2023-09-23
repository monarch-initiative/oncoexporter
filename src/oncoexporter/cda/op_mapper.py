from typing import Optional
import phenopackets as PPkt



class OpMapper:
    """
    todo -- pass in path to NCI ontology, Mondo, etc, and make functions for text mining
    for now, maybe ingest tsv file with example terms
    """
    def __init__(self, ncit_obo=None) -> None:
        # init OAK for NCIT
        # init OAK for Mondo
        # etc.
        pass





    def get_nci_term(self, string) -> Optional[PPkt.OntologyClass]:
        oterm = PPkt.OntologyClass()
        if string == "Cancer Related":
            oterm.id = "NCIT:C156427"
            oterm.label = "Cancer-Related Death"
            return oterm
        else:
            return None