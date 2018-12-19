import pytest

from instruct.typedef import parse_typedef, make_custom_typecheck
from typing import List, Union, AnyStr, Any, Optional, Generic, TypeVar, Tuple

NoneType = type(None)


def test_parse_typedef():

    custom_type = make_custom_typecheck(lambda val: val == 3)
    assert isinstance(3, custom_type)
    assert not isinstance('a', custom_type)

    assert parse_typedef(Union[int, AnyStr]) == (int, str, bytes,)

    ListOfInts = parse_typedef(List[int])
    assert isinstance([1, 2, 3], ListOfInts)
    assert not isinstance([1, 2, 3.1], ListOfInts)
    ListOfIntsOrStrs = parse_typedef(List[Union[int, str]])
    assert isinstance(['a', 1, 2], ListOfIntsOrStrs)
    assert not isinstance(['a', 1, 2, {}], ListOfIntsOrStrs)
    ListOfIntsOrAnyStr = parse_typedef(List[Union[int, AnyStr]])
    assert isinstance(['a', b'b', 1], ListOfIntsOrAnyStr)
    assert not isinstance(['a', b'b', 1, [1]], ListOfIntsOrAnyStr)
    Anything = parse_typedef(Union[Any, AnyStr])
    assert isinstance({}, Anything)
    assert isinstance(b'a', Anything)
    assert isinstance(type, Anything)
    assert parse_typedef(Union[str, int, float]) == (str, int, float)
    assert parse_typedef(Optional[str]) == (str, NoneType)
    assert isinstance([['a', 1]], parse_typedef(List[List[Union[int, str]]]))
    assert isinstance([('a', 1), ('b', 2)], parse_typedef(List[Tuple[int, str]]))
    assert not isinstance([['a', 1]], parse_typedef(List[Tuple[int, str]]))


def test_custom_name():
    types = parse_typedef(Union[List[str], List[float]])
    assert not frozenset(x.__name__ for x in types) - \
        frozenset(['List[str]', 'List[float]'])


def test_generic():
    T = TypeVar('T')

    class Item(Generic[T]):
        pass

    assert parse_typedef(Item) is Item
    # To do: support generics?
    with pytest.raises(NotImplementedError):
        parse_typedef(Item[int])
