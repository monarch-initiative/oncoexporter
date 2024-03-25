import pytest

from oncoexporter.cda import GdcMutationService


# @pytest.mark.skip('Requires internet connection')
class TestGdcMutationService:

    @pytest.fixture
    def gdc_mutation_service(self) -> GdcMutationService:
        return GdcMutationService()

    def test_fetch_variants(self, gdc_mutation_service: GdcMutationService):
        # TODO: test more
        submitter_id = 'TCGA-DX-A3UA'
        variants = gdc_mutation_service.fetch_variants(submitter_id)
        assert variants
