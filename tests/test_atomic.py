import json
import pprint
import sys
from typing import Union, List, Tuple, Optional, Dict, Any, Type, Generic, Set

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from enum import Enum
import datetime
import base64
import pickle
from collections.abc import Mapping as AbstractMapping

import pytest
import instruct
import inflection
from instruct.types import AbstractAtomic
from instruct import (
    public_class,
    Base,
    add_event_listener,
    ClassCreationFailed,
    OrphanedListenersError,
    handle_type_error,
    SimpleBase,
    NoJSON,
    NoIterable,
    NoPickle,
    Range,
    RangeError,
    AtomicMeta,
    NoHistory,
    clear,
    asdict,
    asjson,
    schema_for,
)

if sys.version_info < (3, 9):
    from typing_extensions import get_type_hints
else:
    from typing import get_type_hints

if sys.version_info >= (3, 13):
    from typing import TypeVar
else:
    from typing_extensions import TypeVar


def test_simple() -> None:
    class Data(SimpleBase):
        foo: int
        bar: str
        baz: Dict[str, Any]
        cool: Annotated[int, "is this cool?", "yes"]

    assert get_type_hints(Data) == {
        "foo": int,
        "bar": str,
        "baz": Dict[str, Any],
        "cool": int,
    }
    assert isinstance(Data, AbstractAtomic)
    assert isinstance(Data(), AbstractAtomic)


class Data(Base, history=True):
    __slots__ = {"field": Union[str, int], "other": str}

    def __init__(self, **kwargs):
        self.field = 0
        super().__init__(**kwargs)


class NestedData(Base):
    """
    And embedded dict should mean a class will be spawned and stored at the value
    location
    """

    __slots__ = {"id": int, "nested": {"field": str}}


class Field(Base):
    __slots__ = {"field": str}


class Child(Field):
    __slots__ = {"another": str}


class NestedDataAlt(Base):
    __slots__ = {"id": int, "nested": Field}


class LinkedFields(Base):
    __slots__ = {"id": int, "name": str}

    __coerce__ = {"id": (str, lambda obj: int(obj, 10))}

    def __init__(self, *args, **kwargs):
        self.id = 0
        super().__init__(*args, **kwargs)

    @add_event_listener("id")
    def _on_id_change(self, old, new):
        if new == -1:
            self.name = "invalid"


class IBase(Base):
    __slots__ = ()


class InheritCoerceBase(IBase):
    __slots__ = {"id": int}

    __coerce__ = {"id": (str, lambda obj: int(obj, 10))}


class InheritCoerce(InheritCoerceBase):
    __slots__ = {"baz": int}
    __coerce__ = {"baz": (str, lambda obj: int(obj, 10))}

    @property
    def off_by_one(self):
        return self.baz + 1

    @off_by_one.setter
    def off_by_one(self, val):
        self.baz = val - 1


def test_ordering_keys():
    assert tuple(InheritCoerce.keys()) == ("id", "baz")
    assert tuple(InheritCoerce.keys(InheritCoerce(id=1, baz="2"))) == ("id", "baz")


def test_constructor_arguments():
    InheritCoerce(1, "2")
    with pytest.raises(TypeError):
        InheritCoerce(1, "2", 2)
    # keyword arguments always are applied after positional lol
    i = InheritCoerce(1, 2, off_by_one=3)
    assert i.baz == 2


def test_coerce_definition_error():
    with pytest.raises(TypeError) as exc_info:

        class Foo(Base):
            __slots__ = {"a": int}

            __coerce__ = "a string"

    assert "AbstractMapping" in str(exc_info.value)


def test_inheritance():
    child = Child(field="a", another="b")
    assert child.field == "a"
    assert child.another == "b"
    assert child._column_types["field"] is str

    assert InheritCoerce(id="1234").id == 1234


def test_mapping():
    l1 = LinkedFields(id=2, name="Name")
    assert len(l1) == 2
    assert isinstance(l1, AbstractMapping)


def test_pickle():
    l1 = LinkedFields(id=2, name="Name")
    data = pickle.dumps(l1)
    l2 = pickle.loads(data)
    assert l1 == l2


def test_subtracted_pickle():
    cls = LinkedFields - {"id"}
    assert instruct.keys(cls) == {"name"}
    c = cls("Autumn")
    assert cls._skipped_fields == {"id": None}
    assert instruct._dump_skipped_fields(cls) == {"id": None}
    data = pickle.dumps(c)
    c2 = pickle.loads(data)
    assert c == c2
    assert instruct.public_class(c2, preserve_subtraction=True) is cls


def test_partial_pickle():
    l1 = LinkedFields(id=2)
    assert l1.name is None
    data = pickle.dumps(l1)
    l2 = pickle.loads(data)
    assert l1 == l2


def test_json():
    l1 = LinkedFields(id=2, name="Name")
    print("y")
    x = asjson(l1)
    print(x)
    data = json.dumps(x)
    print("DAta ", data)
    l2 = LinkedFields(**json.loads(data))
    assert l1 == l2
    l3 = LinkedFields.from_json(asjson(l1))
    assert l1 == l2 == l3


def test_json_complex():
    class SubItems(Base):
        __slots__ = {"value": int}

    called = 0

    def _parse_collection(items):
        nonlocal called
        called += 1
        return [SubItems(**item) for item in items]

    class Item(Base):
        __slots__ = {"collection": List[SubItems]}
        __coerce__ = {"collection": (List[dict], _parse_collection)}

    collection = [{"value": 1}, {"value": -1}]
    assert not isinstance(collection[0], SubItems)
    assert not isinstance(collection, Item._column_types["collection"])
    a = Item(collection=collection)
    assert asdict(a) == {"collection": _parse_collection(collection)}
    assert a.collection
    assert a.collection == _parse_collection(collection)
    a_json = asjson(a)
    assert "collection" in a_json
    assert isinstance(a_json["collection"][0], dict)
    assert isinstance(a_json["collection"][1], dict)
    element = a["collection"][0]
    assert called > 0
    assert isinstance(element, SubItems)


def test_mapping_immutability():
    class Embedded(Base):
        __slots__ = {"d": str}

    class Item(Base):
        __slots__ = {"data": Dict[str, Embedded]}

    i = Item(data={"foo": Embedded(d="bar")})
    data = asjson(i)
    assert isinstance(i.data["foo"], Embedded)
    del data


