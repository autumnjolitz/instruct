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
from typing import Tuple
from instruct import SimpleBase
from instruct.subtype import *


@fixture(scope="session")
def Item():
    class ItemCls(SimpleBase):
        field: str
        value: int

    return ItemCls


@fixture(scope="session")
def SubItem(Item):
    return Item - {"field"}


def test_simple_function_composition(Item, SubItem):
    """
    For the raw callable for casting

    Item -> Item - {...}
    """

    cast_func = handle_instruct(Item, SubItem)
    from_value = Item(field="my value", value=123)
    to_value = SubItem(field="my value", value=123)
    assert cast_func(from_value) == to_value
    assert isinstance(cast_func(from_value), SubItem)

    # test currying

    cast_func = handle_instruct(Item)(SubItem)
    assert cast_func(from_value) == to_value
    assert isinstance(cast_func(from_value), SubItem)


def test_collection_function_composition(Item, SubItem):
    """
    For the raw callable for casting

    List[Item] -> List[SubItem]
    Tuple[Item, ...] -> Tuple[SubItem, ...]
    Tuple[Item, str] -> Tuple[SubItem, str]
    """
    cast_func = handle_collection(list, handle_instruct(Item, SubItem))
    from_value = [Item(field="my value", value=123)]
    to_value = [SubItem(field="my value", value=123)]
    mutated_value = cast_func(from_value)
    assert mutated_value == to_value
    assert isinstance(mutated_value, list)
    assert all(isinstance(x, SubItem) for x in mutated_value)

    cast_func = handle_collection(tuple, handle_instruct(Item, SubItem))
    from_value = (Item(field="my value", value=123),)
    to_value = (SubItem(field="my value", value=123),)
    mutated_value = cast_func(from_value)
    assert mutated_value == to_value
    assert isinstance(mutated_value, tuple)
    assert all(isinstance(x, SubItem) for x in mutated_value)

    cast_func = handle_collection(tuple, handle_instruct(Item, SubItem, handle_object(str)))
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
    cast_func = handle_mapping(dict, str, handle_mapping(dict, str, handle_instruct(Item, SubItem)))
    from_value = {"a": {"b": Item(field="my value", value=1234)}}
    to_value = {"a": {"b": SubItem(field="my value", value=1234)}}
    mutated_value = cast_func(from_value)
    assert mutated_value == to_value

    cast_func = handle_mapping(
        dict, str, handle_collection(tuple, handle_object(str, handle_instruct(Item, SubItem)))
    )
    from_value = {"a": ("b", Item(field="my value", value=1234))}
    to_value = {"a": ("b", SubItem(field="my value", value=1234))}
    mutated_value = cast_func(from_value)
    assert mutated_value == to_value

    cast_func = handle_mapping(
        dict,
        handle_object(str, handle_object(int)),
        handle_collection(
            Tuple[Item, ...],
            handle_instruct(Item, SubItem, handle_collection(tuple, handle_object(str))),
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


# More todo:
# - handle_mapping(dict, str, handle_collection(tuple, handle_instruct(Item, SubItem, handle_object(str))))
# - handle_mapping(dict, str, handle_collection(tuple, handle_instruct(Item, SubItem)))
# - handle_mapping(dict, str, handle_collection(tuple, handle_object(str, handle_instruct(Item, SubItem))))
