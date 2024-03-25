import json
import logging
import typing

import phenopackets as pp
import requests


class GdcMutationService:
    """
    `GdcMutationService` queries Genomic Data Commons REST endpoint to fetch variants for a CDA subject.
    """

    def __init__(
            self,
            page_size=100,
            page=1,
            timeout=10,
    ):
        self._logger = logging.getLogger(__name__)
        self._url = 'https://api.gdc.cancer.gov/ssms'
        self._page_size = page_size
        self._page = page
        self._timeout = timeout
        self._fields = ','.join((
            # "mutation_type",
            # "mutation_subtype",
            "ncbi_build",
            "chromosome",
            "start_position",
            # "end_position",
            "reference_allele",
            "tumor_allele",
            # "genomic_dna_change",
            # "end_position",
            # "gene_aa_change",
            "consequence.transcript.gene.gene_id",
            "consequence.transcript.gene.symbol",
            "consequence.transcript.transcript_id",
            "consequence.transcript.annotation.hgvsc",
        ))

    def fetch_variants(self, subject_id: str) -> typing.Sequence[pp.VariantInterpretation]:
        params = self._prepare_query_params(subject_id)

        response = requests.get(self._url, params=params, timeout=self._timeout)

        if response.status_code == 200:
            data = response.json()
            mutations = data.get("data", {}).get("hits", [])

            mutation_details = []
            for mutation in mutations:
                vi = self._map_mutation_to_variant_interpretation(mutation)
                mutation_details.append(vi)

            return mutation_details
        else:
            raise ValueError(f'Failed to fetch data due to {response.status_code}: {response.reason}')

    def _prepare_query_params(self, subject_id: str):
        filters = {
            "op": "in",
            "content": {
                "field": "cases.submitter_id",
                "value": [subject_id]
            }
        }
        return {
            "fields": self._fields,
            "filters": json.dumps(filters),
            "format": "JSON",
            "size": self._page_size,
            "from": (self._page - 1) * self._page_size + 1,
        }

    def _map_mutation_to_variant_interpretation(self, mutation) -> typing.Optional[pp.VariantInterpretation]:
        vcf_record = self._parse_vcf_record(mutation)

        vd = pp.VariationDescriptor()
        vd.id = mutation['id']
        if vcf_record is not None:
            vd.vcf_record.CopyFrom(vcf_record)

        # TODO: set gene
        # TODO: 't_depth', 't_ref_count', 't_alt_count', 'n_depth', 'n_ref_count', 'n_alt_count'
        # TODO: mutation status

        for csq in mutation['consequence']:
            expression = GdcMutationService._map_consequence_to_expression(csq)
            if expression is not None:
                vd.expressions.append(expression)

        vd.molecule_context = pp.MoleculeContext.genomic

        vi = pp.VariantInterpretation()
        vi.variation_descriptor.CopyFrom(vd)
        return vi

    def _parse_vcf_record(self, mutation) -> typing.Optional[pp.VcfRecord]:
        if mutation['reference_allele'] == '-' or mutation['tumor_allele'] == '-':
            self._logger.debug(
                'Cannot create a VCF record due to missing bases in the reference_allele/tumor_allele alleles: %s',
                mutation)
            return None

        vcf_record = pp.VcfRecord()

        vcf_record.genome_assembly = mutation['ncbi_build']
        vcf_record.chrom = mutation['chromosome']
        vcf_record.id = mutation['id']
        vcf_record.pos = mutation['start_position']
        vcf_record.ref = mutation['reference_allele']
        vcf_record.alt = mutation['tumor_allele']

        return vcf_record

    @staticmethod
    def _map_consequence_to_expression(csq) -> typing.Optional[pp.Expression]:
        tx = csq['transcript']

        expression = pp.Expression()
        expression.syntax = 'hgvs.c'
        tx_id = tx['transcript_id']
        ann = tx['annotation']['hgvsc']
        expression.value = f'{tx_id}:{ann}'

        return expression
