import abc



class OpMessage(metaclass=abc.ABCMeta):


    @abc.abstractmethod
    def to_ga4gh(self):
        pass
