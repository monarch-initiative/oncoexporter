import os
import warnings
from cdapython import Q
import phenopackets as PPkt
import typing
import pandas as pd
import pickle
from .cda_disease_factory import CdaDiseaseFactory
from .cda_importer import CdaImporter
from .cda_factory import CdaFactory
from .cda_individual_factory import CdaIndividualFactory
from .cda_biosample_factory import CdaBiosampleFactory
from .cda_mutation_factory import CdaMutationFactory
from .cda_medicalaction_factory import make_cda_medicalaction
from tqdm import tqdm

from datetime import datetime


class CdaTableImporter(CdaImporter[Q]):
    """This class is the entry point for transforming CDA data into GA4GH Phenopackets. Client code only needs
    to initialize it with a CDA query, and it can return phenopackets with the :func:`get_ga4gh_phenopackets`.
    It also returns individual tables for that can be used for testing or visualizing data.

    The CDA query determines the cohort that will be retrieved from CDA. This class then retrieves data
    for this cohort in form of pandas DataFrames and extracts data for phenopacket construction using the data
    in the tables

    :param use_cache: if True, cache/retrieve from cache
    :type use_cache: bool
    :param cache_dir: a `str` with path to the folder to store the cache files
    :param page_size: Number of pages to retrieve at once. Defaults to 10000.
    :type page_size: int
    """

    def __init__(self, use_cache: bool = False,
                 cache_dir: typing.Optional[str] = None,
                 page_size: int = 10000):
        self._use_cache = use_cache
        self._page_size = page_size

        self._individual_factory = CdaIndividualFactory()
        self._disease_factory = CdaDiseaseFactory()
        self._specimen_factory = CdaBiosampleFactory()
        self._mutation_factory = CdaMutationFactory()

        if cache_dir is None:
            self._cache_dir = os.path.join(os.getcwd(), '.oncoexporter_cache')
            if not os.path.isdir(self._cache_dir):
                os.makedirs(self._cache_dir, exist_ok=True)
        else:
            if not os.path.isdir(cache_dir) or not os.access(cache_dir, os.W_OK):
                raise ValueError(f'`cache_dir` must be a writable directory: {cache_dir}')

    def _get_cda_df(self, callback_fxn, cache_name: str):
        fpath_cache = os.path.join(self._cache_dir, cache_name)
        print(f"Retrieving dataframe {fpath_cache}")
        if self._use_cache and os.path.isfile(fpath_cache):
            with open(fpath_cache, 'rb') as cachehandle:
                print(f"loading cached dataframe from {fpath_cache}")
                individual_df = pickle.load(cachehandle)
        else:
            print(f"calling CDA function")
            individual_df = callback_fxn()
            if self._use_cache:
                print(f"Creating cached dataframe as {fpath_cache}")
                with open(fpath_cache, 'wb') as f:
                    pickle.dump(individual_df, f)
        return individual_df


    def _get_subject_df(self, q: Q, cohort_name: str) -> pd.DataFrame:
        """Retrieve the subject dataframe from CDA

        This method uses the Query that was passed to the constructor to retrieve data from the CDA subject table

        :raises: raises an exception if the query object was not properly initialized
        :returns: pandas DataFrame that corresponds to the CDA subject table.
        :rtype: pd.DataFrame
        """
        callable = lambda: q.subject.run(page_size=self._page_size).get_all().to_dataframe()
        subject_df = self._get_cda_df(callable, f"{cohort_name}_individual_df.pkl")
        return subject_df


    def get_merged_diagnosis_research_subject_df(self, q: Q, cohort_name: str) -> pd.DataFrame:
        """Retrieve a merged dataframe from CDA corresponding to the diagnosis and research subject tables
        """
        diagnosis_callable = lambda: q.diagnosis.run(page_size=self._page_size).get_all().to_dataframe()
        diagnosis_df = self._get_cda_df(diagnosis_callable, f"{cohort_name}_diagnosis_df.pkl")
        print("obtained diagnosis_df")
        rsub_callable = lambda: q.researchsubject.run(page_size=self._page_size).get_all().to_dataframe()
        rsub_df = self._get_cda_df(rsub_callable, f"{cohort_name}_rsub_df.pkl")
        print("obtained rsub_df")
        merged_df = pd.merge(diagnosis_df, rsub_df, left_on='researchsubject_id', right_on='researchsubject_id',
                                suffixes=["_di", "_rs"])
        return merged_df

    def get_specimen_df(self, q: Q, cohort_name: str) -> pd.DataFrame:
        """Retrieve the subject dataframe from CDA

        This method uses the Query that was passed to the constructor to retrieve data from the CDA subject table

        :raises: raises an exception if the query object was not properly initialized
        :returns: pandas DataFrame that corresponds to the CDA subject table.
        :rtype: pd.DataFrame
        """
        specimen_callable = lambda: q.specimen.run(page_size=self._page_size).get_all().to_dataframe()
        specimen_df = self._get_cda_df(specimen_callable, f"{cohort_name}_specimen_df.pkl")
        return specimen_df

    def get_treatment_df(self, q: Q, cohort_name: str) -> pd.DataFrame:
        treatment_callable = lambda: q.treatment.run(page_size=self._page_size).get_all().to_dataframe()
        treatment_df = self._get_cda_df(treatment_callable, f"{cohort_name}_treatment_df.pkl")
        return treatment_df

    def get_mutation_df(self, q: Q, cohort_name: str) -> pd.DataFrame:
        mutation_callable = lambda: q.mutation.run(page_size=self._page_size).get_all().to_dataframe()
        mutation_df = self._get_cda_df(mutation_callable, f"{cohort_name}_mutation_df.pkl")
        return mutation_df


    def get_ga4gh_phenopackets(self, source: Q, **kwargs) -> typing.List[PPkt.Phenopacket]:
        """Get a list of GA4GH phenopackets corresponding to the individuals returned by the query passed to the constructor.

        :returns: A list of GA4GH phenopackets corresponding to the individuals selected by the query passed to the constructor.
        :rtype: typing.List[PPkt.Phenopacket]
        """
        if not isinstance(source, Q):
            raise ValueError(f"query_obj argument must be Q.Q object, but instead was {type(source)}")

        if 'cohort_name' in kwargs:
            cohort_name = kwargs['cohort_name']
        else:
            # Format it as a string, for example: 'YYYY-MM-DD HH:MM:SS'
            ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            cohort_name = f'cohort-{ts}'

        # Dictionary of phenopackets, keys are the phenopacket ids.
        ppackt_d = {}

        # First obtain the pandas DataFrames from the CDA tables with rows that correspond to the Query
        subject_df = self._get_subject_df(source)
        merged_df = self.get_merged_diagnosis_research_subject_df(source)
        specimen_df = self.get_specimen_df(source)
        treatment_df = self.get_treatment_df(source)
        mutation_df = self.get_mutation_df(source)

        # Now use the CdaFactory classes to transform the information from the DataFrames into
        # components of the GA4GH Phenopacket Schema
        # Add these components one at a time to Phenopacket objects.

        # treatment_factory = TODO

        # Retrieve GA4GH Individual messages
        for _, row in tqdm(subject_df.iterrows(),total=len(subject_df), desc= "individual dataframe"):
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

        # Retrieve GA4GH Disease messages
        for _, row in tqdm(merged_df.iterrows(), total= len(merged_df.index), desc="merged diagnosis dataframe"):
            disease_message = self._disease_factory.to_ga4gh(row)
            pp = ppackt_d.get(row["subject_id_rs"])

            # Do not add the disease if it is already in the phenopacket.
            if not any(disease.term.id == disease_message.term.id for disease in pp.diseases):
                pp.diseases.append(disease_message)

        # Retrieve GA4GH Biospecimen messages
        for idx, row in tqdm(specimen_df.iterrows(),total= len(specimen_df.index), desc="specimen/biosample dataframe"):
            biosample_message = self._specimen_factory.to_ga4gh(row)
            individual_id = row["subject_id"]
            if individual_id not in ppackt_d:
                raise ValueError(f"Attempt to enter unknown individual ID from biosample factory: \"{individual_id}\"")
            
            # convert CDA days_to_collection to PPKt time_of_collection
            #         days_to_collection: number of days from index date to sample collection date
            #         time_of_collection: Age of subject at time sample was collected 
            days_to_coll_iso = CdaFactory.days_to_iso(row["days_to_collection"])
            # this should work if both are pd.Timedelta: 
            time_of_collection = ppackt_d[individual_id]["iso8601duration"] + days_to_coll_iso # should it be 'Age' or 'iso8601duration'?
            biosample_message["time_of_collection"] = time_of_collection

            ppackt_d.get(individual_id).biosamples.append(biosample_message)


        # Retrieve GA4GH Genomic Interpretation messages (for mutation)
        for idx, row in tqdm(mutation_df.iterrows(), total=len(mutation_df.index), desc="mutation dataframe"):
            individual_id = row["cda_subject_id"]
            variant_interpretation_message = self._mutation_factory.to_ga4gh(row)
            genomic_interpretation = PPkt.GenomicInterpretation()
            genomic_interpretation.subject_or_biosample_id = row["Tumor_Aliquot_UUID"]
            genomic_interpretation.variant_interpretation.CopyFrom(variant_interpretation_message)

            pp = ppackt_d[individual_id]
            if len(pp.interpretations) == 0:
                diagnosis = PPkt.Diagnosis()
                if len(pp.diseases) == 0:
                    warnings.warn("Couldn't find a disease for this individual {individual_id}, so I'm using neoplasm")
                    disease = PPkt.Disease()
                    # assign neoplasm ncit
                    disease.term.id = "NCIT:C3262"
                    disease.term.label = "Neoplasm"
                    pp.diseases.append(disease)
                else:
                    disease = pp.diseases[0]
                diagnosis.disease.CopyFrom(disease.term)
                diagnosis.genomic_interpretations.append(genomic_interpretation)

                interpretation = PPkt.Interpretation()
                interpretation.progress_status = PPkt.Interpretation.ProgressStatus.SOLVED
                interpretation.id = "id"
                interpretation.diagnosis.CopyFrom(diagnosis)
                pp.interpretations.append(interpretation)
            else:
                pp.interpretations[0].diagnosis.genomic_interpretations.append(genomic_interpretation)

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

