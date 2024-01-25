import abc
import typing
import phenopackets


T = typing.TypeVar('T')


class CdaImporter(typing.Generic[T], metaclass=abc.ABCMeta):
    """
    `CdaImporter` transforms the input into phenopackets.
    """

    @abc.abstractmethod
    def get_ga4gh_phenopackets(self, source: T, **kwargs) -> typing.List[phenopackets.Phenopacket]:
        pass
