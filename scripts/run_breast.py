import os
from google.protobuf.json_format import MessageToJson

from cdapython import Q
from oncoexporter.cda import CdaTableImporter, configure_cda_table_importer

table_importer: CdaTableImporter = configure_cda_table_importer()

Tsite_breast = Q('primary_diagnosis_site = "%breast%"')
cohort_name_breast = 'Breast'
p_breast = table_importer.get_ga4gh_phenopackets(Tsite_breast, cohort_name=cohort_name_breast)


result_dir_breast = os.path.abspath(os.path.join('phenopackets', cohort_name_breast))
os.makedirs(result_dir_breast, exist_ok=True)

# Writing phenopackets for Breast tissue
print(f'Writing {len(p_breast)} phenopackets to {result_dir_breast}')
for pp in p_breast:
    file_path = os.path.join(result_dir_breast, f'{pp.id}.json')
    with open(file_path, 'w') as fh:
        json = MessageToJson(pp)
        fh.write(json)
