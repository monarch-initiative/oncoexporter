import os.path

from cdapython import Q
import phenopackets as PPkt
import typing
import pandas as pd
import pickle
from . import CdaDiseaseFactory
from .cda_importer import CdaImporter
from .cda_individual_factory import CdaIndividualFactory
from .cda_biosample import CdaBiosampleFactory
from .cda_mutation_factory import CdaMutationFactory
from tqdm import tqdm

class CdaTableImporter(CdaImporter):


    def __init__(self, query:str=None, query_obj:Q=None, use_cache=False):
        """
        :param query: A query for CDA such as 'primary_diagnosis_site = "Lung"'

        The CDA query determines the cohort that will be retrieved from CDA.
        This class then retrieves data for this cohort in form of pandas DataFrames
        and extracts data for phenopacket construction using the data in the tables
        """
        if query is not None and query_obj is None:
            self._query = Q(query)
        elif query_obj is not None and query is None:
            if not isinstance(query_obj, Q):
                raise ValueError(f"query_obj argument must be Q.Q object, but instead was {type(query_obj)}")
            self._query = query_obj
        else:
            raise ValueError("Need to pass either query or query_obj argument but not both")
        self._ppackt_d = {} # key -- patient ID, value: PPkt.Phenopacket
        self._use_cache = use_cache

    def get_diagnosis_df(self, callable, cache_name: str):
        if self._use_cache and os.path.isfile((cache_name)):
            individual_df = pickle.load(cache_name)
        else:
            individual_df = callable()
            if self._use_cache:
                with open(cache_name, 'wb') as f:
                    pickle.dump(individual_df, f)
        return individual_df

    def get_ga4gh_phenopackets(self) -> typing.List[PPkt.Phenopacket]:
        """

        1.

        """
        subject_id_to_interpretation = {}

        individual_factory = CdaIndividualFactory()
        callable = self._query.subject.run().get_all().to_dataframe
        individual_df = self.get_diagnosis_df(callable, "individual_df.pkl")
        print("obtained individual_df")
        diagnosis_callable = self._query.diagnosis.run().get_all().to_dataframe
        diagnosis_df = self.get_diagnosis_df(diagnosis_callable, "diagnosis_df.pkl")
        print("obtained diagnosis_df")
        rsub_callable =  self._query.researchsubject.run().get_all().to_dataframe
        rsub_df = self.get_diagnosis_df(rsub_callable, "rsub_df.pkl")
        print("obtained rsub_df")
        specimen_callable = self._query.specimen.run.get_all().to_dataframe
        specimen_df = self.get_diagnosis_df(specimen_callable, "specimen_df.pkl")
        treatment_callable = self._query.treatment.run.get_all().to_dataframe
        treatment_df = self.get_diagnosis_df(treatment_callable, "treatment_df.pkl")
        mutation_callable = self._query.mutation.run.get_all().to_dataframe
        mutation_df = self.get_diagnosis_df(mutation_callable, "mutation_df.pkl")
        for idx, row in tqdm(individual_df.iterrows(), len(individual_df),"individual dataframe"):
            individual_message = individual_factory.from_cancer_data_aggregator(row=row)
            indivudal_id = individual_message.id
            interpretation = PPkt.Interpretation()
            interpretation.id = "id"
            interpretation.progress_status = PPkt.Interpretation.ProgressStatus.SOLVED
            subject_id_to_interpretation[indivudal_id] = interpretation
            ppackt = PPkt.Phenopacket()
            ppackt.subject.CopyFrom(individual_message)
            self._ppackt_d[indivudal_id] = ppackt
        merged_df = pd.merge(diagnosis_df, rsub_df, left_on='subject_id', right_on='subject_id',
                             suffixes=["_di", "_rs"])
        disease_factory = CdaDiseaseFactory()
        for idx, row in tqdm(merged_df.iterrows(), len(merged_df), "merged diagnosis dataframe"):
            disease_message = disease_factory.from_cancer_data_aggregator(row)
            individual_id = row["subject_id"]
            if individual_id not in subject_id_to_interpretation:
                raise ValueError(f"Could not find individual id {individual_id} in subject_id_to_disease")
            subject_id_to_interpretation.get(individual_id).diagnosis.append(disease_message.term)
            if individual_id not in self._ppackt_d:
                raise ValueError(f"Attempt to enter unknown individual ID from disease factory: \"{individual_id}\"")
            self._ppackt_d.get(individual_id).diseases.append(disease_message)

        specimen_factory = CdaBiosampleFactory()
        for idx, row in tqdm(specimen_df.iterrows(), len(specimen_df), "specimen/biosample dataframe"):
            biosample_message = specimen_factory.from_cancer_data_aggregator(row)
            individual_id = row["subject_id"]
            if individual_id not in self._ppackt_d:
                raise ValueError(f"Attempt to enter unknown individual ID from biosample factory: \"{individual_id}\"")
            self._ppackt_d.get(individual_id).biosamples.append(biosample_message)

        """
         
            if self._disease_id is not None and self._disease_label is not None:
                interpretation.diagnosis.disease.id = self._disease_id
                interpretation.diagnosis.disease.label = self._disease_label
            for var in self._interpretation_list:
                genomic_interpretation = phenopackets.GenomicInterpretation()
                genomic_interpretation.subject_or_biosample_id = self._individual_id
                # by assumption, variants passed to this package are all causative
                genomic_interpretation.interpretation_status = phenopackets.GenomicInterpretation.InterpretationStatus.CAUSATIVE
                genomic_interpretation.variant_interpretation.CopyFrom(var)
                interpretation.diagnosis.genomic_interpretations.append(genomic_interpretation)
            php.interpretations.append(interpretation)
        
        """
        mutation_factory = CdaMutationFactory()
        for idx, row in tqdm(mutation_df.iterrows(), len(mutation_df), "mutation dataframe"):
            individual_id = row["cda_subject_id"]
            if individual_id not in subject_id_to_interpretation:
                raise ValueError(f"Could not find individual id {individual_id} in subject_id_to_interpretation")
            pp = self._ppackt_d[individual_id]
            if len(pp.interpretations) == 0:
                interpretation = PPkt.Interpretation()
                disease = pp.diseases[0]
                diagnosis = PPkt.Diagnosis()
                diagnosis.disease.CopyFrom(disease.term)
                interpretation.diagnosis.CopyFrom(diagnosis)
                pp.interpretations.append(interpretation)
            else:
                diagnosis = pp.interpretations[0].diagnosis
            variant_interpretation_message = mutation_factory.from_cancer_data_aggregator(row)
            genomic_interpretation = PPkt.GenomicInterpretation()
            # TODO -- CLEAN UP
            genomic_interpretation.subject_or_biosample_id = row["Tumor_Aliquot_UUID"]
            # by assumption, variants passed to this package are all causative -- ASK CDA
            # genomic_interpretation.interpretation_status = PPkt.GenomicInterpretation.InterpretationStatus.CAUSATIVE
            genomic_interpretation.variant_interpretation.CopyFrom(variant_interpretation_message)
            diagnosis.genomic_interpretations.append(genomic_interpretation)

        return list(self._ppackt_d.values())

