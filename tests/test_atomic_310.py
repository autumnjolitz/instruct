from instruct import Base, public_class


def test_subtraction():
    class Foo(Base):
        a: tuple[int, ...]
        b: str | int
        c: str

    class FooGroup(Base):
        foos: list[Foo]

    cls = FooGroup - {"foos": {"a", "b"}}

    ModifiedFoo = public_class(cls, "foos", preserve_subtraction=True)

    assert tuple(ModifiedFoo) == ("c",)
