from cdapython import Q
from oncoexporter.cda import CdaTableImporter
Tsite = Q('primary_diagnosis_site = "%lung%" OR primary_diagnosis_site = "%pulmonary%"')
table_importer = CdaTableImporter(query_obj=Tsite, use_cache=True)
p = table_importer.get_ga4gh_phenopackets(page_size=10000)
