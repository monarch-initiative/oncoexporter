import pandas as pd
import phenopackets as PPkt
import pytest

from oncoexporter.cda import CdaIndividualFactory


class TestCdaIndividualFactory:

    @pytest.fixture
    def individual_factory(self) -> CdaIndividualFactory:
        return CdaIndividualFactory()

    @pytest.fixture
    def idx(self) -> pd.Index:
        return pd.Index(['subject_id', 'subject_identifier', 'species', 'sex', 'race',
                         'ethnicity', 'days_to_birth', 'subject_associated_project',
                         'vital_status', 'days_to_death', 'cause_of_death']
                        )

    @pytest.fixture
    def alive_row(self, idx: pd.Index) -> pd.Series:
        return pd.Series(
            index=idx,
            data=['CGCI.HTMCP-03-06-02007',
                  "[{'system': 'GDC', 'field_name': 'case.submitter_id', 'value': 'HTMCP-03-06-02007'}]",
                  'Homo sapiens',
                  'female',
                  'black or african american',
                  'not reported',
                  '-15987.0',
                  "['CGCI-HTMCP-CC']",
                  "Alive",
                  "NaN",
                  "None",
                  ],
        )

    @pytest.fixture
    def deceased_row(self, idx: pd.Index) -> pd.Series:
        return pd.Series(
            index=idx,
            data=['CGCI.HTMCP-03-06-02007',
                  "[{'system': 'GDC', 'field_name': 'case.submitter_id', 'value': 'HTMCP-03-06-02007'}]",
                  'Homo sapiens',
                  'female',
                  'black or african american',
                  'not reported',
                  '-15987.0',
                  "['CGCI-HTMCP-CC']",
                  "Dead",
                  "343",
                  "Cancer Related",
                  ],
        )

    def test_id(self, individual_factory: CdaIndividualFactory,
                alive_row: pd.Series):
        ga4gh_indi = individual_factory.to_ga4gh(alive_row)

        assert ga4gh_indi.id == 'CGCI.HTMCP-03-06-02007'

    def test_iso_age(self, individual_factory: CdaIndividualFactory,
                     alive_row: pd.Series):
        """
        CDA provides age as number of days. The conversion to an ISO period depends on actual birth month etc, but
        is approximately correct.
        """
        ga4gh_indi = individual_factory.to_ga4gh(alive_row)

        assert ga4gh_indi.time_at_last_encounter.age.iso8601duration == 'P15987D'

    def test_taxonomy(self, individual_factory: CdaIndividualFactory,
                      alive_row: pd.Series):
        ga4gh_indi = individual_factory.to_ga4gh(alive_row)
        taxonomy = ga4gh_indi.taxonomy

        assert taxonomy is not None
        assert taxonomy.id == "NCBITaxon:9606"
        assert taxonomy.label == "Homo sapiens"

    def test_alive_vital_status(self, individual_factory: CdaIndividualFactory,
                                alive_row: pd.Series):
        ga4gh_indi = individual_factory.to_ga4gh(alive_row)

        vs = ga4gh_indi.vital_status
        assert vs is not None
        assert vs.status == PPkt.VitalStatus.ALIVE

    def test_deceased_vital_status(self, individual_factory: CdaIndividualFactory,
                                   deceased_row: pd.Series):
        ga4gh_indi = individual_factory.to_ga4gh(deceased_row)

        vs = ga4gh_indi.vital_status
        assert vs is not None
        assert vs.status == PPkt.VitalStatus.DECEASED

        assert vs.cause_of_death.id == 'NCIT:C156427'
        assert vs.cause_of_death.label == 'Cancer-Related Death'
        assert vs.survival_time_in_days == 343
