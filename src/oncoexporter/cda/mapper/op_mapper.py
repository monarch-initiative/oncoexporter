import abc
import typing

import pandas as pd
import phenopackets as pp


class OpMapper(metaclass=abc.ABCMeta):
    """
    `OpMapper` finds an ontology term based on a table row.

    `OpMapper` transforms a row formatted into :class:`pd.Series` into an ontology term
    of the GA4GH Phenopacket Schema.
    For the CDA, we often need to transform combinations of strings in multiple columns into ontology terms.
    Implementing subclasses check one or more columns, and create ontology terms, if possible,
    based on this information. `None` is returned if a transformation is not possible.

    The mapper uses a subset of the row fields and advertises the names of the required fields through
    the :func:`get_fields` method. Absence of a required field will most likely raise an exception during parsing,
    or return of `None`.
    """

    def __init__(self, required_fields: typing.Iterable[str]):
        # a `set` to deduplicate.
        self._fields = tuple(set(required_fields))

    @abc.abstractmethod
    def get_ontology_term(self, row: pd.Series) -> typing.Optional[pp.OntologyClass]:
        """
        Map the `row` into an ontology term.

        :param row: a table row with information that we will transform into an ontology term.
        """
        pass

    def get_fields(self) -> typing.Sequence[str]:
        """
        Get a sequence of field names required by this mapper.
        """
        return self._fields
