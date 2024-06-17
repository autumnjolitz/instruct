import pytest
from enum import Enum
from instruct.typedef import (
    parse_typedef,
    make_custom_typecheck,
    has_collect_class,
    find_class_in_definition,
    is_typing_definition,
    get_args,
    issubormetasubclass,
)
from instruct import Base, AtomicMeta
from typing import List, Union, AnyStr, Any, Optional, Generic, TypeVar, Tuple, FrozenSet, Set, Dict

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

NoneType = type(None)


def test_parse_typedef():
    custom_type = make_custom_typecheck(lambda val: val == 3)
    assert isinstance(3, custom_type)
    assert not isinstance("a", custom_type)

    assert parse_typedef(Union[int, AnyStr]) == (int, str, bytes)

    ListOfInts = parse_typedef(List[int])
    assert isinstance([1, 2, 3], ListOfInts)
    assert not isinstance([1, 2, 3.1], ListOfInts)
    ListOfIntsOrStrs = parse_typedef(List[Union[int, str]])
    assert isinstance(["a", 1, 2], ListOfIntsOrStrs)
    assert not isinstance(["a", 1, 2, {}], ListOfIntsOrStrs)
    ListOfIntsOrAnyStr = parse_typedef(List[Union[int, AnyStr]])
    assert isinstance(["a", b"b", 1], ListOfIntsOrAnyStr)
    assert not isinstance(["a", b"b", 1, [1]], ListOfIntsOrAnyStr)
    Anything = parse_typedef(Union[Any, AnyStr])
    assert isinstance({}, Anything)
    assert isinstance(b"a", Anything)
    assert isinstance(type, Anything)
    assert parse_typedef(Union[str, int, float]) == (str, int, float)
    assert parse_typedef(Optional[str]) == (str, NoneType)
    assert isinstance([["a", 1]], parse_typedef(List[List[Union[int, str]]]))
    assert isinstance([("a", 1), ("b", 2)], parse_typedef(List[Tuple[str, int]]))
    assert not isinstance([["a", 1]], parse_typedef(List[Tuple[int, str]]))
    new_type = parse_typedef((List[int], List[List[dict]]))
    assert isinstance([1, 2, 3], new_type)
    assert isinstance([[{}]], new_type)
    assert not isinstance([1.2], new_type)
    type_a = parse_typedef(Union[List[Tuple[str, int]], List[int], List[float]])
    type_b = parse_typedef(List[List[Union[str, int, float]]])
    assert isinstance([("a", 1)], type_a)
    assert isinstance([["a", 1]], type_b)

    assert not isinstance([["a", "a"]], type_a)
    assert not isinstance([[1, "a"]], type_a)
    # homogenous tuple type:
    assert isinstance(tuple([1, 1, 1, 1]), parse_typedef(Tuple[int, ...]))
    assert not isinstance(tuple([1, 1, 1, 1]), parse_typedef(Tuple[str, ...]))
    assert isinstance(tuple(["a", "b", "c"]), parse_typedef(Tuple[str, ...]))

    TypedDict = parse_typedef(Dict[Union[str, int, float], str])

    assert isinstance({1.0: "a", 4: "b", "c": "d"}, TypedDict)
    assert not isinstance({1.0: "a", 4: "b", "c": "d", object(): "foo"}, TypedDict)
    assert not isinstance({1.0: "a", 4: "b", "c": object()}, TypedDict)


def test_enum():
    class MyEnum(Enum):
        A = "a"
        B = "b"

    types = parse_typedef(Optional[MyEnum])
    assert isinstance(types, tuple)
    assert all(isinstance(x, type) for x in types)
    assert isinstance(None, types)
    assert isinstance(MyEnum.A, types)
    assert not isinstance("a", types)


def test_custom_name():
    types = parse_typedef(Union[List[str], List[float]])
    assert not frozenset(x.__name__ for x in types) - frozenset(["List[str]", "List[float]"])


def test_literal():
    type_a = parse_typedef(Literal["a", "b"])
    assert isinstance("a", type_a)
    assert isinstance("b", type_a)
    assert not isinstance("c", type_a)

    class File(Base):
        binary_mode: Literal["rb", "wb", "r+b", "w+b"]

    f = File("rb")
    assert f.binary_mode == "rb"
    f.binary_mode = "wb"
    assert f.binary_mode == "wb"
    with pytest.raises(TypeError) as exc:
        f.binary_mode = "blah blah"
    assert str(exc.value).endswith('binary_mode expects either an "rb", "wb", "r+b" or a "w+b"')


