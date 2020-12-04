"""
These tests are intended as part of the building blocks
for being able to write an appropriate coerce function for a given
class when it has fields subtracted such that an instance of parent class
can be used in the subtracted field appropriately.

i.e.

class MyComposite(Base):
    a: int
    b: int

class Foo(Base):
    field: MyComposite

value = (Foo - {"field": {"a"}})(field=MyComposite(1, 2))
assert value.field.a is None
assert value.field.b == 2

"""

from pytest import fixture
from typing import Tuple, Mapping, Union, List
from instruct import SimpleBase, keys, transform_typing_to_coerce, Atomic, asdict
from instruct.subtype import (
    handle_instruct,
    handle_collection,
    handle_object,
    handle_mapping,
    handle_union,
)


@fixture(scope="session")
def Item():
    class ItemCls(SimpleBase):
        field: str
        value: int

        def __repr__(self):
            value = {}
            for key in keys(type(self)):
                value[key] = getattr(self, key)
            return f"{type(self).__name__}({value!r})"

    return ItemCls


@fixture(scope="session")
def SubItem(Item):
    return Item - {"field"}


@fixture(scope="session")
def ComplexItem(Item):
    class ComplexItemImpl(SimpleBase):
        mapping: Mapping[str, Mapping[str, Union[Item, int]]]
        vector: List[Item]
        vector_map: Tuple[Mapping[int, Tuple[Item, ...]]]

    return ComplexItemImpl


def test_simple_function_composition(Item, SubItem):
    """
    For the raw callable for casting

    Item -> Item - {...}
    """

    cast_func = handle_instruct(Atomic, Item, SubItem)
    from_value = Item(field="my value", value=123)
    to_value = SubItem(field="my value", value=123)
    assert cast_func(from_value) == to_value
    assert isinstance(cast_func(from_value), SubItem)

    # test currying

    cast_func = handle_instruct(Atomic, Item)(SubItem)
    assert cast_func(from_value) == to_value
    assert isinstance(cast_func(from_value), SubItem)


def test_collection_function_composition(Item, SubItem):
    """
    For the raw callable for casting

    List[Item] -> List[SubItem]
    Tuple[Item, ...] -> Tuple[SubItem, ...]
    Tuple[Item, str] -> Tuple[SubItem, str]
    """
    cast_func = handle_collection(list, handle_instruct(Atomic, Item, SubItem))
    from_value = [Item(field="my value", value=123)]
    to_value = [SubItem(field="my value", value=123)]
    mutated_value = cast_func(from_value)
    assert mutated_value == to_value
    assert isinstance(mutated_value, list)
    assert all(isinstance(x, SubItem) for x in mutated_value)

    cast_func = handle_collection(tuple, handle_instruct(Atomic, Item, SubItem))
    from_value = (Item(field="my value", value=123),)
    to_value = (SubItem(field="my value", value=123),)
    mutated_value = cast_func(from_value)
    assert mutated_value == to_value
    assert isinstance(mutated_value, tuple)
    assert all(isinstance(x, SubItem) for x in mutated_value)

    cast_func = handle_collection(tuple, handle_instruct(Atomic, Item, SubItem, handle_object(str)))
    from_value = (Item(field="my value", value=123), "abcdef")
    to_value = (SubItem(field="my value", value=123), "abcdef")
    mutated_value = cast_func(from_value)
    assert mutated_value == to_value
    assert isinstance(mutated_value, tuple)
    assert isinstance(mutated_value[0], SubItem) and isinstance(mutated_value[1], str)


