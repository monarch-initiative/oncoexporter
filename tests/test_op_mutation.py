import pandas as pd
from unittest import TestCase
import phenopackets as PPkt
import os
from oncoexporter.model import OpMutation
from oncoexporter.cda import CdaMutationFactory
## REMOVE LATER
from google.protobuf.json_format import MessageToJson


TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'data', 'mutation_excerpt.tsv')


def get_column_dict():
    d = {}
    for column_name in [
            'cda_subject_id', 'primary_site', 'Hugo_Symbol', 'Entrez_Gene_Id', 'NCBI_Build', 'Chromosome',
            'Start_Position', 'End_Position', 'Reference_Allele', 'Tumor_Seq_Allele1', 'Tumor_Seq_Allele2', 'dbSNP_RS',
            'dbSNP_Val_Status', 'Match_Norm_Seq_Allele1', 'Match_Norm_Seq_Allele2', 'Tumor_Validation_Allele1',
            'Tumor_Validation_Allele2', 'Match_Norm_Validation_Allele1', 'Match_Norm_Validation_Allele2',
            'Mutation_Status', 'HGVSc', 'HGVSp', 'HGVSp_Short', 'Transcript_ID', 'ENSP'
        ]:
        d[column_name] = "n/a"
    return d


def get_vcf_ref(vinterpretation):
    if not isinstance(vinterpretation, PPkt.VariantInterpretation):
        raise ValueError(F"expected GA4GH VariantInterpretation but got {type(vinterpretation)}")
    if vinterpretation.variation_descriptor is None:
        raise ValueError("Could not find variation_descriptor")
    vdesc = vinterpretation.variation_descriptor
    if vdesc.vcf_record is None:
        raise ValueError("Could not find variation_descriptor")
    vcf = vdesc.vcf_record
    genome_assembly = vcf.genome_assembly
    ref = vcf.ref
    alt = vcf.alt
    pos = vcf.pos
    return genome_assembly, ref, alt, pos


class OpMutationTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        df = pd.read_csv(TESTDATA_FILENAME, sep="\t")
        # TCGA.TCGA-C5-A1MI -- subject is on the first row
        df_a1mi = df[df['cda_subject_id'].str.contains("TCGA.TCGA-C5-A1MI")]
        assert len(df_a1mi) == 1
        cls._a1mi = df_a1mi.iloc[0]



    def test_a1mi(self):
        factory = CdaMutationFactory()
        vinterpretation = factory.to_ga4gh(self._a1mi)
        self.assertIsNotNone(vinterpretation)
        genome_assembly, ref, alt, pos = get_vcf_ref(vinterpretation=vinterpretation)
        self.assertEqual("hg38", genome_assembly)



    def test_gene(self):
        d = get_column_dict()
        d['Hugo_Symbol'] = "MFG42"
        d['Entrez_Gene_Id'] = "42"
        series = pd.Series(d)
        factory = CdaMutationFactory()
        vinterpretation = factory.to_ga4gh(series)
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

    def test_hgvs(self):
        d = get_column_dict()
        d['Transcript_ID'] = "ENST00000380152"
        d['ENSP'] = "ENSP00000369497"
        d['HGVSc'] = "c.5526T>G"
        d['HGVSp'] = "p.Tyr1842Ter"
        series = pd.Series(d)
        factory = CdaMutationFactory()
        vinterpretation = factory.to_ga4gh(series)

        self.assertIsNotNone(vinterpretation)
        self.assertIsNotNone(vinterpretation.variation_descriptor)
        self.assertEqual(2, len(vinterpretation.variation_descriptor.expressions))

        self.assertEqual("hgvs.c", vinterpretation.variation_descriptor.expressions[0].syntax)
        self.assertEqual("ENST00000380152:c.5526T>G", vinterpretation.variation_descriptor.expressions[0].value)

        self.assertEqual("hgvs.p", vinterpretation.variation_descriptor.expressions[1].syntax)
        self.assertEqual("ENSP00000369497:p.Tyr1842Ter", vinterpretation.variation_descriptor.expressions[1].value)







