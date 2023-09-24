import abc



class OpMessage(metaclass=abc.ABCMeta):
    """
    The interface (superclass) for messages that transform data into messages of the GA4GH Phenopacket Schema
    """


    @abc.abstractmethod
    def to_ga4gh(self):
        """
        :return: An message corresponding to a message of the GA4GH Phenopacket Schema
        :rtype: a protobuf message
        """
        pass
