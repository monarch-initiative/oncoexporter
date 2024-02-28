import typing

import pytest

from oncoexporter.cda import CdaFactory


@pytest.mark.parametrize('val, expected',
                         [
                             # Ints are OK.
                             (0,        'P0D'),
                             (-1,       'P1D'),
                             (1,        'P1D'),

                             # Finite floats are OK.
                             (3.14,     'P3D'),
                             (-12.71,   'P13D'),
                             ('nan',    None),
                             ('inf',    None),
                             ('-inf',   None),

                             # Anything that can be parsed into finite floats and ints is OK.
                             ('-1234',  'P1234D'),
                             ('0',      'P0D'),
                             ('-0',     'P0D'),
                             ('1',      'P1D'),
                             ('1000',   'P1000D'),
                             ('3.14',   'P3D'),
                             ('-12.71', 'P13D'),
                         ])
def test_days_to_iso(val: typing.Union[str, int], expected: typing.Optional[str]):
    actual = CdaFactory.days_to_iso(val)

    assert actual == expected


def test_days_to_iso_raises():
    with pytest.raises(ValueError) as e:
        CdaFactory.days_to_iso(True)

    assert e.value.args[0] == "days argument must be an int or a str but was <class 'bool'>"
