import abc
from typing import Optional
import phenopackets as PPkt




class OpMapper(metaclass=abc.ABCMeta):
    """
    Superclass for mapper objects that map input data to Ontology classes.
    Subclasses may create state in the constructor
    """

    @abc.abstractmethod
    def get_ontology_term(self, row) ->Optional[PPkt.OntologyClass]:
        """
        The factory classes take pandas table rows (Series) as input and transform them into messages in the
        GA4GH Phenopacket Schema. For the CDA, we often need to transform combinations of strings in multiple
        columns into Ontology terms. Implementing subclasses check one or more columns and create ontology
        terms if possible based on this information. They return None if a transformation is not possible.

        :param row: a table row with information that we will transform into an ontology term
        :type row: pd.core.Series
        :return: A GA4GH Phenopacket Schema OntologyClass message or None
        :rtype
        """
        raise NotImplementedError("method needs to be implemented in subclass")

    """
    def get_nci_term(self, string) -> Optional[PPkt.OntologyClass]:
        
    """