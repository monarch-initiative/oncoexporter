import logging
import typing

import pandas as pd
import phenopackets as pp

from .cda_factory import CdaFactory


class CdaMutationFactory(CdaFactory):
    """
    https://cda.readthedocs.io/en/latest/Schema/fields_mutation/
    153 fields - need to decide which to keep
    'cda_subject_id',
    'Entrez_Gene_Id',
    'Hugo_Symbol',
    'NCBI_Build',
    'Chromosome',
    'Start_Position',
    'Reference_Allele',
    'Tumor_Seq_Allele2',
    'dbSNP_RS',
    'Transcript_ID',
    'HGVSc',
    'ENSP',
    'HGVSp_Short',
    'Mutation_Status',
    't_depth',
    't_ref_count',
    't_alt_count',
    'n_depth',
    'n_ref_count',
    'n_alt_count',
    """

    def __init__(self):
        self._column_names = [
            'Entrez_Gene_Id', 'Hugo_Symbol',
            'NCBI_Build', 'Chromosome', 'Start_Position', 'Reference_Allele', 'Tumor_Seq_Allele2',
            'dbSNP_RS',
            'Transcript_ID', 'HGVSc', 'ENSP', 'HGVSp_Short',
            'Mutation_Status',
            't_depth', 't_ref_count', 't_alt_count',
            'n_depth', 'n_ref_count', 'n_alt_count'
        ]
        self._logger = logging.getLogger(__name__)

    def to_ga4gh(self, row: pd.Series) -> pp.VariantInterpretation:
        """
        Convert a row from the CDA mutation table
        into a VariantInterpretation message (GA4GH Phenopacket Schema).

       :param row: a :class:`pd.Series` with the row of the CDA mutation table.
        """
        if not isinstance(row, pd.Series):
            raise ValueError(f"Invalid argument. Expected pandas series but got {type(row)}")

        if any(field not in row for field in self._column_names):
            keys = set(row.index)
            missing = keys.difference(self._column_names)
            raise ValueError(f'Missing field(s): {missing}')


        vdescriptor = pp.VariationDescriptor()

        vdescriptor.id = self._generate_id(row)

        # Gene context
        if row['Hugo_Symbol'] is not None and row['Entrez_Gene_Id'] is not None:
            vdescriptor.gene_context.value_id = f"NCBIGene:{row['Entrez_Gene_Id']}"
            vdescriptor.gene_context.symbol = row['Hugo_Symbol']

        # We may consider including an HGVS c expression for ALL transcripts,
        # using the `all_effects` field that looks like this:
        # SPRY3,missense_variant,p.G118A,ENST00000302805,NM_005840.2,c.353G>C,MODERATE,YES,deleterious(0),benign(0.001),1;SPRY3,missense_variant,p.G118A,ENST00000675360,NM_001304990.1,c.353G>C,MODERATE,,deleterious(0),benign(0.001),1
        if row['Transcript_ID'] is not None and row['HGVSc'] is not None:
            hgvs_expression = pp.Expression()
            hgvs_expression.syntax = "hgvs.c"
            hgvs_expression.value = f"{row['Transcript_ID']}:{row['HGVSc']}"
            vdescriptor.expressions.append(hgvs_expression)

        if row['ENSP'] is not None and row['HGVSp_Short'] is not None:
            hgvs_expression = pp.Expression()
            hgvs_expression.syntax = "hgvs.p"
            hgvs_expression.value = f"{row['ENSP']}:{row['HGVSp_Short']}"
            vdescriptor.expressions.append(hgvs_expression)

        # TODO: consider adding HGVS.g

        vcf_record = self._create_vcf_record(row)
        if vcf_record is not None:
            vdescriptor.vcf_record.CopyFrom(vcf_record)

        # Tumor/normal depths
        for name in ('t_depth', 't_ref_count', 't_alt_count',
                     'n_depth', 'n_ref_count', 'n_alt_count'):
            val = row[name]
            ext = pp.Extension()
            ext.name = name
            # We expect an `int` or `None`.
            ext.value = str(val)
            vdescriptor.extensions.append(ext)

        # Mutation status
        ms = row['Mutation_Status']
        if ms is not None and len(ms) > 1:
            ext = pp.Extension()
            ext.name = 'Mutation_Status'
            ext.value = ms
            vdescriptor.extensions.append(ext)

        vdescriptor.molecule_context = pp.MoleculeContext.genomic

        vinterpretation = pp.VariantInterpretation()
        vinterpretation.variation_descriptor.CopyFrom(vdescriptor)
        return vinterpretation

    def _create_vcf_record(self, row: pd.Series) -> typing.Optional[pp.VcfRecord]:
        ref = row['Reference_Allele']
        alt = row['Tumor_Seq_Allele2']
        if ref == '-' or alt == '-':
            self._logger.debug(
                'Cannot create a VCF record due to missing bases in the Reference_Allele/Tumor_Seq_Allele2 alleles: %s',
                row)
            return None

        vcf_record = pp.VcfRecord()
        vcf_record.genome_assembly = row['NCBI_Build']
        vcf_record.chrom = row['Chromosome']
        vcf_record.id = row['dbSNP_RS']
        vcf_record.pos = row['Start_Position']
        vcf_record.ref = ref
        vcf_record.alt = alt
        return vcf_record

    @staticmethod
    def _generate_id(row: pd.Series) -> str:
        return str(hash(''.join(str(x) for x in row.values)))

