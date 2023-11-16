# CDA Disease

We extract information about the disease diagnosis from two CDA tables, `diagnosis` and `researchsubject`. We first summarize the tables and then outline our ETL strategy.



## diagnosis


| Column          | Example        | Explanation |
|:----------------|:---------------|:----------------|
| diagnosis_id | CGCI-HTMCP-CC.HTMCP-03-06-02424.HTMCP-03-06-02424_diagnosis| y |
| diagnosis_identifier | see below | y |
| primary_diagnosis | Squamous cell carcinoma, keratinizing, NOS | y |
| age_at_diagnosis | 13085.0 | y |
| morphology | 8071/3 | y |
| stage | None | y |
| grade | G3 | y |
| method_of_diagnosis | Biopsy | y |
| subject_id | CGCI.HTMCP-03-06-02424 | y |
| researchsubject_id | CGCI-HTMCP-CC.HTMCP-03-06-02424| y |


The fields of the table have the following meaning.

- diagnosis_id
Question: It seems as if this identifier has some syntex of meaning or is it random?
- diagnosis_identifier
Question: This field seems to have a lot of structure. How is it used in CDA and is there documentation on how to interpret it?
This field has the following structure.
```
[{'system': 'GDC',
  'field_name': 'case.diagnoses.diagnosis_id',
  'value': '06af070e-aad4-5b2d-a693-b6ccfe93985a'},
 {'system': 'GDC',
  'field_name': 'case.diagnoses.submitter_id',
  'value': 'HTMCP-03-06-02424_diagnosis'}]
```
- primary_diagnosis
This field represents the main cancer diagnosis of this individual
- age_at_diagnosis
This field represents the number of days of life of the individual on the day during which the cancer diagnosis was made.
- morphology
Question: What do entries such as `8071/3` mean? Is there a data dictionary for morphology?
- stage
Cancer stage.
- grade
Cancer grade. Note that in many tables there are strings such as G3. NCIT has more detailed terms, but we think it best to stick to the top level, and possible consider postcomposition to represent specific stage systems.
- method_of_diagnosis
This corresponds to
- subject_id
Identifier for the individual being investigated
- researchsubject_id
Identifier for the researchsubject (which can be a sample or an individaul - Question: where is this documented?)


## researchsubject


| Column          | Example        | Explanation |
|:----------------|:---------------|:----------------|
| researchsubject_id | CPTAC-3.C3L-00563 | y |
|  researchsubject_identifier     | see below | y |
|   member_of_research_project    | CPTAC-3 | y |
|  primary_diagnosis_condition     | Adenomas and Adenocarcinomas | y |
|  primary_diagnosis_site     | Uterus, NOS  | y |
|   subject_id    | CPTAC.C3L-00563 | y |


- researchsubject_id
xyz
- researchsubject_identifier
Question: How do we interpret this kind of structure:
```
[{'system': 'GDC',
  'field_name': 'case.case_id',
  'value': '2b1894fb-b168-42ca-942f-a5def0bb8309'},
 {'system': 'GDC', 'field_name': 'case.submitter_id', 'value': 'C3L-00563'}]
```

- member_of_research_project
Question: Where do we get more information about the research projects? What informationis available?
- primary_diagnosis_condition
Question: This seems to be duplicative with the field `primary_diagnosis` in the diagnosis table. What is the difference?
- primary_diagnosis_site
Todo - we can map this to uberon
- subject_id
This relates to the subject_id in other tables.
