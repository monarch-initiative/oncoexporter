import pandas as pd
from unittest import TestCase
import phenopackets as PPkt
import pytest
from src.oncoexporter.model import OpMutation
from src.oncoexporter.cda import CdaMutationFactory
## REMOVE LATER
from google.protobuf.json_format import MessageToJson


def get_column_dict():
    d = {}
    for column_name in [
            'cda_subject_id', 'primary_site', 'Hugo_Symbol', 'Entrez_Gene_Id', 'NCBI_Build', 'Chromosome',
            'Start_Position', 'End_Position', 'Reference_Allele', 'Tumor_Seq_Allele1', 'Tumor_Seq_Allele2', 'dbSNP_RS',
            'dbSNP_Val_Status', 'Match_Norm_Seq_Allele1', 'Match_Norm_Seq_Allele2', 'Tumor_Validation_Allele1',
            'Tumor_Validation_Allele2', 'Match_Norm_Validation_Allele1', 'Match_Norm_Validation_Allele2',
            'Mutation_Status', 'HGVSc', 'HGVSp', 'HGVSp_Short', 'Transcript_ID'
        ]:
        d[column_name] = "n/a"
    return d


class OpMutationTestCase(TestCase):

    def test_gene(self):
        d = get_column_dict()
        d['Hugo_Symbol'] = "MFG42"
        d['Entrez_Gene_Id'] = "42"
        series = pd.Series(d)
        factory = CdaMutationFactory()
        vinterpretation = factory.from_cancer_data_aggregator(series)
        self.assertIsNotNone(vinterpretation)
        self.assertIsNotNone(vinterpretation.variation_descriptor)
        vdescriptor = vinterpretation.variation_descriptor
        self.assertIsNotNone(vdescriptor)
        self.assertIsNotNone(vdescriptor.gene_context)
        gcontext = vdescriptor.gene_context
        self.assertEqual("NCBIGene:42", gcontext.value_id)
        self.assertEqual("MFG42", gcontext.symbol)
        json_string = MessageToJson(vinterpretation)
        print(json_string)



