.. _workplan:

=========
Work plan
=========

The goal of this pilot project is to create a Python package that will simplify the encoding of oncology clinical data
using the `GA4GH Phenopakcet Schema <https://phenopacket-schema.readthedocs.io/en/latest/>`_.

The `pyphetools <https://github.com/monarch-initiative/pyphetools>`_ project has a comparable code base targeted 
a rare disease.


This pilot project will use the API of the `CDA project <https://github.com/CancerDataAggregator/cda-python.git>`_ 
to access `Cancer Data Aggregator <https://datacommons.cancer.gov/cancer-data-aggregator>`_ resources, and output 
patient data using the Phenopacket Schema. The C2P code can then be extended to ingest data from other sources. 