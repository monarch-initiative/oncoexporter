"""
oncopacket is a library for transforming National Cancer Institute (NCI) data into phenopackets.
"""

__version__ = '0.0.3'

from src.oncopacket.cda.cda_individual_factory import CdaIndividualFactory

__all__ = [
    'CdaIndividualFactory'
]
