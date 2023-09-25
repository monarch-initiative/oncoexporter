import os
import warnings

from cdapython import Q
import phenopackets as PPkt
import typing
import pandas as pd
import pickle
from .cda_disease_factory import CdaDiseaseFactory
from .cda_importer import CdaImporter
from .cda_individual_factory import CdaIndividualFactory
from .cda_biosample import CdaBiosampleFactory
from .cda_mutation_factory import CdaMutationFactory
from .cda_medicalaction_factory import make_cda_medicalaction
from tqdm import tqdm


class CdaTableImporter(CdaImporter):

    def __init__(self, cohort_name: str, query: str = None, query_obj: Q = None, use_cache=False):
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
        self._use_cache = use_cache
        self._cohort_name = cohort_name

    def get_diagnosis_df(self, fallback, cache_name: str):
        print(f"Retrieving dataframe {cache_name}")
        if self._use_cache and os.path.isfile(cache_name):
            with open(cache_name, 'rb') as cachehandle:
                print(f"loading cached dataframe from {cache_name}")
                individual_df = pickle.load(cachehandle)
        else:
            print(f"calling CDA function")
            individual_df = fallback()
            if self._use_cache:
                print(f"Creating cached dataframe as {cache_name}")
                with open(cache_name, 'wb') as f:
                    pickle.dump(individual_df, f)
        return individual_df

    def get_ga4gh_phenopackets(self, page_size: int = 100) -> typing.List[PPkt.Phenopacket]:
        """

        1.

        """
        ppackt_d = {}

        individual_factory = CdaIndividualFactory()
        callable = lambda: self._query.subject.run(page_size=page_size).get_all().to_dataframe()
        print("getting individual_df")
        individual_df = self.get_diagnosis_df(callable, "individual_df.pkl")
        print("obtained individual_df")
        diagnosis_callable = lambda: self._query.diagnosis.run(page_size=page_size).get_all().to_dataframe()
        diagnosis_df = self.get_diagnosis_df(diagnosis_callable, "diagnosis_df.pkl")
        print("obtained diagnosis_df")
        rsub_callable = lambda: self._query.researchsubject.run(page_size=page_size).get_all().to_dataframe()
        rsub_df = self.get_diagnosis_df(rsub_callable, "rsub_df.pkl")
        print("obtained rsub_df")

        specimen_callable = lambda: self._query.specimen.run(page_size=page_size).get_all().to_dataframe()
        specimen_df = self.get_diagnosis_df(specimen_callable, "specimen_df.pkl")

        treatment_callable = lambda: self._query.treatment.run(page_size=page_size).get_all().to_dataframe()
        treatment_df = self.get_diagnosis_df(treatment_callable, "treatment_df.pkl")

        mutation_callable = lambda: self._query.mutation.run(page_size=page_size).get_all().to_dataframe()
        mutation_df = self.get_diagnosis_df(mutation_callable, "mutation_df.pkl")

        for idx, row in tqdm(individual_df.iterrows(),total=len(individual_df), desc= "individual dataframe"):
            individual_message = individual_factory.from_cancer_data_aggregator(row=row)
            individual_id = individual_message.id

            ppackt = PPkt.Phenopacket()
            ppackt.id = f'{self._cohort_name}-{individual_id}'
            ppackt.subject.CopyFrom(individual_message)
            ppackt_d[individual_id] = ppackt
        merged_df = pd.merge(diagnosis_df, rsub_df, left_on='researchsubject_id', right_on='researchsubject_id',
                             suffixes=["_di", "_rs"])
        disease_factory = CdaDiseaseFactory()
        for idx, row in tqdm(merged_df.iterrows(), total= len(merged_df.index), desc="merged diagnosis dataframe"):
            disease_message = disease_factory.from_cancer_data_aggregator(row)
            pp = ppackt_d.get(row["subject_id_rs"])

            # Do not add the disease if it is already in the phenopacket.
            if not any(disease.term.id == disease_message.term.id for disease in pp.diseases):
                pp.diseases.append(disease_message)

        specimen_factory = CdaBiosampleFactory()
        for idx, row in tqdm(specimen_df.iterrows(),total= len(specimen_df.index), desc="specimen/biosample dataframe"):
            biosample_message = specimen_factory.from_cancer_data_aggregator(row)
            individual_id = row["subject_id"]
            if individual_id not in ppackt_d:
                raise ValueError(f"Attempt to enter unknown individual ID from biosample factory: \"{individual_id}\"")
            ppackt_d.get(individual_id).biosamples.append(biosample_message)

        mutation_factory = CdaMutationFactory()
        for idx, row in tqdm(mutation_df.iterrows(), total=len(mutation_df.index), desc="mutation dataframe"):
            individual_id = row["cda_subject_id"]
            variant_interpretation_message = mutation_factory.from_cancer_data_aggregator(row)
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

            # TODO -- CLEAN UP
            # by assumption, variants passed to this package are all causative -- ASK CDA
            # genomic_interpretation.interpretation_status = PPkt.GenomicInterpretation.InterpretationStatus.CAUSATIVE





        # make_cda_medicalaction
        for idx, row in tqdm(treatment_df.iterrows(), total=len(treatment_df.index), desc="Treatment DF"):
            individual_id = row["subject_id"]
            medical_action_message = make_cda_medicalaction(row)
            if individual_id not in ppackt_d:
                raise ValueError(f"Attempt to enter unknown individual ID from treatemtn factory: \"{individual_id}\"")
            ppackt_d.get(individual_id).medical_actions.append(medical_action_message)

        return list(ppackt_d.values())

