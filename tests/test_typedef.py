from instruct import parse_typedef
from typing import List, Union, AnyStr, Any


def test_parse_typedef():
    assert parse_typedef(Union[int, AnyStr]) == (int, str, bytes,)
    assert parse_typedef(List[int]) == (list,)
    assert parse_typedef(List[Union[int, str]]) == (list,)
    assert parse_typedef(List[Union[int, AnyStr]]) == (list,)
    assert parse_typedef(Union[Any, AnyStr]) == (object, str, bytes,)
    assert parse_typedef(Union[str, int, float]) == (str, int, float)