def test_coercion():
    l = LinkedFields(id="2", name="attr")  # noqa
    assert l.id == 2
    l.id = "5"
    assert l.id == 5


def test_event_listener():
    l = LinkedFields(id=2, name="attr")  # noqa
    l.id = -1
    assert l.name == "invalid"


def test_derived_klass():
    assert isinstance(NestedData._columns["nested"], type)
    item = NestedData(id=1, nested={"field": "name"})
    assert item.nested.field == "name"
    with pytest.raises(TypeError):
        item.nested.field = 1


def test_derived_equivalence():
    item = NestedData(id=1, nested={"field": "name"})
    item_alt = NestedDataAlt(id=1, nested={"field": "name"})
    assert item == item_alt


def test_valid_types():
    t = Data(field=1)
    assert "__dict__" not in dir(t)
    assert t.field == 1
    t.field = "t"
    assert t.field == "t"


def test_invalid_types():
    with pytest.raises(TypeError):
        Data(field=None)


def test_history():
    t = Data(field="name")
    t.field = "not name"
    for change in t.list_changes():
        print(change)
        print(
            "[{0.timestamp}] [{0.delta.state}] {0.key} -> {0.delta.old} -> {0.delta.new}".format(
                change
            )
        )


def test_history_autoprune():
    """
    A historical object should be smart enough to recognize when it's not really changed
    """
    t = Data(field="name")
    t.field = "not name"
    t.field = "name"
    changes = tuple(t.list_changes())
    for change in changes:
        print(
            "[{0.timestamp}] [{0.delta.state}] {0.key} -> {0.delta.old} -> {0.delta.new}".format(
                change
            )
        )
    assert len(changes) == 3
    assert not t.is_dirty, "object was cleanly initialized and not effectively changed"


def test_changed():
    t = Data()
    t.field = "Name"
    assert t.is_dirty, "Item should be dirty - we added a property!"
    t.field = 0
    assert not t.is_dirty, "Item is now reset"


def test_reset():
    t = Data(field="Name")
    t.reset_changes()
    assert t.field == "Name"
    assert not t.is_dirty


def test_fast_setter():
    class FastData(Base, fast=True):
        __slots__ = {"a": int, "bar": str}

        @add_event_listener("a")
        def on_a_set(self, old, new):
            self.bar = str(new)

    f = FastData(a=1)
    assert f.bar == "1"


def test_values_view():
    class Foo(SimpleBase):
        foo: str

    f = Foo("abc")
    assert "abc" in instruct.values(f)

    with pytest.raises(AttributeError):
        # Avoid clobbering any properties named values please.
        f.values()
    print(instruct.values(f))
    assert {"abc"} == set(instruct.values(f))


def test_items_view():
    class Bar(Base):
        baz: int

    class Foo(Base):
        foo: str
        bar: Optional[Bar]

    f = Foo("abc", Bar(1))
    assert dict(Foo.items(f)) == f._asdict()


def test_getitem():
    class Foo(Base):
        __slots__ = {"a": int, "b": str}

        def some_func():
            return 1

        @add_event_listener("b")
        def _on_b(self, old, new):
            print("ass", new, type(self))

    f = Foo(a=1, b="s")
    assert f["a"] == 1
    assert f["b"] == "s"

    assert {**f} == {"a": 1, "b": "s"}
    f["b"] = "New str"
    assert f["b"] == "New str"
    with pytest.raises(TypeError):
        f["b"] = 1234

    # Now test a more complicated case:
    with pytest.raises(OrphanedListenersError):

        class BarA(Foo):
            __slots__ = {"new": Union[str, int]}

            @property
            def c(self):
                return self.new

            @c.setter
            def c(self, val):
                self.new = val

            @add_event_listener("b")
            def _change_b(self, old, new):
                self._b_ = new.upper()

            @add_event_listener("new")
            def _on_update_(self, _, new):
                self._new_ = new * 2

        del BarA

    class BarA(Foo):
        __slots__ = {"new": Union[str, int], "b": str}

        @property
        def c(self):
            return self.new

        @c.setter
        def c(self, val):
            self.new = val

        @add_event_listener("b")
        def _change_b(self, old, new):
            self._b_ = new.upper()

        @add_event_listener("new")
        def _on_update_(self, _, new):
            self._new_ = new * 2

    b = BarA(c=1, a=2, b="A string")
    assert b.b == "A STRING"

    assert {**b} == {"new": 2, "a": 2, "b": "A STRING"}


class Member(Base):
    first_name: str
    last_name: str
    id: int

    def _set_defaults(self):
        self.first_name = self.last_name = ""
        self.id = -1
        super()._set_defaults()


class Organization(Base, history=True):
    # ARJ: Note how we can also use the dataclass/typing.NamedTuple
    # definition format and it behaves just like the ``__slots__`` example
    # above!
    name: str
    id: int
    members: List[Member]
    created_date: datetime.datetime
    secret: Annotated[str, NoJSON, NoPickle, NoIterable, NoHistory]

    __coerce__ = {
        "created_date": (str, lambda obj: datetime.datetime.strptime("%Y-%m-%d", obj)),
        "members": (List[dict], lambda values: [Member(**value) for value in values]),
    }

    def _set_defaults(self):
        self.name = ""
        self.id = -1
        self.members = []
        self.created_date = datetime.datetime.utcnow()
        super()._set_defaults()


def test_readme():
    data = {
        "name": "An Org",
        "id": 123,
        "members": [{"id": 551, "first_name": "Jinja", "last_name": "Ninja"}],
    }
    org = Organization(**data)
    assert org._annotated_metadata and org._annotated_metadata["secret"]
    assert org.members[0].first_name == "Jinja"
    org.name = "New Name"
    org.created_date = datetime.datetime(2018, 10, 23)
    pprint.pprint(tuple(org.list_changes()))
    print(asdict(org))
    types = frozenset((type(x) for _, x in org))
    assert len(types) == 4 and type(None) not in types
    assert not any(y == "my secret" for y in tuple(org))
    assert Organization.to_json(org) == {
        "created_date": "2018-10-23T00:00:00",
        "id": 123,
        "members": [{"first_name": "Jinja", "id": 551, "last_name": "Ninja"}],
        "name": "New Name",
    }
    org2 = pickle.loads(pickle.dumps(org))
    assert org2.secret is None
    assert asjson(org2) == {
        "created_date": "2018-10-23T00:00:00",
        "id": 123,
        "members": [{"first_name": "Jinja", "id": 551, "last_name": "Ninja"}],
        "name": "New Name",
    }

    clear(org)
    assert frozenset((type(x) for _, x in org)) == {type(None)}


