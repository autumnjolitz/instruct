from pickle import loads, dumps

import pytest
from instruct.types import FrozenMapping, FROZEN_MAPPING_SINGLETONS
from instruct.utils import flatten, flatten_fields


def test_frozen_mapping():
    # Test identity operations:
    assert FrozenMapping() is FrozenMapping(None) is FrozenMapping({})
    # Test simple mapping:

    f1 = FrozenMapping({"a": 1, "b": 2})
    assert f1 is FrozenMapping({"a": 1, "b": 2})

    # Test pickling:
    assert loads(dumps(f1)) is f1

    # Test exploding on unhashable types:
    with pytest.raises(TypeError):
        f2 = FrozenMapping({"a": {"unhashable"}})

    # Test on other hashables:
    f2 = FrozenMapping({"a": frozenset({"hashable"})})
    assert f2 is FrozenMapping({"a": frozenset({"hashable"})})

    # Test merging:
    f3 = f1 | f2
    assert f3["a"] == frozenset({"hashable"})
    f3 |= {"b": 3}
    assert f3["b"] == 3
    f4 = {"foo": "bar"} | f3
    f4_i = f3 | {"foo": "bar"}
    assert isinstance(f4, FrozenMapping)
    assert isinstance(f4_i, FrozenMapping)
    assert hash(f4) == hash(f4_i)
    assert f4 is f4_i
    assert (f4 - {"foo"}) is f3
    assert (f4 - {"foo": "baz"}) is f4_i
    x = FrozenMapping({"a": {"b": {"c": None}, "d": 1}}) - FrozenMapping({"a": "b"})
    assert x is FrozenMapping({"a": {"d": 1}})

    # Test weak refs:
    hash_code_1 = hash(f1)
    hash_code_2 = hash(f2)
    assert hash_code_1 in FROZEN_MAPPING_SINGLETONS
    assert hash_code_2 in FROZEN_MAPPING_SINGLETONS
    # Kill it:
    del f1, f2
    assert hash_code_1 not in FROZEN_MAPPING_SINGLETONS
    assert hash_code_2 not in FROZEN_MAPPING_SINGLETONS


def test_flatten():
    assert flatten([["a"]], eager=True) == ("a",)


def test_flatten_fields():
    # The format is always:
    #   if a string, it means "remove this from the DAO universally"
    #   if a mapping, means "operate on this field and operate on these elements"
    #       where operation if string means "remove" and if not string means recurse
    expected = FrozenMapping(
        {
            "a": FrozenMapping({"a": None}),
            "Q": FrozenMapping({"x": None, "y": None}),
            "b": FrozenMapping({"c": None}),
            "d": FrozenMapping(
                {"e": FrozenMapping({"f": None}), "h": FrozenMapping({"foo": None, "bar": None})}
            ),
            "stripme": None,
        }
    )

    assert flatten_fields.collect(expected) == expected

    n1 = flatten_fields.collect(
        {
            "a": ("a",),
            "Q": ("x", "y"),
            "b": "c",
            "d": {"e": {"f"}, "h": ("foo", "bar")},
            "stripme": None,
        }
    )
    assert n1 == expected

    n2 = flatten_fields.collect(
        {
            "a": {"a": None},
            "Q": {"x": None, "y": None},
            "b": {"c": None},
            "d": {"e": {"f": None}, "h": {"foo": None, "bar": None}},
            "stripme": None,
        }
    )
    assert n2 == expected
    n3 = flatten_fields.collect(
        {
            "a": ({"a": None},),
            "Q": ({"x": None}, {"y": None}),
            "b": {"c": None},
            "d": {"e": {"f": None}, "h": ({"foo": None, "bar": None},)},
            "stripme": {},
        }
    )
    assert n3 == expected


def test_merge_skip_keys():
    skipped = FrozenMapping({})
    skip_only_a = skipped | flatten_fields.collect({"a"})
    assert skip_only_a is FrozenMapping({"a": None})
    skip_parts_of_ab = skipped | flatten_fields.collect({"a": {"b": None}, "c": {"d": None}})
    assert skip_parts_of_ab is FrozenMapping({"a": {"b": None}, "c": {"d": None}})
    assert (skip_parts_of_ab | flatten_fields.collect(("a", "b", "c"))) is FrozenMapping(
        {"a": None, "b": None, "c": None}
    )
