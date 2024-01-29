import os
from google.protobuf.json_format import MessageToJson

from cdapython import Q
from oncoexporter.cda import CdaTableImporter

table_importer = CdaTableImporter(use_cache=True)
Tsite = Q('primary_diagnosis_site = "%lung%" OR primary_diagnosis_site = "%pulmonary%"')
p = table_importer.get_ga4gh_phenopackets(Tsite, cohort_name='Lung')

print("Created {} phenopackets".format(len(p)))

result_dir = 'phenopackets'
os.makedirs(result_dir, exist_ok=True)

for pp in p:
    file_path = os.path.join(result_dir, f'{pp.id}.json')
    with open(file_path, 'w') as fh:
        json = MessageToJson(pp)
        fh.write(json)