def test_invalid_kwargs():
    class Test(Base):
        __slots__ = {"foo": str, "bar": float, "blech": int}

    with pytest.raises(ClassCreationFailed) as e:
        Test(foo=1.2, bar=1, blech="2")
    assert len(e.value.errors) == 3
    print(asjson(e.value))


def test_properties():
    class Test(Base):
        __slots__ = {"foo": str, "bar": float, "blech": int}

        @property
        def yoo(self):
            return self.foo

        @yoo.setter
        def yoo(self, val):
            self.foo = val

    assert Test._properties | Test._columns.keys() == frozenset(["foo", "bar", "blech", "yoo"])

    t = Test(yoo="New foo")
    assert t.foo == "New foo"


def test_coerce_complex():
    class ItemItem(Base):
        __slots__ = {"value": int}

    class Item(Base):
        __slots__ = {"value": List[ItemItem]}

        __coerce__ = {"value": (List[dict], lambda items: [ItemItem(**item) for item in items])}

    f = Item(value=[{"value": 1}, {"value": 2}])
    assert tuple(item.value for item in f.value) == (1, 2)
    with pytest.raises(TypeError, match="Unable to set value"):
        try:
            Item(value=[1, 2])
        except ClassCreationFailed as e:
            (err,) = e.errors
            raise err from None

    class SomeEnum(Enum):
        VALUE = "value"
        V2 = "v2"

    def parse(items):
        return [tuple(item) for item in items]

    class ComplextItem(Base):
        __slots__ = {
            "name": str,
            "type": SomeEnum,
            "value": Union[List[Tuple[str, int]], List[int], List[float]],
            "some_set": Set[str],
            "fixed": Literal["immatype"],
        }

        __coerce__ = {
            "type": (str, lambda val: SomeEnum(val)),
            "value": (List[List[Union[str, int, float]]], parse),
        }

    class VectoredItems(Base):
        __slots__ = {"items": List[ComplextItem]}

        __coerce__ = {
            "items": (
                List[dict],
                lambda items: [ComplextItem(**item) for item in items],
            )
        }

    c = ComplextItem(value=[["a", 1], ["b", 2]], name="ab", type="value")
    assert c.value == [("a", 1), ("b", 2)]

    VectoredItems(items=[{"value": [["a", 1], ["b", 2]], "name": "ab", "type": "value"}])
    assert schema_for(VectoredItems) == {
        "items": [
            {
                "name": str,
                "some_set": {str},
                "fixed": "immatype",
                "type": {"oneof": ["value", "v2"]},
                "value": {
                    "oneof": [
                        [{0: str, 1: int}],
                        [int],
                        [float],
                    ]
                },
            }
        ]
    }


def test_qulaname():
    def parse(items):
        return [tuple(item) for item in items]

    class SomeEnum(Enum):
        VALUE = "value"

    class ComplextItem(Base):
        __slots__ = {
            "name": str,
            "type": SomeEnum,
            "value": Union[List[Tuple[str, int]], List[int], List[float]],
        }

        __coerce__ = {
            "type": (str, lambda val: SomeEnum(val)),
            "value": (List[List[Union[str, int, float]]], parse),
        }

    class VectoredItems(Base):
        __slots__ = {"items": List[ComplextItem]}

        __coerce__ = {
            "items": (
                List[dict],
                lambda items: [ComplextItem(**item) for item in items],
            )
        }

    assert VectoredItems.__qualname__ == "test_qulaname.<locals>.VectoredItems"
    assert (
        VectoredItems._data_class.__qualname__
        == "test_qulaname.<locals>.VectoredItems._VectoredItems"
    )
    assert VectoredItems.__name__ == "VectoredItems"
    assert VectoredItems._data_class.__name__ == "_VectoredItems"
    assert VectoredItems.__module__ is VectoredItems._data_class.__module__
    assert getattr(VectoredItems, "_VectoredItems") is VectoredItems._data_class


def test_redefine_fields():
    class LooseyGooseyItem(Base):
        __slots__ = {"a": Optional[str], "b": Optional[str], "c": Optional[str]}

    class ARequired(LooseyGooseyItem):
        __slots__ = {"a": str}

    item = ARequired(a="a")
    assert item.b is None
    assert item.c is None
    with pytest.raises(ValueError):
        ARequired(a=None)


class DivergentType(Enum):
    USE_DIVERGENT_A = 1
    USE_DIVERGENT_B = 2


class DivergentA(Base):
    __slots__ = {"foo": str, "id": str}


class DivergentB(Base):
    __slots__ = {"type": str, "id": int}


class Foo(Base):
    __extra_slots__ = ("pending",)
    __slots__ = {"complex": Union[DivergentA, DivergentB], "type": DivergentType}

    def __delattr__(self, key):
        if key in self.__class__.keys():
            setattr(self, f"_{key}_", None)

    def __init__(self, **data):
        self.pending = None
        if "complex" in data and not isinstance(data["complex"], (DivergentA, DivergentB)):
            self.pending = data.pop("complex")
        super().__init__(**data)

    @add_event_listener("type")
    def _on_type_set(self, old, new):
        if self.pending is not None:
            if new is DivergentType.USE_DIVERGENT_A:
                self.complex = DivergentA(**self.pending)
                self.pending = None
            elif new is DivergentType.USE_DIVERGENT_B:
                self.complex = DivergentB(**self.pending)
                self.pending = None

    @handle_type_error("complex")
    def _on_type_failure(self, value):
        if isinstance(value, dict):
            self.pending = value
            return True


