from typing import Dict, Generic, TypeVar

from instruct.typing import resolve, make_union

T = TypeVar("T")


def test_simple_resolve():
    class LocalOnlyClass(Generic[T]):
        pass

    assert resolve("str") is str
    assert resolve("str | int") == str | int

    assert resolve(str | int, "Dict[str, int | str]") == (str | int, Dict[str, int | str])
    assert resolve("LocalOnlyClass[T]") == LocalOnlyClass[T]


def test_union():
    assert make_union(int, str, dict[str, int]) == int | str | dict[str, int]
