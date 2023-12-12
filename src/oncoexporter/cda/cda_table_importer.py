import os
import warnings
import requests
import csv
from cdapython import Q
import phenopackets as PPkt
import typing
import pandas as pd
import pickle
from .cda_disease_factory import CdaDiseaseFactory
from .cda_importer import CdaImporter
from .cda_individual_factory import CdaIndividualFactory
from .cda_biosample_factory import CdaBiosampleFactory
from .cda_mutation_factory import CdaMutationFactory
from .cda_medicalaction_factory import make_cda_medicalaction
from tqdm import tqdm


class CdaTableImporter(CdaImporter):
    """This class is the entry point for transforming CDA data into GA4GH Phenopackets. Client code only needs to initialize it with a CDA query and it can return phenopackets with the **get_ga4gh_phenopackets** method. It also returns individual tables for that can be used for testing or visualizing data.

    The CDA query determines the cohort that will be retrieved from CDA. This class then retrieves data for this cohort in form of pandas DataFrames and extracts data for phenopacket construction using the data in the tables

    :param cohort_name: A user-chosen name for the cohort
    :type cohort_name: str
    :param query: A query for CDA such as 'primary_diagnosis_site = "Lung"'
    :type query: str
    :param query_obj: a query object created by CDA. Note that either this argument or the query (string) argument must be provided, but not both.
    :type query_obj: Q
    :param use_cache: if True, cache/retrieve from cache
    :type use_cache: bool
    """

    def __init__(self, cohort_name: str, query: str = None, query_obj: Q = None,
                 use_cache=False,
                 icdo_to_ncit_map_url='https://evs.nci.nih.gov/ftp1/NCI_Thesaurus/Mappings/ICD-O-3_Mappings/ICD-O-3.1-NCIt_Morphology_Mapping.txt'):
        """Constructor
        """
        if query is not None and query_obj is None:
            self._query = Q(query)
        elif query_obj is not None and query is None:
            if not isinstance(query_obj, Q):
                raise ValueError(f"query_obj argument must be Q.Q object, but instead was {type(query_obj)}")
            self._query = query_obj
        else:
            raise ValueError("Need to pass either query or query_obj argument but not both")
        self._use_cache = use_cache
        self._cohort_name = cohort_name
        self._icdo_to_ncit = self._download_and_icdo_to_ncit_tsv(icdo_to_ncit_map_url)
        pass

    def _download_and_icdo_to_ncit_tsv(self, url: str, key_column: str = 'ICD-O Code') -> dict:
        """
        Helper function to download a TSV file, parse it, and create a dict of dicts.
        """
        response = requests.get(url)
        response.raise_for_status()  # This will raise an error if the download failed

        tsv_data = csv.DictReader(response.text.splitlines(), delimiter='\t')

        result_dict = {}
        if key_column not in tsv_data.fieldnames:
            warnings.warn(f"Couldn't find key_column {key_column} in fieldnames "
                          f"{tsv_data.fieldnames} of file downloaded from {url}")
        for row in tsv_data:
            key = row.pop(key_column, None)
            if key:
                result_dict[key] = row

        return result_dict

    def _get_cda_df(self, callback_fxn, cache_name: str):
        print(f"Retrieving dataframe {cache_name}")
        if self._use_cache and os.path.isfile(cache_name):
            with open(cache_name, 'rb') as cachehandle:
                print(f"loading cached dataframe from {cache_name}")
                individual_df = pickle.load(cachehandle)
        else:
            print(f"calling CDA function")
            individual_df = callback_fxn()
            if self._use_cache:
                print(f"Creating cached dataframe as {cache_name}")
                with open(cache_name, 'wb') as f:
                    pickle.dump(individual_df, f)
        return individual_df


    def get_subject_df(self, page_size=10000) -> pd.DataFrame:
        """Retrieve the subject dataframe from CDA

        This method uses the Query that was passed to the constructor to retrieve data from the CDA subject table

        :param page_size: Number of pages to retrieve at once. Defaults to 10000.
        :type page_size: int

        :raises: raises an exception if the query object was not properly initialized
        :returns: pandas DataFrame that corresponds to the CDA subject table.
        :rtype: pd.DataFrame
        """
        if self._query is None:
            raise Exception(f"Could not retrieve subject dataframe because query object was None")
        callable = lambda: self._query.subject.run(page_size=page_size).get_all().to_dataframe();
        subject_df = self._get_cda_df(callable, f".{self._cohort_name}_individual_df.pkl");
        return subject_df


    def get_merged_diagnosis_research_subject_df(self, page_size=10000) -> pd.DataFrame:
        """Retrieve a merged dataframe from CDA corresponding to the diagnosis and research subject tables

        :param page_size: Number of pages to retrieve at once. Defaults to 10000.
        :type page_size: int
        """
        diagnosis_callable = lambda: self._query.diagnosis.run(page_size=page_size).get_all().to_dataframe()
        diagnosis_df = self._get_cda_df(diagnosis_callable, f".{self._cohort_name}_diagnosis_df.pkl")
        print("obtained diagnosis_df")
        rsub_callable = lambda: self._query.researchsubject.run(page_size=page_size).get_all().to_dataframe()
        rsub_df = self._get_cda_df(rsub_callable, f".{self._cohort_name}_rsub_df.pkl")
        print("obtained rsub_df")
        merged_df = pd.merge(diagnosis_df, rsub_df, left_on='researchsubject_id', right_on='researchsubject_id',
                                suffixes=["_di", "_rs"])
        return merged_df

    def get_specimen_df(self, page_size=10000) -> pd.DataFrame:
        """Retrieve the subject dataframe from CDA

        This method uses the Query that was passed to the constructor to retrieve data from the CDA subject table

        :param page_size: Number of pages to retrieve at once. Defaults to 10000.
        :type page_size: int

        :raises: raises an exception if the query object was not properly initialized
        :returns: pandas DataFrame that corresponds to the CDA subject table.
        :rtype: pd.DataFrame
        """
        specimen_callable = lambda: self._query.specimen.run(page_size=page_size).get_all().to_dataframe()
        specimen_df = self._get_cda_df(specimen_callable, f".{self._cohort_name}_specimen_df.pkl")
        return specimen_df

    def get_treatment_df(self, page_size=10000) -> pd.DataFrame:
        treatment_callable = lambda: self._query.treatment.run(page_size=page_size).get_all().to_dataframe()
        treatment_df = self._get_cda_df(treatment_callable, f".{self._cohort_name}_treatment_df.pkl")
        return treatment_df

    def get_mutation_df(self, page_size=10000) -> pd.DataFrame:
        mutation_callable = lambda: self._query.mutation.run(page_size=page_size).get_all().to_dataframe()
        mutation_df = self._get_cda_df(mutation_callable, f".{self._cohort_name}_mutation_df.pkl")
        return mutation_df


    def get_ga4gh_phenopackets(self, page_size: int = 10000) -> typing.List[PPkt.Phenopacket]:
        """Get a list of GA4GH phenopackets corresponding to the individuals returned by the query passed to the constructor.

        :param page_size: Number of pages to retrieve at once. Defaults to 10000.
        :type page_size: int
        :returns: A list of GA4GH phenopackets corresponding to the individuals selected by the query passed to the constructor.
        :rtype: typing.List[PPkt.Phenopacket]
        """
        # Dictionary of phenopackets, keys are the phenopacket ids.
        ppackt_d = {}

        # First obtain the pandas DataFrames from the CDA tables with rows that correspond to the Query
        subject_df = self.get_subject_df(page_size=page_size)
        merged_df  = self.get_merged_diagnosis_research_subject_df(page_size=page_size)
        specimen_df = self.get_specimen_df(page_size=page_size)
        treatment_df = self.get_treatment_df(page_size=page_size)
        mutation_df = self.get_mutation_df(page_size=page_size)

        # Now use the CdaFactory classes to transform the information from the DataFrames into
        # components of the GA4GH Phenopacket Schema
        # Add these components one at a time to Phenopacket objects.

        individual_factory = CdaIndividualFactory()
        disease_factory = CdaDiseaseFactory()
        specimen_factory = CdaBiosampleFactory()
        mutation_factory = CdaMutationFactory()
        # treatment_factory = TODO

        # Retrieve GA4GH Individual messages
        for _, row in tqdm(subject_df.iterrows(),total=len(subject_df), desc= "individual dataframe"):
            individual_message = individual_factory.to_ga4gh(row=row)
            individual_id = individual_message.id
            ppackt = PPkt.Phenopacket()
            ppackt.id = f'{self._cohort_name}-{individual_id}'
            ppackt.subject.CopyFrom(individual_message)
            ppackt_d[individual_id] = ppackt

        # Retrieve GA4GH Disease messages
        for _, row in tqdm(merged_df.iterrows(), total= len(merged_df.index), desc="merged diagnosis dataframe"):
            disease_message = disease_factory.to_ga4gh(row)
            pp = ppackt_d.get(row["subject_id_rs"])

            # Do not add the disease if it is already in the phenopacket.
            if not any(disease.term.id == disease_message.term.id for disease in pp.diseases):
                pp.diseases.append(disease_message)

        # Retrieve GA4GH Biospecimen messages
        for idx, row in tqdm(specimen_df.iterrows(),total= len(specimen_df.index), desc="specimen/biosample dataframe"):
            biosample_message = specimen_factory.to_ga4gh(row)
            individual_id = row["subject_id"]
            if individual_id not in ppackt_d:
                raise ValueError(f"Attempt to enter unknown individual ID from biosample factory: \"{individual_id}\"")
            ppackt_d.get(individual_id).biosamples.append(biosample_message)

        # Retrieve GA4GH Genomic Interpretation messages (for mutation)
        for idx, row in tqdm(mutation_df.iterrows(), total=len(mutation_df.index), desc="mutation dataframe"):
            individual_id = row["cda_subject_id"]
            variant_interpretation_message = mutation_factory.to_ga4gh(row)
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
                raise ValueError(f"Attempt to enter unknown individual ID from treatemtn factory: \"{individual_id}\"")
            ppackt_d.get(individual_id).medical_actions.append(medical_action_message)

        # When we get here, we have constructed GA4GH Phenopackets with Individual, Disease, Biospecimen, MedicalAction, and GenomicInterpretations
        return list(ppackt_d.values())

