import json
from typing import Union, List, Tuple, Optional, Dict
from enum import Enum
import datetime
import pickle
from collections.abc import Mapping

import pytest

from instruct import (
    Base,
    add_event_listener,
    ClassCreationFailed,
    OrphanedListenersError,
    handle_type_error,
)


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

    def __init__(self, **kwargs):
        self.id = 0
        super().__init__(**kwargs)

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
    l1 = LinkedFields(id=2, name='Autumn')
    assert len(l1) == 2
    assert isinstance(l1, Mapping)


def test_pickle():
    l1 = LinkedFields(id=2, name='Autumn')
    data = pickle.dumps(l1)
    l2 = pickle.loads(data)
    assert l1 == l2


def test_partial_pickle():
    l1 = LinkedFields(id=2)
    assert l1.name is None
    data = pickle.dumps(l1)
    l2 = pickle.loads(data)
    assert l1 == l2


def test_json():
    l1 = LinkedFields(id=2, name='Autumn')
    data = json.dumps(l1.to_json())
    l2 = LinkedFields(**json.loads(data))
    assert l1 == l2
    l3 = LinkedFields.from_json(l1.to_json())
    assert l1 == l2 == l3


def test_json_complex():
    class SubItems(Base):
        __slots__ = {"value": int}

    class Item(Base):
        __slots__ = {"collection": List[SubItems]}
        __coerce__ = {
            "collection": (List[dict], lambda items: [SubItems(**item) for item in items])
        }

    a = Item(collection=[{"value": 1}, {"value": -1}])
    a_json = a.to_json()
    assert isinstance(a_json["collection"][0], dict)
    assert isinstance(a_json["collection"][1], dict)
    assert isinstance(a["collection"][0], SubItems)


def test_mapping_immutability():
    class Embedded(Base):
        __slots__ = {"d": str}

    class Item(Base):
        __slots__ = {"data": Dict[str, Embedded]}

    i = Item(data={"foo": Embedded(d="bar")})
    data = i.to_json()
    assert isinstance(i.data["foo"], Embedded)
    del data


def test_coercion():
    l = LinkedFields(id='2', name='Autumn')
    assert l.id == 2
    l.id = "5"
    assert l.id == 5


def test_event_listener():
    l = LinkedFields(id=2, name='Autumn')
    l.id = -1
    assert l.name == "invalid"


def test_derived_klass():
    assert isinstance(NestedData._columns['nested'], type)
    item = NestedData(id=1, nested={'field': 'autumn'})
    assert item.nested.field == 'autumn'
    with pytest.raises(TypeError):
        item.nested.field = 1


def test_derived_equivalence():
    item = NestedData(id=1, nested={'field': 'autumn'})
    item_alt = NestedDataAlt(id=1, nested={'field': 'autumn'})
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
    t = Data(field='autumn')
    t.field = 'not autumn'
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
    t = Data(field="autumn")
    t.field = "not autumn"
    t.field = "autumn"
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
    t.field = 'Autumn'
    assert t.is_dirty, 'Item should be dirty - we added a property!'
    t.field = 0
    assert not t.is_dirty, "Item is now reset"


def test_reset():
    t = Data(field='Autumn')
    t.reset_changes()
    assert t.field == 'Autumn'
    assert not t.is_dirty


def test_fast_setter():
    class FastData(Base, fast=True):
        __slots__ = {"a": int, "bar": str}

        @add_event_listener("a")
        def on_a_set(self, old, new):
            self.bar = str(new)

    f = FastData(a=1)
    assert f.bar == "1"


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


def test_readme():
    class Member(Base):
        __slots__ = {"first_name": str, "last_name": str, "id": int}

        def __init__(self, **kwargs):
            self.first_name = self.last_name = ""
            self.id = -1
            super().__init__(**kwargs)

    class Organization(Base, history=True):
        __slots__ = {
            "name": str,
            "id": int,
            "members": List[Member],
            "created_date": datetime.datetime,
        }

        __coerce__ = {
            "created_date": (str, lambda obj: datetime.datetime.strptime("%Y-%m-%d", obj)),
            "members": (list, lambda val: [Member(**item) for item in val]),
        }

        def __init__(self, **kwargs):
            self.name = ""
            self.id = -1
            self.members = []
            self.created_date = datetime.datetime.utcnow()
            super().__init__(**kwargs)

    data = {
        "name": "An Org",
        "id": 123,
        "members": [{"id": 551, "first_name": "Jinja", "last_name": "Ninja"}],
    }
    org = Organization(**data)
    assert org.members[0].first_name == "Jinja"
    org.name = "New Name"
    print(tuple(org.list_changes()))
    types = frozenset((type(x) for _, x in org))
    assert len(types) == 4 and type(None) not in types
    org.clear()
    assert frozenset((type(x) for _, x in org)) == {type(None)}


def test_invalid_kwargs():
    class Test(Base):
        __slots__ = {"foo": str, "bar": float, "blech": int}

    with pytest.raises(ClassCreationFailed) as e:
        Test(foo=1.2, bar=1, blech="2")
    assert len(e.value.errors) == 3
    print(e.value.to_json())


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
        Item(value=[1, 2])

    class SomeEnum(Enum):
        VALUE = "value"

    def parse(items):
        return [tuple(item) for item in items]

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

        __coerce__ = {"items": (List[dict], lambda items: [ComplextItem(**item) for item in items])}

    c = ComplextItem(value=[["a", 1], ["b", 2]], name="ab", type="value")
    assert c.value == [("a", 1), ("b", 2)]

    VectoredItems(items=[{"value": [["a", 1], ["b", 2]], "name": "ab", "type": "value"}])


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

        __coerce__ = {"items": (List[dict], lambda items: [ComplextItem(**item) for item in items])}

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
        if key in self.keys():
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
