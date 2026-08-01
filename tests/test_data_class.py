from enum import IntFlag

import pytest

import instruct
from instruct import ParameterKind, _, data_class, validate


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
    _.parameter_kind(
        "flags",
        ParameterKind.HIDE,
    )
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


@data_class(immutable=True)
class ImmutableItem(MutableItem):
    pass


class AnotherImmutableItem(MutableItem, immutable=True):
    pass


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


def test_immutable_item():
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


def test_immutable_slicing():
    i2 = ImmutableItem(12, "foobar", config={"yay": "poop"})
    print(f"Fart: {i2[:1]}")


if __name__ == "__main__":
    test_mutable_item()
    test_mutable_coerce()
    test_class_subtraction()
    test_immutable_item()
    test_immutable_slicing()
