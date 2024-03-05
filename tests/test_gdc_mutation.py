import pytest

from oncoexporter.cda import GdcMutationService


@pytest.mark.skip('Requires internet connection')
class TestGdcMutationService:

    @pytest.fixture
    def gdc_mutation_service(self) -> GdcMutationService:
        return GdcMutationService()

    def test_fetch_variants(self, gdc_mutation_service: GdcMutationService):
        # TODO: test more
        subject_id = 'a8b1f6e7-2bcf-460d-b1c6-1792a9801119'
        variants = gdc_mutation_service.fetch_variants(subject_id)
        print(variants)