def test_extra_slots():
    """
    Demonstrate a technique to hold arbitrary values in a lookaside that
    is untracked (intentionally).
    """

    f = Foo(complex={"type": "art", "id": 123})
    assert f.complex is None
    assert f.pending == {"type": "art", "id": 123}

    # pickle shows that we lose the temporary slot as expected:
    # This keeps the requirements that objects are mostly good
    m = pickle.loads(pickle.dumps(f))
    assert m.pending is not f.pending
    assert m.pending is None

    f.type = DivergentType.USE_DIVERGENT_B
    assert f.pending is None
    assert isinstance(f.complex, DivergentB)
    del f.complex
    del f.type

    assert f.pending is None
    div_b = {"id": "123", "foo": "BAAAAAZ"}
    f.complex = div_b
    assert f.pending is not None
    assert f.complex is None
    f.type = DivergentType.USE_DIVERGENT_A
    assert f.complex == DivergentA(**div_b)


def test_original_slots():
    from instruct.typedef import parse_typedef

    for key, value in DivergentA._slots.items():
        assert DivergentA._columns[key] == parse_typedef(value)


def test_embedded_collection_tracking():
    class Foo(Base):
        __slots__ = {"field": Union[str, bool]}

    class Bar(Base):
        __slots__ = {"fields": List[Foo], "bar": List[str]}

    assert "fields" in Bar._nested_atomic_collection_keys
    assert "bar" not in Bar._nested_atomic_collection_keys

    class Barter(Base):
        __slots__ = {"mapping": Dict[str, Bar]}

    assert Barter._nested_atomic_collection_keys.keys() == {"mapping"}

    class CollectableBarter(Barter):
        __slots__ = {"others": Dict[str, Dict[int, List[Barter]]]}

    assert CollectableBarter._nested_atomic_collection_keys.keys() == {
        "others",
        "mapping",
    }

    class InheritedBarter(CollectableBarter, Bar, Foo):
        __slots__ = {"key": str}

    assert not ({"others", "fields"} - set(InheritedBarter._nested_atomic_collection_keys))


def test_skip_fields():
    cls = InheritCoerce - {"id"}
    assert "id" not in cls.keys()
    assert (InheritCoerce.keys() - {"id"}) == cls.keys()
    a = cls(baz="1")
    assert a.baz == 1
    b = cls(1)
    assert b.baz == 1
    assert asjson(b) == {"baz": 1}


def test_override_special_functions():
    class OverriddenEq(Base):
        __slots__ = {"a": str}

        def __eq__(self, other: Union[str, int]) -> bool:
            if isinstance(other, (int, str)):
                other = OverriddenEq(f"{other}")
            return super().__eq__(other)

    assert OverriddenEq("1") == OverriddenEq("1")
    assert OverriddenEq("1") == 1


def test_dataclasses_format():
    """
    Data classes are popular and make linters happy. Let's support them by
    copying __annotations__ -> __slots__ as is.
    """

    class Dataclass(Base):
        a: Union[str, int]
        b: int

    class InstructVersion(Base):
        __slots__ = {"a": Union[str, int], "b": int}

    assert Dataclass("foo", 2) == InstructVersion("foo", 2)

    # Now test the case where the annotations are strings (because of
    # ``from __future__ import annotations``
    # )
    class DataclassFuture(Base):
        a: "Union[str, int]"
        b: "int"

    assert Dataclass("foo", 2) == DataclassFuture("foo", 2)
    assert DataclassFuture("foo", 2) == InstructVersion("foo", 2)


def test_keyword_only_args_super():
    type_signature = Tuple[int, int, int]

    class F(Base):
        __slots__ = ()

        def test_function_capabilities(self, a, b: int = 1, *, defaults=1) -> type_signature:
            return a, b, defaults

    assert F().test_function_capabilities(1) == (1, 1, 1)
    assert F().test_function_capabilities.__annotations__ == {
        "b": int,
        "return": type_signature,
    }

    class BaseClass(Base):
        __slots__ = ()

        def my_function(self, *, defaults=1):
            return defaults, dict(self)

    class Inherits(BaseClass):
        a: str

        def bar(self):
            return self.my_function()

    b = Inherits("foobar")
    assert b.my_function(defaults=2) == (2, {"a": "foobar"})

    assert b.my_function() == (1, {"a": "foobar"})
    assert b.bar() == (1, {"a": "foobar"})


def test_as_primitives():
    class Foo(Base):
        foo: str
        bar: int
        baz: Tuple[complex, ...]

    f = Foo("abc", 1, (1j, 2 + 1j))
    assert f._astuple() == ("abc", 1, (1j, 2 + 1j))
    assert f._asdict() == {"foo": "abc", "bar": 1, "baz": (1j, 2 + 1j)}
    assert f._aslist() == ["abc", 1, (1j, 2 + 1j)]
    assert instruct.astuple(f) == ("abc", 1, (1j, 2 + 1j))
    assert instruct.asdict(f) == {"foo": "abc", "bar": 1, "baz": (1j, 2 + 1j)}
    assert instruct.aslist(f) == ["abc", 1, (1j, 2 + 1j)]


def test_without_keys():
    class Foo(SimpleBase, json=True):
        bar: str

    f = Foo("abc")

    with pytest.raises(TypeError):
        {**f}

    assert asjson(f) == {"bar": "abc"}

    class ClobberedKeys(SimpleBase):
        bar: str
        keys: List[str]

    c = ClobberedKeys("a", ["foo"])
    with pytest.raises(TypeError):
        {**c}

    # Show that accessing the metaclass ALWAYS
    # allows for getting the keys, values, etc functions
    instruct.keys(ClobberedKeys) & {"bar", "keys"} == {"bar", "keys"}
    instruct.keys(c) & {"bar", "keys"} == {"bar", "keys"}


def test_without_json():
    class Foo(SimpleBase):
        bar: int

    f = Foo(1)

    assert Foo.to_json(f) == ({"bar": 1},)
    assert (asjson(f),) == Foo.to_json(f)

    class Clobbered(SimpleBase):
        to_json: bool

    assert not callable(Clobbered.to_json)
    c = Clobbered(False)

    with pytest.raises(TypeError):
        Clobbered.to_json()

    assert type(Clobbered).to_json(c) == ({"to_json": False},)


def test_overridden_from_json():
    class Foo(SimpleBase, json=True):
        field: int

        @classmethod
        def from_json(cls, item: Union[str, Dict[str, Any]]):
            if isinstance(item, str):
                item = json.loads(item)
            return super().from_json(item)

    assert Foo(1) == Foo.from_json('{"field": 1}')


def decodebase64uri(s: str):
    if s.startswith("base64:"):
        return base64.urlsafe_b64decode(s[len("base64") :])
    raise TypeError


