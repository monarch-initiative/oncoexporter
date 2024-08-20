import os
from google.protobuf.json_format import MessageToJson

from oncoexporter.cda import CdaTableImporter, configure_cda_table_importer

'''
https://cda.readthedocs.io/en/latest/documentation/cdapython/code_update/#returning-a-matrix-of-results
old: all of the functions previously used with, or chained onto Q()...run() have been replaced with the single function fetch_rows()

fetch_rows(table=None, *, match_all=[], match_any=[], data_source=[], add_columns=[], link_to_table='', provenance=False, count_only=False, return_data_as='dataframe', output_file='', debug=False)

fetch_rows( table='subject', match_all=[ 'primary_disease_type = *duct*', 'sex = F*' ] )
fetch_rows( table='researchsubject', match_all=[ 'primary_diagnosis_site = NULL' ] )
'''
######   Input parameters  ########
table_importer: CdaTableImporter = configure_cda_table_importer(use_cache=True)

Query = {'match_any': ['primary_diagnosis_site = *thyroid*',
                       'primary_diagnosis_site = *thyroidal*'],
         'data_source': 'GDC'}
cohort_name = 'Thyroid'
####################################

p = table_importer.get_ga4gh_phenopackets(Query, cohort_name=cohort_name)

result_dir = os.path.abspath(os.path.join('phenopackets', cohort_name))
os.makedirs(result_dir, exist_ok=True)

print(f'Writing {len(p)} phenopackets to {result_dir}')
for pp in p:
    file_path = os.path.join(result_dir, f'{pp.id}.json')
    with open(file_path, 'w') as fh:
        json = MessageToJson(pp)
        fh.write(json)
