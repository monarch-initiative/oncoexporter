# Work plan

The goal of this pilot project is to create a Python package that will simplify the encoding of oncology clinical data
using the `GA4GH Phenopakcet Schema <https://phenopacket-schema.readthedocs.io/en/latest/>`_.

The `pyphetools <https://github.com/monarch-initiative/pyphetools>`_ project has a comparable code base targeted
a rare disease.


This pilot project will use the API of the `CDA project <https://github.com/CancerDataAggregator/cda-python.git>`_
to access `Cancer Data Aggregator <https://datacommons.cancer.gov/cancer-data-aggregator>`_ resources, and output
patient data using the Phenopacket Schema. The C2P code can then be extended to ingest data from other sources.


# GitHub project board

Let's use this [project board](https://github.com/orgs/monarch-initiative/projects/60/views/1){:target="_blank"} to keep track of issues.
The board is connected to the two repositories

- [oncoexporter](https://github.com/monarch-initiative/oncoexporter){:target="_blank"}
- []


## Work items

The first phase of work will be to provide and test ETL code to transform CDA data into collections of phenopackets.

Let's use the following table to keep track of our status.

| CDA ETL class                                            | Oncoexporter Class                           | Status                 |
|:---------------------------------------------------------|:---------------------------------------------|:-----------------------|
| [CdaIndividualFactory](./cda/cda_individual_factory.md)  | [OpIndividual](./model/op_individual.md)     | done, needs unit tests |