def test_bytes_base64():
    class Foo(Base):
        item: bytes
        foo: bytes

        __coerce__ = {("item", "foo"): (str, decodebase64uri)}

    f = Foo(b"\x00\xef\xff", b"foobar")
    assert asjson(f) == {"foo": "base64:Zm9vYmFy", "item": "base64:AO__"}
    assert (
        json.dumps(asjson(f), sort_keys=True) == '{"foo": "base64:Zm9vYmFy", "item": "base64:AO__"}'
    )

    class Broken(Base):
        # intentionally break the json encoder by no-oping the
        # field handling:
        BINARY_JSON_ENCODERS = {"item": lambda val: val}
        item: bytes

    with pytest.raises(TypeError):
        json.dumps(asjson(Broken(b"\x00\xef\xff")))

    class Baz(Base):
        BINARY_JSON_ENCODERS = {"foo": lambda val: val.decode("utf8")}
        item: bytes
        foo: bytes

        __coerce__ = {
            "item": (str, decodebase64uri),
            "foo": (str, lambda val: val.encode("utf8")),
        }

        @classmethod
        def from_json(cls, item: Union[str, Dict[str, Any]]):
            if isinstance(item, str):
                item = json.loads(item)
            return super().from_json(item)

    f = Baz(b"\x00\xef\xff", b"foobar")
    assert asjson(f) == {"foo": "foobar", "item": "base64:AO__"}
    assert json.dumps(asjson(f), sort_keys=True) == '{"foo": "foobar", "item": "base64:AO__"}'
    assert f == Baz.from_json(json.dumps(asjson(f), sort_keys=True))


def test_skip_keys_simple():
    class F(Base):
        foo: str

    class Q(Base):
        bar: str

    class F2(Base):
        foo: str

    f_minus = F - {"foo"}
    f2_minus = F2 - {"foo"}
    assert f_minus is not f2_minus

    q_minus = Q - {"bar"}
    assert q_minus is not Q

    assert F - {"foo"} is F - {"foo"}
    assert F - {"foo"} is not F
    assert Q - {"foo"} is Q - {"foo"}
    assert Q - {"bar"} is Q - {"bar"}
    assert Q - {"bar"} is not Q


def test_complex_skip_keys_simple():
    class Item(Base):
        foo: str
        bar: int

    class Container(Base):
        baz: Item
        name: str

        __coerce__ = {"baz": (Union[Dict[str, Union[str, int]], str], Item.from_json)}

    c = Container({"foo": "abc", "bar": 1}, "hello")

    cls = Container - {"baz": {"foo"}}
    c2 = cls.from_json(asjson(c))
    assert asjson(c2) == {"baz": {"bar": 1}, "name": "hello"}

    c2.baz = {"foo": "s", "bar": 1}
    assert asjson(c2) == {"baz": {"bar": 1}, "name": "hello"}
    c2.baz = Item(**{"foo": "s", "bar": 1})
    assert asjson(c2) == {"baz": {"bar": 1}, "name": "hello"}

    cls = Container - {"baz"}
    c2 = cls.from_json(asjson(c))
    assert asjson(c2) == {"name": "hello"}

    class Item(Base):
        foo: str
        bar: int

    ItemType = Union[Dict[str, Union[str, int]], str]

    class Container(Base):
        bazes: Tuple[Item, ...]
        name: str
        altname: str

        @property
        def altname(self):
            return (self._altname_ or "y") + "x"

        __coerce__ = {"bazes": (Union[List[ItemType], Tuple[ItemType, ...]], Item.from_many_json)}

    c = Container([{"foo": "abc", "bar": 1}], "hello")

    i = (Container - {"name", "altname"}).from_json(asjson(c))
    assert i.name is None
    assert i.altname is None
    assert dict(i).keys() & {"altname", "name"} == set()


def test_skip_keys_complex():
    class Person(Base):
        id: int
        name: str
        created_date: str

    class Position(Base):
        id: int
        supervisor: Tuple[Person, ...]
        worker: Person
        task_name: str

    job_id = 1
    supervisor_id = 2
    worker_id = 456
    regular_people = Position(
        id=job_id,
        supervisor=(Person(id=2, name="John", created_date="0"),),
        worker=Person(id=456, name="Sam", created_date="0"),
        task_name="Business Partnerships",
    )
    assert Person.to_json(regular_people) == {
        "id": 1,
        "supervisor": [{"created_date": "0", "id": 2, "name": "John"}],
        "task_name": "Business Partnerships",
        "worker": {"created_date": "0", "id": 456, "name": "Sam"},
    }

    # Let's pretend they're anonymized:
    FacelessPerson: Type[Person] = Person - {"name", "created_date"}
    FacelessPosition: Type[Position] = Position - {
        "supervisor": {"name", "created_date"},
        "worker": {"name", "created_date"},
    }

    faceless_people = FacelessPosition(
        id=job_id,
        supervisor=(FacelessPerson(id=supervisor_id, name="SupervisorName", created_date="0"),),
        worker=FacelessPerson(id=worker_id, name="worker", created_date="0"),
        task_name="servitor",
    )
    assert faceless_people.id == job_id
    assert faceless_people.supervisor[0].id == supervisor_id
    assert faceless_people.worker.id == worker_id
    # Are we sure they don't have names?
    assert faceless_people.worker.name is None
    assert faceless_people.supervisor[0].name is None
    assert Person.to_json(faceless_people) == {
        "id": 1,
        "supervisor": [{"id": 2}],
        "worker": {"id": 456},
        "task_name": "servitor",
    }

    assert FacelessPerson is FacelessPosition._nested_atomic_collection_keys["supervisor"][0]
    assert FacelessPerson is FacelessPosition._slots["worker"]
    assert instruct._dump_skipped_fields(FacelessPosition) == {
        "supervisor": {"name": None, "created_date": None},
        "worker": {"name": None, "created_date": None},
    }


