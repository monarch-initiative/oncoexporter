import json
import logging
import typing
import pandas as pd
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
            timeout=30,
    ):
        self._logger = logging.getLogger(__name__)
        self._variants_url = 'https://api.gdc.cancer.gov/ssms'
        self._survival_url = 'https://api.gdc.cancer.gov/analysis/survival'
        self._cases = 'https://api.gdc.cancer.gov/cases'
        self._page_size = page_size
        self._page = page
        self._timeout = timeout
        self._variant_fields = ','.join((
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
            "consequence.transcript.aa_change",
            "consequence.transcript.gene.gene_id",
            "consequence.transcript.gene.symbol",
            "consequence.transcript.transcript_id",
            "consequence.transcript.annotation.hgvsc",
        ))
        self._case_fields = ','.join((
            "demographic.vital_status",
        ))
        self._ensembl_tx2prot = pd.read_csv("Homo_sapiens.GRCh38.112.ena.tsv", sep="\t") # from https://ftp.ensembl.org/pub/current_tsv/homo_sapiens/
        self._tx_to_prot_dict = dict(zip(self._ensembl_tx2prot.transcript_stable_id, self._ensembl_tx2prot.protein_stable_id))


    def _fetch_data_from_gdc(self, url: str, subject_id: str, fields: typing.List[str]=None) -> typing.Any:
        params = self._prepare_query_params(subject_id, fields)
        response = requests.get(url, params=params, timeout=self._timeout)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise ValueError(f'Failed to fetch data from {url} due to {response.status_code}: {response.reason}')

    def _prepare_query_params(self, subject_id: str, fields: typing.List[str]=None) -> typing.Dict:
        filters = {
            "op": "in",
            "content": {
                "field": "cases.submitter_id",
                "value": [subject_id]
            }
        }
        
        # To avoid this error: 
        # requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
        headers = {
            'User-Agent': 'My User Agent 1.0',
        }
        
        return {
            "headers": headers,
            "fields": fields,
            "filters": json.dumps(filters),
            "format": "JSON",
            "size": self._page_size,
        }

    def fetch_variants(self, subject_id: str) -> typing.Sequence[pp.VariantInterpretation]:
        variants = self._fetch_data_from_gdc(self._variants_url, subject_id, self._variant_fields)

        mutations = variants.get("data", {}).get("hits", [])

        mutation_details = []
        for mutation in mutations:
            vi = self._map_mutation_to_variant_interpretation(mutation)
            mutation_details.append(vi)

        return mutation_details

    def fetch_vital_status(self, subject_id: str) -> pp.VitalStatus:
        survival_data = self._fetch_data_from_gdc(self._survival_url, subject_id)
        vital_status_data = self._fetch_data_from_gdc(self._cases, subject_id, self._case_fields)

        survival_time = None
        vital_status = None

        survival_results = survival_data.get("results", [])
        if survival_results:
            donors = survival_results[0].get("donors", [])
            if donors:
                survival_time = donors[0].get("time")

        vital_status_hits = vital_status_data.get("data", {}).get("hits", [])
        if vital_status_hits:
            demographic = vital_status_hits[0].get("demographic", {})
            vital_status = demographic.get("vital_status")

        vital_status_obj = pp.VitalStatus()
        vital_status_obj.survival_time_in_days = int(survival_time) if survival_time is not None else 0
        if vital_status == "Dead":
            vital_status_obj.status = pp.VitalStatus.Status.DECEASED
        elif vital_status == "Alive":
            vital_status_obj.status = pp.VitalStatus.Status.ALIVE
        else:
            vital_status_obj.status = pp.VitalStatus.Status.UNKNOWN_STATUS

        return vital_status_obj

    def _map_mutation_to_variant_interpretation(self, mutation) -> pp.VariantInterpretation:
        
        # TODO: 't_depth', 't_ref_count', 't_alt_count', 'n_depth', 'n_ref_count', 'n_alt_count'
        # TODO: mutation status
        # "gene_aa_change": ["KRAS G12D"]
        
        vd = pp.VariationDescriptor()
        vd.id = mutation['id']

        vcf_record = self._parse_vcf_record(mutation)
        if vcf_record is not None:
            vd.vcf_record.CopyFrom(vcf_record)

        for csq in mutation['consequence']:
            expression_list = self._map_consequence_to_expression(csq)# GdcMutationService._map_consequence_to_expression(csq)
            gene_descriptor = GdcMutationService._map_consequence_to_gene_descriptor(csq)
            
            if expression_list is not None:
                vd.expressions.extend(expression_list)
                
            if gene_descriptor is not None:
                vd.gene_context.CopyFrom(gene_descriptor)

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

    #@staticmethod # [pp.Expression]
    def _map_consequence_to_expression(self, csq) -> typing.Optional[list]:
                                                                    
        tx = csq['transcript']

        expression_c = pp.Expression()
        expression_c.syntax = 'hgvs.c'
        tx_id = tx['transcript_id']
        ann = tx['annotation']['hgvsc']
        expression_c.value = f'{tx_id}:{ann}'
        
        expression_p = pp.Expression()
        prot_id = None
        if tx_id in self._tx_to_prot_dict:
            prot_id = self._tx_to_prot_dict[tx_id]
        
        aa_change = None
        if 'aa_change' in tx:
            aa_change = 'p.'+tx['aa_change']
        
        if aa_change is not None and prot_id is not None:
            expression_p.syntax = 'hgvs.p'
            expression_p.value = f'{prot_id}:{aa_change}'
            
        
        '''
        Phenopacket:
        "expressions": [
                  {
                    "syntax": "hgvs.c",
                    "value": "ENST00000373125:c.55C>T"
                  },
        
        GDC:
        curl 'https://api.gdc.cancer.gov/ssms/edd1ae2c-3ca9-52bd-a124-b09ed304fcc2?pretty=true&expand=consequence.transcript'
        {
            "data": {
                "start_position": 25245350,
                "gene_aa_change": [
                    "KRAS G12D"
                ],
            "consequence": [
            {
                "transcript": {
                    "transcript_id": "ENST00000556131",
                    "aa_end": 12,
                    "consequence_type": "missense_variant",
                    "aa_start": 12,
                    "is_canonical": false,
                    "aa_change": "G12D",
                    "ref_seq_accession": ""
            }
        },
        '''
        return ([expression_c,expression_p])
    @staticmethod
    def _map_consequence_to_gene_descriptor(csq) -> (typing.Optional[pp.GeneDescriptor]):
        
        tx = csq['transcript']
        
        gene_context = pp.GeneDescriptor()
        gene_context.value_id = tx['gene']['gene_id']
        gene_context.symbol = tx['gene']['symbol']
        
        return(gene_context)