import typing

from .cda_table_importer import CdaTableImporter
from .cda_disease_factory import CdaDiseaseFactory
from .mapper import OpDiagnosisMapper


def configure_cda_table_importer(
        cache_dir: typing.Optional[str] = None,
        use_cache: bool = False
        #page_size: int = 10000,
) -> CdaTableImporter:
    disease_stage_mapper = OpDiagnosisMapper.multitissue_mapper()
    disease_factory = CdaDiseaseFactory(disease_stage_mapper)
    return CdaTableImporter(disease_factory,
                            cache_dir=cache_dir,
                            use_cache=use_cache)
                            #page_size=page_size)