def test_include_keys_complex():
    class Person(Base):
        id: int
        name: str
        created_date: str

    class Position(Base):
        id: int
        supervisor: Tuple[Person, ...]
        worker: Person
        task_name: str

    job_id = 1
    supervisor_id = 2
    worker_id = 456

    FacelessPerson = Person & "id"
    FacelessPosition = Position & {
        "supervisor": {"id"},
        "worker": "id",
        "id": None,
        "task_name": None,
    }
    faceless_people = FacelessPosition(
        id=job_id,
        supervisor=(FacelessPerson(id=supervisor_id, name="SupervisorName", created_date="0"),),
        worker=FacelessPerson(id=worker_id, name="worker", created_date="0"),
        task_name="servitor",
    )
    assert faceless_people.id == job_id
    assert faceless_people.supervisor[0].id == supervisor_id
    assert faceless_people.worker.id == worker_id
    # Are we sure they don't have names?
    assert faceless_people.worker.name is None
    assert faceless_people.supervisor[0].name is None
    assert Person.to_json(faceless_people) == {
        "id": 1,
        "supervisor": [{"id": 2}],
        "worker": {"id": 456},
        "task_name": "servitor",
    }

    assert FacelessPerson is FacelessPosition._nested_atomic_collection_keys["supervisor"][0]
    assert FacelessPerson is FacelessPosition._slots["worker"]


def test_skip_keys_coerce():
    def parse_supervisors(values):
        assert not isinstance(values, Person)
        return tuple(Person(**value) for value in values)

    def parse_person(value):
        assert not isinstance(value, Person)
        return Person(**value)

    class Person(Base):
        id: int
        name: str
        created_date: str

    class Position(Base):
        id: int
        supervisor: Tuple[Person, ...]
        worker: Person
        task_name: str

        __coerce__ = {
            "supervisor": (List[Dict[str, Union[int, str]]], parse_supervisors),
            "worker": (Dict[str, Union[int, str]], parse_person),
        }

    p = Position.from_json({"id": 1, "task_name": "Business Partnerships"})
    p.supervisor = [{"created_date": "0", "id": 2, "name": "John"}]
    p.worker = {"created_date": "0", "id": 456, "name": "Sam"}

    FacelessPosition = Position & {"id": None, "supervisor": {"id"}, "worker": {"id"}}
    assert instruct.keys(FacelessPosition) == {"id", "supervisor", "worker"}

    OnlyPositionId = Position & "id"
    assert instruct.keys(OnlyPositionId) == {"id"}

    fp = FacelessPosition.from_json({"id": 1, "task_name": "Business Partnerships"})
    fp.supervisor = [{"created_date": "0", "id": 2, "name": "John"}]
    assert fp.supervisor[0].name is None
    assert fp.supervisor[0].id == 2
    fp.worker = {"created_date": "0", "id": 456, "name": "Sam"}
    assert asjson(fp) == {"id": 1, "supervisor": [{"id": 2}], "worker": {"id": 456}}
    fp.worker = Person(789, "abxdef", "0")
    assert asjson(fp) == {"id": 1, "supervisor": [{"id": 2}], "worker": {"id": 789}}
    assert isinstance(fp.worker, Person)
    assert isinstance(fp.worker, Person & "id")
    # Allow us to check the exact type of the subtraction is the same:
    assert instruct.public_class(fp.worker, preserve_subtraction=True) is (Person & "id")
    assert instruct.public_class(fp.worker, preserve_subtraction=True) is not Person


def test_skip_keys_coerce_classmethod() -> None:
    class Person(Base):
        id: int
        name: str
        created_date: str

        @classmethod
        def parse(cls, item):
            assert cls is d, "class mismatch!"
            return d(**item)

        @classmethod
        def check_class(cls, expected_clss):
            return instruct.public_class(cls, preserve_subtraction=True) is expected_clss

    d = Person

    class Position(Base):
        id: int
        supervisor: Tuple[Person, ...]
        worker: Person
        task_name: str

        __coerce__ = {
            "supervisor": (List[Dict[str, Union[int, str]]], Person.from_many_json),
            "worker": (Dict[str, Union[int, str]], Person.parse),
        }

        @property
        def some_prop(self):
            if "task_name" in type(self):
                return self.task_name
            return None

        @classmethod
        def convert_to_person(cls, item):
            if not isinstance(item, Person):
                item = Person.from_json(item)
            return item

    p = Position.from_json({"id": 1, "task_name": "Business Partnerships"})
    p.supervisor = [{"created_date": "0", "id": 2, "name": "John"}]
    p.worker = {"created_date": "0", "id": 456, "name": "Sam"}

    FacelessPosition = Position & {"id": None, "supervisor": {"id"}, "worker": {"id"}}
    FacelessPerson = Person & {"id"}
    assert FacelessPerson is FacelessPosition._slots["worker"]
    fp = FacelessPosition.from_json({"id": 1, "task_name": "Business Partnerships"})
    fp.supervisor = [{"created_date": "0", "id": 2, "name": "John"}]
    assert fp.supervisor[0].name is None
    assert fp.supervisor[0].id == 2
    fp.worker = {"created_date": "0", "id": 456, "name": "Sam"}
    assert len(fp.worker) == 1
    assert "name" not in fp.worker
    assert isinstance(fp.worker, FacelessPerson)
    assert asjson(fp) == {"id": 1, "supervisor": [{"id": 2}], "worker": {"id": 456}}
    assert (
        FacelessPosition.__coerce__["worker"][1]({"created_date": "0", "id": 456, "name": "Sam"})
        == fp.worker
    )
    assert fp.some_prop is None
    assert d is Person
    assert fp.worker.check_class(FacelessPerson)

    # This makes use of replace_class_references:
    #  We will replace Person in the convert_to_person function with the FacelessPerson
    #  class reference.
    bart = FacelessPosition.convert_to_person({"created_date": "0", "id": 912, "name": "Bart"})
    assert isinstance(bart, FacelessPerson)

    p = Position.from_json({"id": 1, "task_name": "Business Partnerships"})
    p.supervisor = [{"created_date": "0", "id": 2, "name": "John"}]
    p.worker = {"created_date": "0", "id": 456, "name": "Sam"}
    assert Person.to_json(p) == {
        "id": 1,
        "supervisor": [{"created_date": "0", "id": 2, "name": "John"}],
        "task_name": "Business Partnerships",
        "worker": {"created_date": "0", "id": 456, "name": "Sam"},
    }

    with pytest.raises(instruct.exceptions.ClassCreationFailed) as exc:
        FacelessPosition(farts=1)

    # ensure the human friendly name is in the class error.
    assert exc.match(inflection.titleize(instruct.public_class(FacelessPosition).__name__))


