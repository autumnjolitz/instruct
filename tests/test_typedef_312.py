from instruct.typedef import parse_typedef

import pytest


def test_parse_typealiastype():
    type i = int
    assert parse_typedef(i) is int
    type b = str | int
    assert {*parse_typedef(b)} == {str, int}
    type c = i | b
    assert {*parse_typedef(c)} == {str, int}

    type d = dict[str, d]

    with pytest.raises(RecursionError):
        parse_typedef(d)