def test_generic():
    T = TypeVar("T")

    class Item(Generic[T]):
        pass

    assert parse_typedef(Item) is Item
    # To do: support generics?
    with pytest.raises(NotImplementedError):
        parse_typedef(Item[int])


def test_set():
    type_a = parse_typedef(Set[str])
    type_b = parse_typedef(FrozenSet[str])
    assert isinstance({"a", "b"}, type_a)
    assert not isinstance({"a", "b"}, type_b)
    assert isinstance(frozenset({"a", "b"}), type_b)
    assert not isinstance(frozenset({"a", "b"}), type_a)


def test_collection_detection():
    class Foo(Base):
        __slots__ = {"a": List[str]}

    assert has_collect_class(List[Foo], Base)
    assert has_collect_class(Tuple[Foo, ...], Base)
    assert has_collect_class(Tuple[Optional[Foo], ...], Base)
    assert has_collect_class(Dict[str, List[Optional[Foo]]], Base)
    assert not has_collect_class(Dict[str, str], Base)
    assert not has_collect_class(Dict[str, Foo], Base)
    assert not has_collect_class(Dict[str, Dict[str, Foo]], Base)
    assert has_collect_class(Dict[str, Dict[str, List[Foo]]], Base)
    assert has_collect_class(Dict[str, Tuple[Union[str, List[Foo]]]], Base)


def test_find_atomic_classes():
    class Item(Base):
        foo: str

    class Bar(Base):
        field: Item

    assert (Item,) == tuple(find_class_in_definition(Item, AtomicMeta, metaclass=True))
    # find_class_in_definition only goes one level and will always return the immediate atomic level
    assert (Bar,) == tuple(find_class_in_definition(Bar, AtomicMeta, metaclass=True))

    type_hints = Tuple[Item, ...]
    items = tuple(find_class_in_definition(type_hints, AtomicMeta, metaclass=True))
    assert items == (Item,)
    assert items[0] is Item
    items = tuple(
        find_class_in_definition(Tuple[Tuple[Item, Item], ...], AtomicMeta, metaclass=True)
    )
    assert items == (Item, Item)
    items = tuple(
        find_class_in_definition(
            Tuple[Tuple[Dict[str, Item], int], ...], AtomicMeta, metaclass=True
        )
    )
    assert items == (Item,)
    type_hints = Optional[Bar]
    items = tuple(find_class_in_definition(type_hints, AtomicMeta, metaclass=True))
    assert items == (Bar,)


def test_parse_typedef_generics():
    T = TypeVar("T")
    assert is_typing_definition(T)
    assert tuple(find_class_in_definition((T,), TypeVar)) == (T,)
    assert tuple(find_class_in_definition(T, TypeVar)) == (T,)
    U = TypeVar("U")
    ListOfT = List[T]
    ListOfTint = ListOfT[int]

    assert not isinstance("any", parse_typedef(T))
    assert not isinstance([1, 2, 3], parse_typedef(ListOfT))
    assert not isinstance("any", parse_typedef(ListOfTint))
    assert not isinstance([None, 2, 3], parse_typedef(ListOfTint))

    assert isinstance([1, 2, 3], parse_typedef(ListOfTint))

    cls = parse_typedef(ListOfT)
    assert callable(cls)
    assert isinstance(cls, type)
    cls_int = cls[int]
    assert isinstance([1, 2, 3], cls_int)

    SomeDictGeneric = Dict[T, U]
    SomeGenericSeq = Tuple[T, U]
    assert not isinstance({"1": 1}, parse_typedef(SomeDictGeneric))
    DictStrInt = SomeDictGeneric[str, int]
    assert isinstance({"1": 1}, parse_typedef(DictStrInt))
    assert isinstance((1, "str"), parse_typedef(SomeGenericSeq[int, str]))
    assert not isinstance((1, 1), parse_typedef(SomeGenericSeq[int, str]))
    assert not isinstance((1, 1), parse_typedef(Tuple[int, str]))