def test_skip_keys_keys():
    class Person(Base):
        id: int
        name: str
        created_date: str

    NamelessPerson = Person - "name"

    class Position(Base):
        id: int
        supervisor: Tuple[Person, ...]
        worker: Person
        task_name: str
        hierarchy: Tuple[Person, NamelessPerson]

        __coerce__ = {
            "supervisor": (List[Dict[str, Union[int, str]]], Person.from_many_json),
            "worker": (Dict[str, Union[int, str]], Person.from_json),
        }

    FacelessPosition = Position & {"id": None, "supervisor": {"id"}, "worker": {"id"}}
    assert tuple(instruct.keys(FacelessPosition)) == ("id", "supervisor", "worker")
    assert tuple(instruct.keys(FacelessPosition, "supervisor")) == ("id",)
    assert tuple(instruct.keys(FacelessPosition, "worker")) == ("id",)

    assert instruct.keys(FacelessPosition, "hierarchy") == {
        Person - "name": instruct.keys(Person - "name"),
        Person: instruct.keys(Person),
    }


def test_public_class():
    class Person(Base):
        id: int
        name: str
        created_date: str

    # ARJ: Anonymous bindings like this
    # means that public_class will always go to the parent class type:
    ForeignPerson = Person - {"id"}
    m = ForeignPerson - {"created_date"}
    n = Person - {"id", "created_date"}
    assert (m) is (n)
    # ARJ: However, if you do class ForeignPerson(Person - {"id"}): ...
    # it will stop at ForeignPerson declaration.
    # This is because non-anonymous (i.e. via class ...) declarations
    # are considered public by default.

    class Position(Base):
        id: int
        supervisor: Tuple[Person, ...]
        worker: Person
        task_name: str
        sponsor: Union[ForeignPerson, Person]

        __coerce__ = {
            "supervisor": (List[Dict[str, Union[int, str]]], Person.from_many_json),
            "worker": (Dict[str, Union[int, str]], Person.from_json),
        }

    class NamelessPerson(Person - {"name"}):
        pass

    print(str(Person - {"name"}))

    TimelessSponsoredPosition = Position - {"sponsor": {"created_date"}}
    assert not NamelessPerson._skipped_fields

    me = Person(1, "Autumn", "N/A")
    assert instruct.public_class(me) is Person
    assert instruct.public_class(Person) is Person
    assert instruct.public_class(Person - {"name"}) is Person
    assert instruct.public_class((Person - {"name"})(**me)) is Person
    assert instruct.public_class(Position, "worker") is Person
    assert instruct.public_class(Position, "sponsor", preserve_subtraction=True) == (
        ForeignPerson,
        Person,
    )
    assert instruct.public_class(Position, "sponsor", 0, preserve_subtraction=True) is ForeignPerson
    assert instruct.public_class(Position, "sponsor", 1, preserve_subtraction=True) is Person
    assert instruct.public_class(
        TimelessSponsoredPosition, "sponsor", preserve_subtraction=True
    ) == (ForeignPerson - {"created_date"}, Person - {"created_date"})
    assert (
        instruct.public_class(TimelessSponsoredPosition, "sponsor", preserve_subtraction=False)
        is Person
    )
    assert instruct.public_class(Position, "sponsor") is Person
    with pytest.raises(AttributeError):
        instruct.public_class(Position, "sponsor", "foobar")
    with pytest.raises(ValueError):
        assert instruct.public_class(Position, "worker", "nonexistent") is Person
    # ARJ: Broken for now due to out-of-order evaluation
    # with pytest.raises(IndexError):
    #     assert instruct.public_class(Position, "sponsor", 1) is Person
    # Note this difference:
    # This is because there was an inheritance declaration of a new class inheriting the
    # skipped type, making it distinct
    assert instruct.public_class(NamelessPerson) is NamelessPerson
    assert not NamelessPerson._skipped_fields
    assert "name" not in NamelessPerson._slots


def test_optional_keys():
    class Q(SimpleBase):
        y: int

    class P(SimpleBase):
        s: Optional[Q]

    assert instruct.show_all_fields(P) == {"s": {"y": None}}
    assert instruct.keys(P, "s") == {"y"}
    assert instruct.keys(P) == {"s"}


def test_absurd_custom_collections():
    """
    Currently we've no way of apply skip keys to a mapping type thaat's overridden
    like below. As a note, it escapes the current checks, allowing for some absurdities

    The cause is that inheriting something like Dict[str, str] means the original
    information of Dict[str, str] is lost (except inside the field ``__orig_bases__``)

    We could consider enforcing it by extracting out from ``__orig_bases__``, however that field
    is meant for Generics, which normally you'd do the decent thing of:

    class SomeCustomMapping(Dict[T, U]):
        ...

    class Foo:
        mapping: SomeCustomMapping[str, Union[Item, Tuple[str, ...]]]
    """

    class Item(Base):
        field: str

    _SomeCustomMapping = Dict[str, Union[Item, Tuple[str, ...]]]

    class SomeCustomMapping(_SomeCustomMapping):
        __slots__ = ()

    class Foo(SimpleBase):
        mapping: SomeCustomMapping
        __coerce__ = {"mapping": (str, lambda obj: SomeCustomMapping(json.loads(obj)))}

    # Absurdity #1 - class is same class
    assert Foo - {"mapping": {"field"}} is Foo

    # Absurdity #2 - should explode (fail type check)
    f = Foo("[[1, 2]]")
    assert f.mapping.keys() == {1}

    with pytest.raises(TypeError):
        # Absurdity #3
        # It basically rejects a valid assignment:
        f.mapping = {"Bar": Item("abc")}


def test_annotated_constants():
    class Item(SimpleBase):
        field1: Annotated[str, NoPickle]
        field2: Annotated[str, NoJSON]
        field3: Annotated[str, NoIterable]
        field4: Annotated[str, NoJSON, NoPickle]
        field5: Annotated[str, NoIterable, NoJSON]

    i = Item("a", "b", "c", "d", "e")
    assert AtomicMeta.to_json(i)[0] == {"field1": "a", "field3": "c"}
    assert i.__reduce__()[-1] == {"field2": "b", "field3": "c", "field5": "e"}
    assert dict(i) == {"field1": "a", "field2": "b", "field4": "d"}
    assert i._asdict() == {
        "field1": "a",
        "field2": "b",
        "field3": "c",
        "field4": "d",
        "field5": "e",
    }
    assert i._astuple() == ("a", "b", "c", "d", "e")


