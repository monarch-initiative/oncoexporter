import pandas as pd
import csv





"""
This script is a heuristic designed to streamline mapping CDA diagnosis information to NCIT terms.
To run the script, first generate a file with the corresponding CDA data

from oncoexporter.cda import CdaTableImporter, CdaDiseaseFactory
from cdapython import ( Q, set_default_project_dataset, set_host_url, set_table_version )
set_default_project_dataset("gdc-bq-sample.dev")
set_host_url("http://35.192.60.10:8080/")
set_table_version("all_merged_subjects_v3_2_final")
cohort_name = "cervix cancer cohort"
query = 'treatment_anatomic_site = "Cervix"'
Tsite = Q('treatment_anatomic_site = "Cervix"')
tableImporter = CdaTableImporter(cohort_name=cohort_name, query_obj=Tsite);
merged_df = tableImporter.get_merged_diagnosis_research_subject_df();
merged_df.to_csv("merged_cervix_disease.tsv", sep="\t")

The relevant code from the oncoexporter to generate the merged table is as follows

diagnosis_callable = lambda: self._query.diagnosis.run(page_size=page_size).get_all().to_dataframe()
diagnosis_df = self._get_cda_df(diagnosis_callable, f".{self._cohort_name}_diagnosis_df.pkl")
print("obtained diagnosis_df")
rsub_callable = lambda: self._query.researchsubject.run(page_size=page_size).get_all().to_dataframe()
rsub_df = self._get_cda_df(rsub_callable, f".{self._cohort_name}_rsub_df.pkl")
print("obtained rsub_df")
merged_df = pd.merge(diagnosis_df, rsub_df, left_on='researchsubject_id', right_on='researchsubject_id',
                        suffixes=["_di", "_rs"])

"""
input_file = "../../../notebooks/merged_cervix_disease.tsv"

with open(input_file) as f:
    for line in f:
        print(line)