def test_mapping_function_composition(Item, SubItem):
    """
    For the raw callable for casting
    Mapping[str, Item] -> Mapping[str, SubItem]
    Mapping[str, Mapping[str, Item]] -> Mapping[str, Mapping[str, SubItem]]
    Mapping[str, Tuple[str, Item]] -> Mapping[str, Tuple[str, SubItem]]
    Mapping[Union[str, int], Union[Tuple[Item, ...], Tuple[str, ...]]]
    """

    # Mapping[str, Mapping[str, Item]] -> Mapping[str, Mapping[str, SubItem]]
    cast_func = handle_mapping(
        dict, str, handle_mapping(dict, str, handle_instruct(Atomic, Item, SubItem))
    )
    from_value = {"a": {"b": Item(field="my value", value=1234)}}
    to_value = {"a": {"b": SubItem(field="my value", value=1234)}}
    mutated_value = cast_func(from_value)
    assert mutated_value == to_value

    # Mapping[str, Tuple[str, Item]] -> Mapping[str, Tuple[str, SubItem]]
    cast_func = handle_mapping(
        dict,
        str,
        handle_collection(tuple, handle_object(str), handle_instruct(Atomic, Item, SubItem)),
    )
    from_value = {"a": ("b", Item(field="my value", value=1234))}
    to_value = {"a": ("b", SubItem(field="my value", value=1234))}
    mutated_value = cast_func(from_value)
    assert mutated_value == to_value

    # Mapping[Union[str, int], Union[Tuple[Item, ...], Tuple[str, ...]]]
    cast_func = handle_mapping(
        dict,
        handle_union(str, handle_object(str), int, handle_object(int)),
        handle_union(
            Tuple[Item, ...],
            handle_collection(tuple, handle_instruct(Atomic, Item, SubItem)),
            Tuple[str, ...],
            handle_collection(tuple, handle_object(str)),
        ),
    )
    from_value = {
        "a": (Item(field="my value", value=12345), Item(field="my secnd v", value=0)),
        1: ("a", "b", "c"),
        "d": ("d",),
        "f": (Item(field="my", value=13111), Item(field="my fourth v", value=0)),
    }
    to_value = {
        "a": (SubItem(field="my value", value=12345), SubItem(field="my secnd v", value=0)),
        1: ("a", "b", "c"),
        "d": ("d",),
        "f": (SubItem(field="my", value=13111), SubItem(field="my fourth v", value=0)),
    }
    mutated_value = cast_func(from_value)
    assert mutated_value == to_value


def test_transform_typing_to_coerce(Item, SubItem, ComplexItem):
    type_hints = Item
    coerce_types, cast_func = transform_typing_to_coerce(type_hints, {Item: SubItem})
    assert type_hints is coerce_types

    from_value = Item(field="my value", value=123)
    to_value = SubItem(field="my value", value=123)
    assert cast_func(from_value) == to_value
    assert isinstance(cast_func(from_value), SubItem)

    type_hints = Tuple[Item, ...]
    coerce_types, cast_func = transform_typing_to_coerce(type_hints, {Item: SubItem})
    assert type_hints is coerce_types
    from_value = (Item(field="my value", value=123),)
    to_value = (SubItem(field="my value", value=123),)
    mutated_value = cast_func(from_value)
    assert mutated_value == to_value
    assert isinstance(mutated_value, tuple)
    assert all(isinstance(x, SubItem) for x in mutated_value)

    kill_keys = {"mapping": "value", "vector": "value", "vector_map": "field"}

    cls = ComplexItem - kill_keys

    from_value = ComplexItem(
        {"a": {"b": 1, "c": Item(field="value mine", value=321)}},
        [Item("", 1), Item("a", 2)],
        ({1: (Item("unique", 233), Item("None", 3144))},),
    )
    to_value = cls(
        {"a": {"b": 1, "c": (Item - "value")("value mine")}},
        [(Item - "value")(""), (Item - "value")("a")],
        ({1: ((Item - "field")(233), (Item - "field")(3144))},),
    )
    kwargs = {}
    for key, type_hints in ComplexItem._slots.items():
        coerce_types, coerce_function = transform_typing_to_coerce(
            type_hints, {Item: Item - kill_keys[key]}
        )
        assert coerce_types is type_hints
        kwargs[key] = coerce_function(getattr(from_value, key))
    assert cls(**kwargs) == to_value


def test_downcoerce(Item, SubItem, ComplexItem):
    cls = ComplexItem - {"mapping": "value", "vector": "value", "vector_map": "field"}
    from_value = ComplexItem(
        {"a": {"b": 1, "c": Item(field="value mine", value=321)}},
        [Item("", 1), Item("a", 2)],
        ({1: (Item("unique", 233), Item("None", 3144))},),
    )
    to_value = cls(
        {"a": {"b": 1, "c": (Item - "value")("value mine")}},
        [(Item - "value")(""), (Item - "value")("a")],
        ({1: ((Item - "field")(233), (Item - "field")(3144))},),
    )
    instance = cls(**dict(from_value))
    assert instance == to_value