def test_annotated_range():
    class Item(Base):
        field1: Annotated[str, "foobar blech"]
        field2: Annotated[int, Range(0, 256)]
        field3: Annotated[
            Union[int, float],
            Range(0, 256, type_restrictions=int),
            Range(0, 1, type_restrictions=float),
        ]

    item = Item("a", 255, 0.5)
    with pytest.raises(TypeError) as exc:
        item.field2 = 256
    print(exc.value)
    with pytest.raises(TypeError) as exc:
        item.field2 = -1
    print(exc.value)

    item.field2 = 0
    item.field3 = 0.9999
    with pytest.raises(TypeError) as exc:
        item.field3 = 1.5
    print(exc.value)
    with pytest.raises(TypeError) as exc:
        item.field3 = -1.5
    print(exc.value)
    item.field3 = 255
    with pytest.raises(TypeError) as exc:
        item.field3 = 256
    print(exc.value)
    with pytest.raises(ClassCreationFailed) as exc:
        Item("a", 256, 10.5)
    assert len(exc.value.errors) == 2
    assert isinstance(exc.value.errors[0], RangeError)
    assert isinstance(exc.value.errors[1], RangeError)
    print(exc.value)
    with pytest.raises(TypeError) as exc:
        Item(field3="x")
    print(exc.value)
    with pytest.raises(TypeError) as exc:
        Item(1)
    print(exc.value)


def test_with_defaults(monkeypatch, mocker):
    now = datetime.datetime.utcnow()

    fake_datetime = mocker.MagicMock()
    fake_datetime.utcnow = mocker.MagicMock()
    fake_datetime.utcnow.return_value = now

    class Foo(SimpleBase):
        id: int
        created_date: datetime.datetime
        baz: str

        def _set_defaults(self):
            self.id = -1
            self.created_date = datetime.datetime.utcnow()
            return super()._set_defaults()

    with monkeypatch.context() as c:
        c.setattr(datetime, "datetime", fake_datetime)
        f = Foo()
    assert f.id == -1
    assert f.created_date == now
    assert f.baz is None

    class Bar(Foo):
        def _set_defaults(self):
            self.baz = "barz!"
            return super()._set_defaults()

    with monkeypatch.context() as c:
        c.setattr(datetime, "datetime", fake_datetime)
        b = Bar()
    assert b.baz == "barz!"
    assert b.id == -1
    assert b.created_date == now


def test_empty():
    class Foo(SimpleBase):
        pass

    assert list(Foo()) == []


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.8 or higher")
def test_using_builtin_unions():
    class TestUnion(SimpleBase):
        field: str | int

    TestUnion("foo")
    TestUnion(1)
    with pytest.raises(TypeError):
        TestUnion(1.5)


def test_with_init_subclass():
    Registry = {}

    class Foo(SimpleBase):
        def __init_subclass__(cls, *, swallow: str = None, **kwargs):
            print("ARRH", cls)
            Registry[cls] = swallow
            super().__init_subclass__()

    f = Foo()  # noqa

    class Bar(Foo, swallow="Barn!"): ...

    assert Bar in Registry
    assert Registry[Bar] == "Barn!"
    assert len(Registry) == 1

    class BarBar(Bar, swallow="Farter"):
        def __init_subclass__(cls, **kwargs):
            return

    assert len(Registry) == 2

    class BreakChainBar(BarBar): ...

    assert len(Registry) == 2


def test_simple_generics():
    T = TypeVar("T")
    assert isinstance(T, TypeVar)

    class Foo(SimpleBase):
        field: T

    assert str(Foo).endswith(f"Foo[{T!s}]")

    assert isinstance(Foo._slots["field"], TypeVar)
    assert Foo.__parameters__ == (T,)

    # with pytest.raises(TypeError):
    assert public_class(Foo(1)) is Foo[Any]
    assert str(public_class(Foo(1))) == "Foo[typing.Any]"

    cls = Foo[int]
    assert Foo[int] is cls
    assert isinstance(cls(1).field, int)
    assert get_type_hints(cls)["field"] is int

    U = TypeVar("U", default=str)

    class Bar(SimpleBase, Generic[U]):
        field: U

    assert isinstance(Bar._slots["field"], TypeVar)
    assert Bar.__parameters__ == (U,)

    cls = Bar[int]
    assert isinstance(cls(1).field, int)
    assert get_type_hints(cls)["field"] is int

    with pytest.raises(TypeError):
        cls[str]

    any_instance = Bar("foobar")
    default_cls = public_class(any_instance)
    assert default_cls.__default__ == (str,)
    assert default_cls is Bar[str], f"{default_cls}, {Bar[str]}"
    print(str(public_class(any_instance)))
    assert any_instance.field == "foobar"
    assert isinstance(any_instance, Bar[str])


def test_annotated_mapping():
    class Test(SimpleBase, mapping=True):
        public: str
        secret: Annotated[bytes, NoIterable]

    t = Test("foo!", b"my-secret!")
    assert t.secret == b"my-secret!"
    assert dict(t) == {"public": "foo!"}
    assert not any(key == "secret" for key, value in t.items())
    assert any(key == "public" for key, value in t.items())
    just_secret = Test & {"secret"}

    t2 = just_secret(b"my-secret-2")
    assert t2.secret == b"my-secret-2"
    assert dict(t2) == {}
    assert "secret" not in t2.keys()
    assert not any(key == "secret" for key, value in t2.items())
    assert "secret" in t2
    assert "secret" in public_class(t2, preserve_subtraction=True)
    assert "secret" in tuple(public_class(t2, preserve_subtraction=True))


class TestNoPickle(SimpleBase, mapping=True):
    name: str
    secret: Annotated[bytes, NoPickle]


def test_no_pickle():
    t = TestNoPickle("1", b"my-secret!")

    assert dict(t) == {"name": "1", "secret": b"my-secret!"}

    buf = pickle.dumps(t)

    t2 = pickle.loads(buf)
    assert not t2.secret
    assert t2.name == "1"


def test_autorepr():
    class Test(SimpleBase, autorepr=True):
        name: str

    assert repr(Test("itm")).startswith("Test(name=")
