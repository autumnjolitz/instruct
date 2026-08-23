from enum import IntFlag

import pytest

import instruct
from instruct import ParameterKind, ParameterVisibility, _, data_class, field, validate


class Fart(IntFlag):
    FOO = 1
    BART = 2
    BAZ = 4

    def parse(
        cls,
        o,
        /,
    ):
        match o:
            case str(s) if (maybe_fart := getattr(cls, s.upper(), None)) is not None:
                return maybe_fart
            case str(s):
                raise ValueError(f"Unknown field in {cls.__name__}: {s!r}")
            case int():
                return cls(int)
            case _ as wtf:
                raise TypeError(f"Unrecognized type for {cls.__name__}: {wtf!r} (a {type(wtf)})")


@data_class
class MutableItem:
    id: int = -1
    name: str = "default"
    flags: Fart
    config: dict[str, str] = {}

    _.parameter_kind(
        (id, name, config),
        ParameterKind.POSITIONAL_ONLY,
        ParameterKind.POSITIONAL_OR_KEYWORD,
        ParameterKind.KEYWORD_ONLY,
    )
    _.parameter_visibility(
        flags,  # noqa: F821
        ParameterVisibility.HIDDEN,
    )

    assert isinstance(flags, instruct.Field)  # noqa: F821
    _.add_converter(flags, (int, str), Fart)  # noqa:F821
    _.add_converter(id, str, int)

    def __post_init__(self):
        self.flags = Fart(0)

    @_.add_event_listener(
        (id, name),
    )
    def _mark_ready(self, new_id, new_name):
        if self.flags is None:
            return
        match (new_id, new_name):
            case (-1, _):
                pass
            case (int(), str()):
                self.flags |= Fart.BAZ

    assert __class_definition__["listeners"]  # noqa:F821
    assert isinstance(flags, instruct.Field)  # noqa:F821


assert tuple(MutableItem.__class_definition__["listeners"])


@data_class(frozen=True)
class ImmutableItem(MutableItem):
    pass


assert tuple(ImmutableItem.__definitions__) == ("id", "name", "flags", "config")


class AnotherImmutableItem(MutableItem, frozen=True): ...


assert AnotherImmutableItem.__class_definition__["options"]["frozen"]


class ImmutableBeta(AnotherImmutableItem):
    c: int = -1


assert ImmutableBeta.__class_definition__["options"]["frozen"]


def test_suggest_default_value():
    @data_class(frozen=True)
    class A:
        id: int = -1

    with pytest.raises(
        ValueError, match="non-default argument follows default argument"
    ) as exc_info:

        class B(A):
            value: int

    assert getattr(exc_info.value, "__notes__", None)
    (
        *rest,
        hint,
    ) = exc_info.value.__notes__
    assert hint.startswith("Assign a default value to")
    assert hint.endswith("B.value")

    class B(A):
        value: int = -1

    assert B.__class_definition__["options"]["frozen"]
    print(B.__new__, "XXX")

    assert tuple(B()) == (-1, -1)
    assert tuple(b := B(1, 2)) == (1, 2)
    assert (b.id, b.value) == (1, 2)

    class Bmut(B, frozen=False):
        pass

    b = Bmut(1, 2)
    assert type(b).__slots__ == ("id", "value")
    b.id = -1
    b.value = "str"
    with pytest.raises(TypeError):
        validate(b)


def test_mutable_item():
    a = MutableItem()
    assert type(a).__slots__ == ("id", "name", "flags", "config"), MutableItem.__slots__
    assert a.id == -1
    assert (a.id, a.name, a.flags, a.config) == (-1, "default", Fart(0), {})
    b = MutableItem(10, "Foo Man", config={"Yes": "No"})
    assert (b.id, b.name, b.flags, b.config) == (10, "Foo Man", Fart.BAZ, {"Yes": "No"})


def test_mutable_coerce():
    a = MutableItem()
    a.id = "banana"
    with pytest.raises(TypeError):
        validate(a)


def test_class_subtraction():
    cls = ImmutableItem - "id"
    assert len(cls.__definitions__) + 1 == len(ImmutableItem.__definitions__)


def test_frozen_item():
    i = ImmutableItem()
    ip = AnotherImmutableItem()
    assert tuple(i) == (-1, "default", Fart(0), {})
    i2 = ImmutableItem(12, "foobar", config={"yay": "poop"})
    i3 = ImmutableItem(12, "foobar", config={"yay": "poop"})
    i2p = AnotherImmutableItem(12, "foobar", config={"yay": "poop"})
    i3p = AnotherImmutableItem(12, "foobar", config={"yay": "poop"})
    assert i2.flags is Fart.BAZ
    assert i2p.flags is Fart.BAZ
    assert i2 != i
    assert i2 == i3 != i
    assert i2p == i3p != ip
    assert i2 != i2p
    assert tuple(i2) == tuple(i2p)
    print(i, i2)
    print(i3._replace(id=2, name="yap", config={}))
    print(i2.__hash__)


def test_frozen_slicing():
    i2 = ImmutableItem(12, "foobar", config={"yay": "poop"})
    print(f"Fart: {i2[:1]}")


