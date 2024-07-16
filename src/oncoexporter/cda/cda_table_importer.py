import os
#from cdapython import Q
from cdapython import tables, columns, column_values, fetch_rows, summary_counts # updated CDA 
import phenopackets as PPkt
import typing
import pandas as pd
import pickle
import re

from .cda_disease_factory import CdaDiseaseFactory
from .cda_importer import CdaImporter
from .cda_factory import CdaFactory
from .cda_individual_factory import CdaIndividualFactory
from .cda_biosample_factory import CdaBiosampleFactory
from .cda_mutation_factory import CdaMutationFactory
from ._gdc import GdcService
from .cda_medicalaction_factory import make_cda_medicalaction
from tqdm import tqdm

from datetime import datetime

#class CdaTableImporter(CdaImporter[Q]):
class CdaTableImporter(CdaImporter[fetch_rows]):
    """This class is the entry point for transforming CDA data into GA4GH Phenopackets. Client code only needs
    to initialize it with a CDA query, and it can return phenopackets with the :func:`get_ga4gh_phenopackets`.
    It also returns individual tables for that can be used for testing or visualizing data.

    The CDA query determines the cohort that will be retrieved from CDA. This class then retrieves data
    for this cohort in form of pandas DataFrames and extracts data for phenopacket construction using the data
    in the tables

    :param disease_factory: the component for mapping CDA table into Disease element of the Phenopacket Schema.
    :param cache_dir: a `str` with path to the folder to store the cache files
    :param use_cache: if True, cache/retrieve from cache
    :param page_size: Number of pages to retrieve at once. Defaults to `10000`
    
    New CDA: 
    https://cda.readthedocs.io/en/latest/documentation/cdapython/code_update/#returning-a-matrix-of-results
    old: all of the functions previously used with, or chained onto Q()...run() have been replaced with the single function fetch_rows()
    new: `fetch_rows(table=, )
    
    https://cda.readthedocs.io/en/latest/documentation/cdapython/code_update/#parameters
    old: page_size, limit, and count parameters have been removed
    new: column_values always returns all unique values and their counts by default, however there are several new parameters
    
    old: system=<data source>
    new: data_source=<data source> can now take a list, as in data_source=["GDC", "PDC"]

    new: sort_by=<column:asc/desc> sort results by any column

    new: force=<True/False> For columns with an extremely large number of unique values, such as filename, the query will fail with a large data warning. 
    You can override the warning with Force=True

    tables: ['diagnosis', 'file', 'researchsubject', 'somatic_mutation', 'specimen', 'subject', 'treatment']
    """

    def __init__(self,
                 disease_factory: CdaDiseaseFactory,
                 use_cache: bool = False,
                 cache_dir: typing.Optional[str] = None,
                 #page_size: int = 10000,
                 gdc_timeout: int = 100000,
                 ):
        self._use_cache = use_cache
        #self._page_size = page_size # not in new CDA 

        self._individual_factory = CdaIndividualFactory()
        self._disease_factory = disease_factory # why is disease_factory set up differently than the others?
        self._specimen_factory = CdaBiosampleFactory()
        self._mutation_factory = CdaMutationFactory()
        self._gdc_service = GdcService(timeout=gdc_timeout)

        if cache_dir is None:
            self._cache_dir = os.path.join(os.getcwd(), '.oncoexporter_cache')
            if not os.path.isdir(self._cache_dir):
                os.makedirs(self._cache_dir, exist_ok=True)
        else:
            if not os.path.isdir(cache_dir) or not os.access(cache_dir, os.W_OK):
                raise ValueError(f'`cache_dir` must be a writable directory: {cache_dir}')

    def _get_cda_df(self, callback_fxn, cache_name: str):
        fpath_cache = os.path.join(self._cache_dir, cache_name)
        if self._use_cache and os.path.isfile(fpath_cache):
            print(f"\tRetrieving dataframe {fpath_cache}")
            with open(fpath_cache, 'rb') as cachehandle:
                print(f"loading cached dataframe from {fpath_cache}")
                individual_df = pickle.load(cachehandle)
        else:
            print(f"\tcalling CDA function")
            individual_df = callback_fxn()
            if self._use_cache:
                print(f"Creating cached dataframe as {fpath_cache}")
                with open(fpath_cache, 'wb') as f:
                    pickle.dump(individual_df, f)
        return individual_df
    def get_subject_df(self, q: dict, cohort_name: str) -> pd.DataFrame:
        """Retrieve the subject dataframe from CDA

        This method uses the Query that was passed to the constructor to retrieve data from the CDA subject table

        :raises: raises an exception if the query object was not properly initialized
        :returns: pandas DataFrame that corresponds to the CDA subject table.
        :rtype: pd.DataFrame
        """
        print("\nGetting subject df...")
        callable = lambda: fetch_rows( table='subject', **q, provenance=True )
        subject_df = self._get_cda_df(callable, f"{cohort_name}_individual_df.pkl")
        subject_df = subject_df.drop(columns=['subject_data_source_id'], axis=1)
        subject_df = subject_df.drop_duplicates()
        print("obtained subject_df")

        return subject_df

    def get_researchsubject_df(self, q: dict, cohort_name: str) -> pd.DataFrame:
        
        print("\nGetting researchsubject df...")
        # tried link_to_table='diagnosis' but it doesn't add any columns
        # research = fetch_rows(table='researchsubject', provenance=True)
        rsub_callable = lambda: fetch_rows( table='researchsubject', **q , add_columns=['subject_id'])
        rsub_df = self._get_cda_df(rsub_callable, f"{cohort_name}_researchsubject_df.pkl") 
        print("obtained researchsubject_df")
        #rsub_df.to_csv('rsub_diagnosis_df.txt', sep='\t')

        return rsub_df

    def get_diagnosis_df(self, q: dict, cohort_name: str) -> pd.DataFrame:
                
        print("\nGetting diagnosis df...")
        # diag = fetch_rows(table='diagnosis', add_columns=['researchsubject_id'])
        diagnosis_callable = lambda: fetch_rows( table='diagnosis', **q , add_columns=['subject_id'])
        diagnosis_df = self._get_cda_df(diagnosis_callable, f"{cohort_name}_diagnosis_df.pkl")
        print("obtained diagnosis_df")
        #diagnosis_df.to_csv('diagnosis_df.txt', sep='\t')
        
        return diagnosis_df
    
    def get_specimen_df(self, q: dict, cohort_name: str) -> pd.DataFrame:
        """Retrieve the subject dataframe from CDA

        This method uses the Query that was passed to the constructor to retrieve data from the CDA subject table

        :raises: raises an exception if the query object was not properly initialized
        :returns: pandas DataFrame that corresponds to the CDA subject table.
        :rtype: pd.DataFrame
        """
        print("\nGetting specimen df...")
        #specimen_callable = lambda: q.specimen.run(page_size=self._page_size).get_all().to_dataframe()
        specimen_callable = lambda: fetch_rows( table='specimen', **q, add_columns=['subject_id'] )
        specimen_df = self._get_cda_df(specimen_callable, f"{cohort_name}_specimen_df.pkl")
        #specimen_df.to_csv('specimen_df.txt', sep='\t')
        return specimen_df

    def get_treatment_df(self, q: dict, cohort_name: str) -> pd.DataFrame:
        print("\nGetting treatment df...")
        #treatment_callable = lambda: q.treatment.run(page_size=self._page_size).get_all().to_dataframe()
        treatment_callable = lambda: fetch_rows( table='treatment', **q, add_columns=['subject_id'] )
        treatment_df = self._get_cda_df(treatment_callable, f"{cohort_name}_treatment_df.pkl")
        #treatment_df.to_csv('treatment_df.txt', sep='\t')
        return treatment_df

    def get_ga4gh_phenopackets(self, source: dict, **kwargs) -> typing.List[PPkt.Phenopacket]:
        """Get a list of GA4GH phenopackets corresponding to the individuals returned by the query passed to the constructor.

        :returns: A list of GA4GH phenopackets corresponding to the individuals selected by the query passed to the constructor.
        :rtype: typing.List[PPkt.Phenopacket]
        
        New version of CDA: need to change Q to fetch_rows()
        """
        # no longer using Q objects
        # if not isinstance(source, Q):
        #    raise ValueError(f"query_obj argument must be Q.Q object, but instead was {type(source)}")

        if 'cohort_name' in kwargs:
            cohort_name = kwargs['cohort_name']
        else:
            # Format timestamp as a string, for example: 'YYYY-MM-DD HH:MM:SS'
            ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            cohort_name = f'cohort-{ts}'

        # Dictionary of phenopackets, keys are the phenopacket ids.
        ppackt_d = {}

        # First obtain the pandas DataFrames from the CDA tables with rows that correspond to the Query
        # (MLS 6/18/24) rewriting this to get subject, researchsubject, diagnosis, specimen, and treatment dataframes,
        # then merge them here to avoid getting researchsubject and subject dataframes multiple times.
        
        subject_df = self.get_subject_df(source, cohort_name)
        rsub_df = self.get_researchsubject_df(source, cohort_name)
        diagnosis_df = self.get_diagnosis_df(source, cohort_name)
        specimen_df = self.get_specimen_df(source, cohort_name)
        treatment_df = self.get_treatment_df(source, cohort_name)
        
        # merge dfs:
        # can actually just make one merged df with subject_id, researchsubject_id, primary_diagnosis_condition,
        # primary_diagnosis_site, primary_diagnosis, age_at_diagnosis, stage
        # loop through it to generate:
        #  - disease_factory
        #  - vital_status
        #  - variants

        sub_rsub_diag_df = subject_df.merge(rsub_df, on='subject_id', how='outer')
        sub_rsub_diag_df = sub_rsub_diag_df.merge(diagnosis_df, on='subject_id', how='outer')
         
        print("merged subject-researchsubject-diagnosis df")
        print(sub_rsub_diag_df.shape)
        
        # Now use the CdaFactory classes to transform the information from the DataFrames into
        # components of the GA4GH Phenopacket Schema
        # Add these components one at a time to Phenopacket objects.

        # treatment_factory = TODO
        
        print("\nConverting to Phenopackets...\n")

        '''
        required fields:
        - 'stage'                           # getting from GDC 
        - 'primary_diagnosis_condition'     # diagnosis mapper 
        - 'primary_diagnosis_site'          # uberon mapper
        - 'primary_diagnosis'               # diagnosis mapper
        - 'age_at_diagnosis'                # disease term mapper
        '''
        
        # Retrieve GA4GH Individual messages
        for _, row in tqdm(subject_df.iterrows(), total=len(subject_df), desc= "individual dataframe"):
            try:
                individual_message = self._individual_factory.to_ga4gh(row=row)
            except ValueError as e:
                # TODO: decide how to handle depending on your paranoia
                #
                pass

            individual_id = individual_message.id
            ppackt = PPkt.Phenopacket()
            ppackt.id = f'{cohort_name}-{individual_id}'
            ppackt.subject.CopyFrom(individual_message)
            ppackt_d[individual_id] = ppackt

        # get stage dictionary
        print("Retrieving stage info from GDC...")
        stage_dict = self._gdc_service.fetch_stage_dict(sub_rsub_diag_df)
        # remove initial data source label: TCGA.TCGA-4J-AA1J > TCGA-4J-AA1J
        sub_rsub_diag_df['subject_id_short'] = sub_rsub_diag_df["subject_id"].str.extract(r'^[^\.]+\.(.+)', expand=False)
        sub_rsub_diag_df['stage'] = sub_rsub_diag_df['subject_id_short'].map(stage_dict).fillna(sub_rsub_diag_df['stage'])

        sub_rsub_diag_df['primary_diagnosis'] = sub_rsub_diag_df['primary_diagnosis'].fillna('') # remove nans (not sure why they are there)
        sub_rsub_diag_df.to_csv('sub_rsub_diag_df.txt', sep='\t')

        # Retrieve GA4GH Disease messages 
        for _, row in tqdm(sub_rsub_diag_df.iterrows(), total=len(sub_rsub_diag_df.index), desc="creating disease messsages"):
            #print(list(row))
            #print("\n", row["subject_id"])
            
            # Retrieve GA4GH Disease messages
            disease_message = self._disease_factory.to_ga4gh(row)
            pp = ppackt_d.get(row["subject_id"]) 
            
            # Do not add the disease if it is already in the phenopacket.
            if not any(disease.term.id == disease_message.term.id for disease in pp.diseases):
                pp.diseases.append(disease_message)

            # need to check if we have the age_at_diagnosis in the phenopacket message
            for disease in pp.diseases:
                if not disease.HasField("onset") and disease.term.id == disease_message.term.id and disease_message.HasField("onset"):
                    disease.onset.CopyFrom(disease_message.onset)
                
            # get vital status from GDC - probably not needed (should be same as subject_df obtained from CDA)
            # vital_status = self._gdc_service.fetch_vital_status(subj_id)
            # ppackt_d.get(individual_id).subject.vital_status.CopyFrom(vital_status)         

        # Get variant data 
        # takes ~45 minutes due to API calls to GDC
        sub_rsub_diag_GDC_df = sub_rsub_diag_df[sub_rsub_diag_df['subject_data_data_source' == 'GDC']]
        for _, row in tqdm(sub_rsub_diag_GDC_df.iterrows(), total=len(sub_rsub_diag_df.index), desc="getting variants from GDC"):

            individual_id = row["subject_id"]

            #for rsub_subj in row["subject_identifier"]:
            #if row["subject_data_source"] == "GDC":
            print("GDC variants...")
            # have to strip off the leading name before first period
            # e.g. TCGA.TCGA-05-4250 -> TCGA-05-4250
            subj_id = re.sub("^[^.]+\.", "", individual_id)
            #print(row["subject_id"], subj_id)
        
            # get variants
            variant_interpretations = self._gdc_service.fetch_variants(subj_id) # was rsub_subj['value']
            if len(variant_interpretations) == 0:
                #print("No variants found")
                continue
            #else:
                #print("length variant_interpretations: {}".format(len(variant_interpretations)))   
            
            # TODO: improve/enhance diagnosis term annotations
            diagnosis = PPkt.Diagnosis()
            diagnosis.disease.id = "NCIT:C3262"
            diagnosis.disease.label = "Neoplasm"

            for variant in variant_interpretations:
                genomic_interpretation = PPkt.GenomicInterpretation()
                genomic_interpretation.subject_or_biosample_id = individual_id
                genomic_interpretation.interpretation_status = PPkt.GenomicInterpretation.InterpretationStatus.UNKNOWN_STATUS
                genomic_interpretation.variant_interpretation.CopyFrom(variant)
                
                diagnosis.genomic_interpretations.append(genomic_interpretation)

            interpretation = PPkt.Interpretation()
            interpretation.id = f"{individual_id}-{row['researchsubject_id']}"
            interpretation.progress_status = PPkt.Interpretation.ProgressStatus.IN_PROGRESS 
            interpretation.diagnosis.CopyFrom(diagnosis)

            ppackt_d.get(individual_id).interpretations.append(interpretation)

            
        # Retrieve GA4GH Biospecimen messages
        for idx, row in tqdm(specimen_df.iterrows(),total=len(specimen_df.index), desc="specimen/biosample dataframe"):
            biosample_message = self._specimen_factory.to_ga4gh(row)
            individual_id = row["subject_id"]
            if individual_id not in ppackt_d:
                raise ValueError(f"Attempt to enter unknown individual ID from biosample factory: \"{individual_id}\"")
            
            # convert CDA days_to_collection to PPKt time_of_collection
            #         days_to_collection: number of days from index date to sample collection date
            #         time_of_collection: Age of subject at time sample was collected 
            if not pd.isna(row['days_to_collection']):
                days_to_coll_iso = CdaFactory.days_to_iso(int(row["days_to_collection"]))
            # this should work if both are pd.Timedelta:
            # TODO: fix the code below!
            # time_of_collection = ppackt_d[individual_id]["iso8601duration"] + days_to_coll_iso # should it be 'Age' or 'iso8601duration'?
            # biosample_message["time_of_collection"] = time_of_collection

            ppackt_d.get(individual_id).biosamples.append(biosample_message)

        # TODO Treatment
        # make_cda_medicalaction
        for idx, row in tqdm(treatment_df.iterrows(), total=len(treatment_df.index), desc="Treatment DF"):
            individual_id = row["subject_id"]
            medical_action_message = make_cda_medicalaction(row)
            if individual_id not in ppackt_d:
                raise ValueError(f"Attempt to enter unknown individual ID from treatment factory: \"{individual_id}\"")
            ppackt_d.get(individual_id).medical_actions.append(medical_action_message)

        # When we get here, we have constructed GA4GH Phenopackets with Individual, Disease, Biospecimen, MedicalAction, and GenomicInterpretations
        return list(ppackt_d.values())

