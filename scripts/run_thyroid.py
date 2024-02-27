import os
from google.protobuf.json_format import MessageToJson

from cdapython import Q
from oncoexporter.cda import CdaTableImporter, configure_cda_table_importer

table_importer: CdaTableImporter = configure_cda_table_importer()

Tsite = Q('primary_diagnosis_site = "%thyroid%" OR primary_diagnosis_site = "%thyroidal%"', )
cohort_name = 'Thyroid'
p = table_importer.get_ga4gh_phenopackets(Tsite, cohort_name=cohort_name)

result_dir = os.path.abspath(os.path.join('phenopackets', cohort_name))
os.makedirs(result_dir, exist_ok=True)

print(f'Writing {len(p)} phenopackets to {result_dir}')
for pp in p:
    file_path = os.path.join(result_dir, f'{pp.id}.json')
    with open(file_path, 'w') as fh:
        json = MessageToJson(pp)
        fh.write(json)
