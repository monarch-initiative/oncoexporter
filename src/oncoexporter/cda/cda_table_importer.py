from cdapython import (
    Q, columns, unique_terms, set_default_project_dataset, set_host_url,
    set_table_version, get_host_url, get_default_project_dataset, get_table_version
)
import phenopackets as PPkt
import typing
import pandas as pd
from . import CdaDiseaseFactory
from .cda_importer import CdaImporter
from .. import CdaIndividualFactory


class CdaTableImporter(CdaImporter):


    def __init__(self, query:str=None, query_obj:Q.Q=None):
        """
        :param query: A query for CDA such as 'primary_diagnosis_site = "Lung"'

        The CDA query determines the cohort that will be retrieved from CDA.
        This class then retrieves data for this cohort in form of pandas DataFrames
        and extracts data for phenopacket construction using the data in the tables
        """
        if query is not None and query_obj is None:
            self._query = Q(query)
        elif query_obj is not None and query is None:
            if not isinstance(query_obj, Q.Q):
                raise ValueError(f"query_obj argument must be Q.Q object, but instead was {type(query_obj)}")
            self._query = query_obj
        else:
            raise ValueError("Need to pass either query or query_obj argument but not both")
        self._ppackt_d = {} # key -- patient ID, value: PPkt.Phenopacket

    def get_ga4gh_phenopackets(self) -> typing.List[PPkt.Phenopacket]:
        """

        1.

        """
        individual_factory = CdaIndividualFactory()
        individual_df = self._query.subject.run().get_all().to_dataframe()
        for idx, row in individual_df.iterrows():
            individual_message = individual_factory.from_cancer_data_aggregator(row=row)
            indivudal_id = individual_message.id
            ppackt = PPkt.Phenopacket()
            ppackt.subject.CopyFrom(individual_message)
            self._ppackt_d[indivudal_id] = ppackt
        diagnosis_df = self._query.diagnosis.run().get_all().to_dataframe()
        rsub_df = self._query..researchsubject.run().get_all().to_dataframe()  # view the dataframe
        merged_df = pd.merge(diagnosis_df, rsub_df, left_on='subject_id', right_on='subject_id',
                             suffixes=["_di", "_rs"])
        disease_factory = CdaDiseaseFactory()
        for idx, row in merged_df.iterrows():
            disease_message = disease_factory.from_cancer_data_aggregator(row)
            individual_id = row["subject_id"]
            if individual_id not in self._ppackt_d:
                raise ValueError(f"Attempt to enter unknown individual ID from disease factory: \"{individual_id}\"")
            self._ppackt_d.get(individual_id).diseases.append(disease_message)


        spcimen_df = self._query.specimen.run().get_all().to_dataframe()
        ## get specimen message
        ## copy to corresponding phenopacket
        pass

