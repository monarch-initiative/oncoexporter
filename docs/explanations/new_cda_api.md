# Explanation of the new CDA API
New API implemented 4/10/24

From the CDA:

With regards to your first question, I have attached a solution I am still testing. I may not be able to discuss thus with the technical team until next week. I add the subject_id column to both the researchsubject and diagnosis tables them merge them with the subject table:
 
    research = fetch_rows(table='researchsubject', add_columns=['subject_id'])
    diag = fetch_rows(table='diagnosis', add_columns=['subject_id'])
    sub = sub.merge(research, on='subject_id', how='outer')
    sub = sub.merge(diag, on='subject_id', how='outer')
 
If this is a method that the technical team considers valid, it should be explained in the documentation. Your workflow should be fairly common for users. As I continue testing, I will let you know if I find problems with this approach. It produces multiple rows for subjects if they have multiple diagnosis_ids which is common in the PDC data and I will need to ask about this.
 
Your second question about link_to_table and add_columns is something we are still testing. You are correct this should not be something behind the scenes but rather clearly defined in the method documentation.

    research = fetch_rows(table='researchsubject', add_columns=['subject_id'])

    research.head()

### Data sources

The source repository can included in a data_source column with the addition of a provenance=True argument:
 
    sub = fetch_rows(table='subject', provenance=True)
 
The caveat is that if provenance is added to a table, add_columns cannot be used also. Another point is that a data_source_id column will be created as well which produces multiple rows when the record is found in multiple sources.
 
So if I add the provenance to subjects:
 
    sub = fetch_rows(table='subject', provenance=True)
 
then subject_data_source and subject_data_source_id will be added. I can then get the researchsubject and diagnosis tables and add the subject_id:
 
    research = fetch_rows(table='researchsubject', add_columns=['subject_id'])
    diag = fetch_rows(table='diagnosis', add_columns=['subject_id'])
 
and do the merge. I can also add the provenance to the researchsubject table:
 
    sub = fetch_rows(table='subject', add_columns=['researchsubject_id'])
    research = fetch_rows(table='researchsubject', provenance=True)
    diag = fetch_rows(table='diagnosis', add_columns=['researchsubject_id'])
 
or the diagnosis table:
 
    sub = fetch_rows(table='subject', add_columns=['diagnosis_id'])
    research = fetch_rows(table='researchsubject', add_columns=['diagnosis_id'])
    diag = fetch_rows(table='diagnosis', provenance=True)
 
In this last case, some subjects do not have diagnosis records, so those subjects are excluded.
 
In the attached notebooks of the three approaches (the output files are too big to attach, let me know if you want truncated versions), I consolidate the data_source_id columns (as opposed to just deleting it which works also) or else the merge expands each subject into many more rows. For example, for subject provenance I used:
 
    sub['subject_data_source_id_concat'] = sub.groupby(['subject_id','subject_data_source'])['subject_data_source_id'].transform(lambda x: ','.join(x))
    sub = sub.drop(columns=['subject_data_source_id'], axis=1)
    sub = sub.drop_duplicates()
 
 ### GDC diagnosis.tumor_stage

 I looked into this and discussed it with the CDA data team. The GDC data here:
 
https://portal.gdc.cancer.gov/analysis_page?app=CohortBuilder&tab=stage_classification
 
is available through the GDC API but it is not clearly described in the documentation. As you note, diagnoses.tumor_stage does not return any data. However, using the schema document here:
 
https://github.com/NCI-GDC/gdcdictionary/blob/develop/src/gdcdictionary/schemas/diagnosis.yaml
 
endpoints such as diagnoses.ajcc_pathologic_stage, diagnoses.ajcc_clinical_stage, diagnoses.ann_arbor_pathologic_stage, and diagnoses.ann_arbor_clinical_stage can be constructed. See gdc_cda_stage_060524.html.
 
For the CDA data team, reconciling different stage data from different systems is fraught with issues and not in their current scope. They query the tumor_stage endpoint only, which has no data.
 
With regards to vital status, try the demographic.vital_status endpoint. That should return data. Please let me know what other questions you have.