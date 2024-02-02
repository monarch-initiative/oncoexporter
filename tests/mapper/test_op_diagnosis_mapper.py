import pandas as pd
import pytest

from oncoexporter.cda.mapper.op_diagnosis_mapper import OpDiagnosisMapper


class TestOpDiagnosisMapper:

    @pytest.fixture
    def mapper(self) -> OpDiagnosisMapper:
        return OpDiagnosisMapper.default_mapper()

    # Tests conceived by Justin in `test_op_diagnosis_mapper` and moved here to be closer to the `OpDiagnosisMapper`.
    @pytest.mark.parametrize(
        'primary_diagnosis, primary_diagnosis_condition, primary_diagnosis_site, expected_id, expected_label',
        [
            ('', '', 'Lung', 'NCIT:C3200', 'Lung Neoplasm'),
            ('Adenocarcinoma', 'Lung Adenocarcinoma', 'Lung', 'NCIT:C3512', 'Lung Adenocarcinoma'),
            ('Acantholytic squamous cell carcinoma', 'Lung Squamous Cell Carcinoma', 'Lung', 'NCIT:C3493', 'Lung Squamous Cell Carcinoma'),
            ('Adenocarcinoma, NOS', 'Lung Adenocarcinoma', 'Lung', 'NCIT:C3512', 'Lung Adenocarcinoma'),
            ('Squamous Cell Carcinoma', 'Lung Squamous Cell Carcinoma', 'Lung', 'NCIT:C3493', 'Lung Squamous Cell Carcinoma'),
            ('cell adenocarcinoma, NOS', 'Lung Adenocarcinoma', 'Lung', 'NCIT:C45516', 'Lung Adenocarcinoma'),
            ('Squamous Cell Carcinoma', 'Lung Adenocarcinoma', 'Lung', 'NCIT:C9133', 'Lung Adenosquamous Carcinoma'),
            ('Adenosquamous carcinoma', 'Lung Adenocarcinoma', 'Lung', 'NCIT:C9133', 'Lung Adenosquamous Carcinoma'),
        ])
    def test_get_ontology_term(self, mapper: OpDiagnosisMapper,
                               primary_diagnosis: str, primary_diagnosis_condition: str, primary_diagnosis_site: str,
                               expected_id: str, expected_label: str):
        row = pd.Series({
            'primary_diagnosis': primary_diagnosis,
            'primary_diagnosis_condition': primary_diagnosis_condition,
            'primary_diagnosis_site': primary_diagnosis_site,
        })

        term = mapper.get_ontology_term(row)

        assert term is not None
        assert term.id == expected_id
        assert term.label == expected_label
