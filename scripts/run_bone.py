import os
from google.protobuf.json_format import MessageToJson

from oncoexporter.cda import CdaTableImporter, configure_cda_table_importer

######   Input parameters  ########
table_importer: CdaTableImporter = configure_cda_table_importer(use_cache=True)

Query = {'match_any': ['primary_diagnosis_site = *bone*',
                       'primary_diagnosis_site = *osseous*'],
         'data_source': 'GDC'}
cohort_name = 'Bone'

p = table_importer.get_ga4gh_phenopackets(Query, cohort_name=cohort_name)

result_dir = os.path.abspath(os.path.join('phenopackets', cohort_name))
os.makedirs(result_dir, exist_ok=True)

print(f'Writing {len(p)} phenopackets to {result_dir}')
for pp in p:
    file_path = os.path.join(result_dir, f'{pp.id}.json')
    with open(file_path, 'w') as fh:
        json = MessageToJson(pp)
        fh.write(json)

