import os

import pandas as pd
import phenopackets as PPkt
import pytest

from oncoexporter.cda import CdaMutationFactory

TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'data', 'mutation_excerpt.tsv')


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
    def payload(self) -> pd.Series:
        df = pd.read_csv(TESTDATA_FILENAME, sep="\t")
        # TCGA.TCGA-C5-A1MI -- subject is on the first row
        df_a1mi = df[df['cda_subject_id'].str.contains("TCGA.TCGA-C5-A1MI")]
        assert len(df_a1mi) == 1
        return df_a1mi.iloc[0]

    def test_a1mi(self, mutation_factory: CdaMutationFactory,
                  payload: pd.Series):
        vinterpretation = mutation_factory.to_ga4gh(payload)
        assert vinterpretation is not None
        genome_assembly, ref, alt, pos = get_vcf_ref(vinterpretation=vinterpretation)
        assert genome_assembly == "GRCh38"

    def test_gene(self, mutation_factory: CdaMutationFactory,
                  payload: pd.Series):
        payload['Hugo_Symbol'] = "MFG42"
        payload['Entrez_Gene_Id'] = "42"

        vinterpretation = mutation_factory.to_ga4gh(payload)
        assert vinterpretation is not None
        assert vinterpretation.variation_descriptor is not None

        vdescriptor = vinterpretation.variation_descriptor
        assert vdescriptor is not None
        assert vdescriptor.gene_context is not None

        gcontext = vdescriptor.gene_context
        assert gcontext.value_id == "NCBIGene:42"
        assert gcontext.symbol == "MFG42"

    def test_hgvs(self, mutation_factory: CdaMutationFactory,
                  payload: pd.Series):
        payload['Transcript_ID'] = "ENST00000380152"
        payload['ENSP'] = "ENSP00000369497"
        payload['HGVSc'] = "c.5526T>G"
        payload['HGVSp_Short'] = "p.Tyr1842Ter"

        vinterpretation = mutation_factory.to_ga4gh(payload)

        assert vinterpretation is not None
        assert vinterpretation.variation_descriptor is not None
        assert len(vinterpretation.variation_descriptor.expressions) == 2

        assert vinterpretation.variation_descriptor.expressions[0].syntax == "hgvs.c"
        assert vinterpretation.variation_descriptor.expressions[0].value == "ENST00000380152:c.5526T>G"

        assert vinterpretation.variation_descriptor.expressions[1].syntax == "hgvs.p"
        assert vinterpretation.variation_descriptor.expressions[1].value == "ENSP00000369497:p.Tyr1842Ter"
