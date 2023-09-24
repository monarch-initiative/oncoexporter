import phenopackets as PPkt

from .op_message import OpMessage


class OpMutation(OpMessage):

    def __init__(self,cda_subject_id=None, primary_site=None, Hugo_Symbol=None, Entrez_Gene_Id=None, NCBI_Build=None, Chromosome=None,
        Start_Position=None, End_Position=None, Reference_Allele=None, Tumor_Seq_Allele1=None, Tumor_Seq_Allele2=None, dbSNP_RS=None,
        dbSNP_Val_Status=None, Match_Norm_Seq_Allele1=None, Match_Norm_Seq_Allele2=None, Tumor_Validation_Allele1=None,
        Tumor_Validation_Allele2=None, Match_Norm_Validation_Allele1=None, Match_Norm_Validation_Allele2=None,
        Mutation_Status=None, HGVSc=None, HGVSp=None, HGVSp_Short=None, Transcript_ID=None, ENSP=None):
            self._gene_symbol = Hugo_Symbol
            self._gene_id = Entrez_Gene_Id
            self._hgvs_c = HGVSc
            self._hgvs_p = HGVSp
            self._transcript_id = Transcript_ID
            self._ensp = ENSP

    def to_ga4gh(self, acmg=None):
        """
        Transform this Variant object into a "variantInterpretation" message of the GA4GH Phenopacket schema
        """
        vdescriptor = PPkt.VariationDescriptor()

        if self._gene_symbol is not None and self._gene_id is not None:
            vdescriptor.gene_context.value_id = f"NCBIGene:{self._gene_id}"
            vdescriptor.gene_context.symbol = self._gene_symbol

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

        """
        if self._hgnc_id is not None and self._symbol is not None:
            vdescriptor.gene_context.value_id = self._hgnc_id
            vdescriptor.gene_context.symbol = self._symbol
        hgvs_expression = PPkt.Expression()
        if self._hgvs is not None:
            hgvs_expression.syntax = "hgvs.c"
            hgvs_expression.value = self._hgvs
            vdescriptor.expressions.append(hgvs_expression)
        if self._g_hgvs is not None:
            hgvs_expression.syntax = "hgvs.g"
            hgvs_expression.value = self._g_hgvs
            vdescriptor.expressions.append(hgvs_expression)
        vdescriptor.molecule_context = PPkt.MoleculeContext.genomic

        vinterpretation = PPkt.VariantInterpretation()
        if acmg is not None:
            if acmg.lower() == 'benign':
                vinterpretation.acmgPathogenicityClassification = PPkt.AcmgPathogenicityClassification.BENIGN
            elif acmg.lower == 'likely benign' or acmg.lower() == 'likely_benign':
                vinterpretation.acmgPathogenicityClassification = PPkt.AcmgPathogenicityClassification.LIKELY_BENIGN
            elif acmg.lower == 'uncertain significance' or acmg.lower() == 'uncertain_significance':
                vinterpretation.acmgPathogenicityClassification = PPkt.AcmgPathogenicityClassification.UNCERTAIN_SIGNIFICANCE
            elif acmg.lower == 'likely pathogenic' or acmg.lower() == 'likely_pathogenic':
                vinterpretation.acmgPathogenicityClassification = PPkt.AcmgPathogenicityClassification.LIKELY_PATHOGENIC
            elif acmg.lower == 'pathogenic' or acmg.lower() == 'pathogenic':
                vinterpretation.acmgPathogenicityClassification = PPkt.AcmgPathogenicityClassification.PATHOGENIC
            else:
                print(f"Warning- did not recognize ACMG category {acmg}")
        vcf_record = PPkt.VcfRecord()
        vcf_record.genome_assembly = self._assembly
        vcf_record.chrom = self._chr
        vcf_record.pos = self._position
        vcf_record.ref = self._ref
        vcf_record.alt = self._alt
        vdescriptor.vcf_record.CopyFrom(vcf_record)
        
        """
        vinterpretation = PPkt.VariantInterpretation()
        vinterpretation.variation_descriptor.CopyFrom(vdescriptor)
        return vinterpretation
