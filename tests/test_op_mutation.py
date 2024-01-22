import os

import pandas as pd
import phenopackets as PPkt
import pytest

from oncoexporter.cda import CdaMutationFactory

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


class TestOpMutation:

    @pytest.fixture
    def mutation_factory(self) -> CdaMutationFactory:
        return CdaMutationFactory()

    @pytest.fixture
    def a1mi(self) -> pd.Series:
        df = pd.read_csv(TESTDATA_FILENAME, sep="\t")
        # TCGA.TCGA-C5-A1MI -- subject is on the first row
        df_a1mi = df[df['cda_subject_id'].str.contains("TCGA.TCGA-C5-A1MI")]
        assert len(df_a1mi) == 1
        return df_a1mi.iloc[0]

    def test_a1mi(self, mutation_factory: CdaMutationFactory,
                  a1mi: pd.Series):
        vinterpretation = mutation_factory.to_ga4gh(a1mi)
        assert vinterpretation is not None
        genome_assembly, ref, alt, pos = get_vcf_ref(vinterpretation=vinterpretation)
        assert genome_assembly == "GRCh38"

    def test_gene(self, mutation_factory: CdaMutationFactory):
        d = get_column_dict()
        d['Hugo_Symbol'] = "MFG42"
        d['Entrez_Gene_Id'] = "42"
        series = pd.Series(d)

        vinterpretation = mutation_factory.to_ga4gh(series)
        assert vinterpretation is not None
        assert vinterpretation.variation_descriptor is not None

        vdescriptor = vinterpretation.variation_descriptor
        assert vdescriptor is not None
        assert vdescriptor.gene_context is not None

        gcontext = vdescriptor.gene_context
        assert gcontext.value_id == "NCBIGene:42"
        assert gcontext.symbol == "MFG42"

    def test_hgvs(self, mutation_factory: CdaMutationFactory):
        d = get_column_dict()
        d['Transcript_ID'] = "ENST00000380152"
        d['ENSP'] = "ENSP00000369497"
        d['HGVSc'] = "c.5526T>G"
        d['HGVSp'] = "p.Tyr1842Ter"
        series = pd.Series(d)

        vinterpretation = mutation_factory.to_ga4gh(series)

        assert vinterpretation is not None
        assert vinterpretation.variation_descriptor is not None
        assert len(vinterpretation.variation_descriptor.expressions) == 2

        assert vinterpretation.variation_descriptor.expressions[0].syntax == "hgvs.c"
        assert vinterpretation.variation_descriptor.expressions[0].value == "ENST00000380152:c.5526T>G"

        assert vinterpretation.variation_descriptor.expressions[1].syntax == "hgvs.p"
        assert vinterpretation.variation_descriptor.expressions[1].value == "ENSP00000369497:p.Tyr1842Ter"
