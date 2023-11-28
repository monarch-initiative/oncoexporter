import pandas as pd
from .cda_factory import CdaFactory
from ..model.op_mutation import OpMutation

class CdaMutationFactory(CdaFactory):
    """
    cda_subject_id
    primary_site
    Hugo_Symbol
    Entrez_Gene_Id
    NCBI_Build
    Chromosome
    Start_Position
    End_Position
    Reference_Allele
    Tumor_Seq_Allele1
    Tumor_Seq_Allele2
    dbSNP_RS
    dbSNP_Val_Status
    Match_Norm_Seq_Allele1
    Match_Norm_Seq_Allele2
    Tumor_Validation_Allele1
    Tumor_Validation_Allele2
    Match_Norm_Validation_Allele1
    Match_Norm_Validation_Allele2
    Mutation_Status
    HGVSc
    HGVSp
    HGVSp_Short
    Transcript_ID



    """

    def __init__(self):
        self._column_names = [
            'cda_subject_id', 'primary_site', 'Hugo_Symbol', 'Entrez_Gene_Id', 'NCBI_Build', 'Chromosome',
            'Start_Position', 'End_Position', 'Reference_Allele', 'Tumor_Seq_Allele1', 'Tumor_Seq_Allele2', 'dbSNP_RS',
            'dbSNP_Val_Status', 'Match_Norm_Seq_Allele1', 'Match_Norm_Seq_Allele2', 'Tumor_Validation_Allele1',
            'Tumor_Validation_Allele2', 'Match_Norm_Validation_Allele1', 'Match_Norm_Validation_Allele2',
            'Mutation_Status', 'HGVSc', 'HGVSp', 'HGVSp_Short', 'Transcript_ID', 'ENSP'
        ]

    def to_ga4gh_individual(self, row):
        """
        convert a row from the CDA subject table into an Individual message (GA4GH Phenopacket Schema)
        The row is a pd.core.series.Series and contains the columns
        ['diagnosis_id', 'diagnosis_identifier', 'primary_diagnosis',
       'age_at_diagnosis', 'morphology', 'stage', 'grade',
       'method_of_diagnosis', 'subject_id', 'researchsubject_id']
       :param row: a row from the CDA subject table
        """
        if not isinstance(row, pd.core.series.Series):
            raise ValueError(f"Invalid argument. Expected pandas series but got {type(row)}")

        cda_subject_id, primary_site, Hugo_Symbol, Entrez_Gene_Id, NCBI_Build, Chromosome, \
        Start_Position, End_Position, Reference_Allele, Tumor_Seq_Allele1, Tumor_Seq_Allele2, dbSNP_RS, \
        dbSNP_Val_Status, Match_Norm_Seq_Allele1, Match_Norm_Seq_Allele2, Tumor_Validation_Allele1, \
        Tumor_Validation_Allele2, Match_Norm_Validation_Allele1, Match_Norm_Validation_Allele2, \
        Mutation_Status, HGVSc, HGVSp, HGVSp_Short, Transcript_ID, ENSP \
            = self.get_items_from_row(row, self._column_names)

        mutation = OpMutation(Hugo_Symbol=Hugo_Symbol, Entrez_Gene_Id=Entrez_Gene_Id,
                              HGVSc=HGVSc, HGVSp=HGVSp, Transcript_ID=Transcript_ID, ENSP=ENSP)
        return mutation.to_ga4gh()

