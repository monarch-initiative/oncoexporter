from cdapython import Q
from oncoexporter.cda import CdaTableImporter
Tsite = Q('primary_diagnosis_site = "%lung%" OR primary_diagnosis_site = "%pulmonary%"')
table_importer = CdaTableImporter(query_obj=Tsite, use_cache=True)
p = table_importer.get_ga4gh_phenopackets(page_size=10000)
from google.protobuf.json_format import MessageToJson

for ppkt in p:
    pass
    for i in ppkt.interpretations:
        if len(i.diagnosis.genomic_interpretations) > 0:
            print(MessageToJson(i))
