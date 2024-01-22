import os
from google.protobuf.json_format import MessageToJson

from cdapython import Q
from oncoexporter.cda import CdaTableImporter

Tsite = Q('primary_diagnosis_site = "%lung%" OR primary_diagnosis_site = "%pulmonary%"')
table_importer = CdaTableImporter(query=Tsite, use_cache=True, cohort_name='Lung')
p = table_importer.get_ga4gh_phenopackets(page_size=10000)

print("Created {} phenopackets".format(len(p)))

result_dir = 'phenopackets'
os.makedirs(result_dir, exist_ok=True)

for pp in p:
    file_path = os.path.join(result_dir, f'{pp.id}.json')
    with open(file_path, 'w') as fh:
        json = MessageToJson(pp)
        fh.write(json)