def test_with_field():
    @data_class(frozen=True)
    class A:
        id: int
        name: str

    assert hasattr(A, "__hash__")
    assert callable(A.__hash__)

    class A_Tagged(A):
        tags: list[str] = field(default_factory=(lambda: ["first tag"]), hash=False, compare=False)
        assert tags.hash is False

    assert A_Tagged.__class_definition__["options"]["frozen"]
    assert not A_Tagged.__definitions__["tags"].hash
    assert callable(A_Tagged.__hash__)
    a = A(1, "Mx. Foo")
    a_2 = A(2, "Mx. Bar")
    b = A_Tagged(1, "Mx. Foo")
    c = A_Tagged(1, "Mx. Foo")
    assert a != a_2
    assert b == c
    assert hash(a) != hash(b)
    assert hash(b) == hash(c)
    b.tags.append("ignored")
    c.tags.append("not that")
    assert hash(a) != hash(b)
    assert hash(b) == hash(c)
    assert b != c


def test_with_custom_super():
    @data_class
    class A:
        __slots__ = ("_db",)

        id: int
        name: str

        def __init__(self, *args, db, **kwargs):
            self._db = db
            super().__init__(*args, **kwargs)

    fake_db = object()
    a = A(1, "foo", db=fake_db)
    assert a._db is fake_db


def test_with_custom_super_inherit():
    @data_class
    class A:
        __slots__ = ("_db",)

        id: int
        name: str

        def __init__(self, *args, db, **kwargs):
            print("inside A init")
            self._db = db
            print(f"calling super on {__class__} for istance {self!r}")
            assert isinstance(self, __class__)
            super().__init__(*args, **kwargs)

    fake_db = object()
    a = A(1, "foo", db=fake_db)
    assert a._db is fake_db

    class B(A, frozen=True):
        pass

    print("create a b plz")
    b = B(1, "a", db=fake_db)
    assert b._db is fake_db


def test_with_custom_slots():
    @data_class(frozen=False)
    class A:
        __slots__ = ("_db",)

        id: int
        name: str

        def __post_init__(self, *, db, **kwargs):
            self._db = db

    @data_class(frozen=False)
    class B:
        __slots__ = ("_db",)

        id: int
        name: str

        def __post_init__(self, *, db, **kwargs):
            self._db = db

    class C(A, frozen=True): ...

    fake_db = object()
    a = A(1, "foo", db=fake_db)
    c = C(1, "foo", db=fake_db)
    assert a._db is fake_db
    assert "_db" not in A.__annotations__
    b = B(1, "foo", db=fake_db)
    assert b._db is fake_db
    assert "_db" not in B.__annotations__
    assert c._db is fake_db
    assert c.__definitions__ == b.__definitions__ == c.__definitions__
    assert c.__class_definition__["options"]["frozen"]


def test_call_count(mocker, monkeypatch):
    with monkeypatch.context() as c:
        DataTypeFactoryNew = mocker.MagicMock(side_effect=instruct.DataClassTypeFactory.__new__)
        data_class = mocker.MagicMock(side_effect=instruct.data_class)
        c.setattr(instruct.DataClassTypeFactory, "__new__", DataTypeFactoryNew)
        c.setattr(instruct, "data_class", data_class)

        @data_class(slots=False)
        class A:
            a: str
            b: int
            c: dict[str, str]

        assert (DataTypeFactoryNew.call_count, data_class.call_count) == (1, 1)
        assert A.__class_definition__["options"]["slots"] is False

        DataTypeFactoryNew.reset_mock()
        data_class.reset_mock()

        @data_class(slots=True)
        class B:
            a: str
            b: int
            c: dict[str, str]

        assert (DataTypeFactoryNew.call_count, data_class.call_count) == (2, 1)

        DataTypeFactoryNew.reset_mock()
        data_class.reset_mock()

        class C(A):
            pass

        assert A.__class_definition__["options"]["slots"] is False
        assert C.__class_definition__["options"]["slots"] is False
        assert (DataTypeFactoryNew.call_count, data_class.call_count) == (1, 1)

        DataTypeFactoryNew.reset_mock()
        data_class.reset_mock()

        a = A("a", 3, {})
        c = C("b", 2, {})

        # pathological case:
        # we have a chain of non-slotted classes as parents.
        # which will be upcoerced to slotted versions in D's base chain:
        effective_cls_mro_len = len(C.mro()[:-1]) + 1  # exclude object from the effective chain

        class D(C, slots=True): ...

        # So we will define D and len(unslotted bases)
        actual_effective_mro_len = len(D.mro()[:-1])
        assert actual_effective_mro_len == 3
        assert D.__class_definition__["options"]["slots"] is True
        assert not hasattr(D("a", 1, {"a": "b"}), "__dict__")
        assert (DataTypeFactoryNew.call_count, data_class.call_count) == (
            2 * actual_effective_mro_len,
            1 * actual_effective_mro_len,
        )

        d = D("d", 4, {"y": "q"})
        assert isinstance(d, A)
        assert isinstance(d, C)
        assert not hasattr(d, "__dict__")

        _, slottedC, *_ = D.mro()
        assert issubclass(slottedC, C), slottedC.mro()
        assert issubclass(D, A)

        DataTypeFactoryNew.reset_mock()
        data_class.reset_mock()

        class F(C, frozen=True):
            sid: str

        assert F.__class_definition__["options"]["slots"] is True
        assert F.__class_definition__["options"]["frozen"] is True
        assert (DataTypeFactoryNew.call_count, data_class.call_count) == (6, 3)

        f = F("f", 5, {"y": "q"}, "565")
        assert instruct.astuple(f) == ("f", 5, {"y": "q"}, "565")


if __name__ == "__main__":
    for attr in tuple(locals()):
        value = locals()[attr]
        if attr.startswith("test_") and callable(value):
            value()
