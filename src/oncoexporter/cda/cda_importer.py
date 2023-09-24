import abc
import typing
import phenopackets


class CdaImporter(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_ga4gh_phenopackets(self) -> typing.List[phenopackets.Phenopacket]:
        raise NotImplementedError("get_ga4gh_phenopackets needs to be implemented by a subclass")
