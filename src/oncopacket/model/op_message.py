import abc


class OpMessage(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def to_phenopacket(self):
        pass
