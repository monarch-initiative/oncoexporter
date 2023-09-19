"""
oncopacket is a library for transforming National Cancer Institute (NCI) data into phenopackets.
"""

__version__ = '0.0.3'

from src.oncopacket.cda.cda_individual_etl import IndividualFactory

__all__ = [
    'IndividualFactory'
]
