import abc
from protobuf import Message


class MessageFactory(metaclass=abc.ABCMeta):
    pass

    # @abc.abstractmethod
    def to_ga4gh(self):
        pass
