import phenopackets as PPkt

from .op_message import OpMessage


class OpMutation(OpMessage):

    def __init__(self, cda_subject_id=None, primary_site=None, Hugo_Symbol=None, Entrez_Gene_Id=None, NCBI_Build=None, Chromosome=None,
        Start_Position=None, End_Position=None, Reference_Allele=None, Tumor_Seq_Allele1=None, Tumor_Seq_Allele2=None, dbSNP_RS=None,
        dbSNP_Val_Status=None, Match_Norm_Seq_Allele1=None, Match_Norm_Seq_Allele2=None, Tumor_Validation_Allele1=None,
        Tumor_Validation_Allele2=None, Match_Norm_Validation_Allele1=None, Match_Norm_Validation_Allele2=None,
        Mutation_Status=None, HGVSc=None, HGVSp=None, HGVSp_Short=None, Transcript_ID=None, ENSP=None):
            self._gene_symbol = Hugo_Symbol
            self._gene_id = Entrez_Gene_Id
            self._hgvs_c = HGVSc
            self._hgvs_p = HGVSp_Short
            self._transcript_id = Transcript_ID
            self._ensp = ENSP
            self._genome_build = NCBI_Build
            self._chromosome = Chromosome
            self._position = Start_Position
            self._ref = Reference_Allele
            self._alt = Tumor_Seq_Allele2
            self._mutation_status = Mutation_Status

    def to_ga4gh(self) -> PPkt.VariantInterpretation:
        """
        Transform this Variant object into a "variantInterpretation" message of the GA4GH Phenopacket schema
        """
        vdescriptor = PPkt.VariationDescriptor()

        if self._gene_symbol is not None and self._gene_id is not None:
            vdescriptor.gene_context.value_id = f"NCBIGene:{self._gene_id}"
            vdescriptor.gene_context.symbol = self._gene_symbol
        vdescriptor.molecule_context = PPkt.MoleculeContext.genomic
        if self._hgvs_c is not None:
            hgvs_expression = PPkt.Expression()
            hgvs_expression.syntax = "hgvs.c"
            if self._transcript_id is not None:
                hgvs_expression.value = f"{self._transcript_id}:{self._hgvs_c}"
            else:
                hgvs_expression.value = self._hgvs_c
            vdescriptor.expressions.append(hgvs_expression)

        if self._hgvs_p is not None:
            hgvs_expression = PPkt.Expression()
            hgvs_expression.syntax = "hgvs.p"

            if self._ensp is not None:
                hgvs_expression.value = f"{self._ensp}:{self._hgvs_p}"
            else:
                hgvs_expression.value = self._hgvs_p
            vdescriptor.expressions.append(hgvs_expression)

        vcf_record = PPkt.VcfRecord()
        vcf_record.genome_assembly = self._genome_build
        vcf_record.chrom = self._chromosome
        vcf_record.pos = self._position
        vcf_record.ref = self._ref
        vcf_record.alt = self._alt
        vdescriptor.vcf_record.CopyFrom(vcf_record)

        vinterpretation = PPkt.VariantInterpretation()
        vinterpretation.variation_descriptor.CopyFrom(vdescriptor)
        return vinterpretation
