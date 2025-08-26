from instruct import Base, public_class
from urllib.parse import urlsplit


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


def test_match_args():
    class MutableURL(Base):
        scheme: str
        netloc: str
        path: str
        query: str
        fragment: str

        @classmethod
        def parse(cls, url):
            return cls(**urlsplit(url)._asdict())

    assert MutableURL.__match_args__ == ("scheme", "netloc", "path", "query", "fragment")

    match MutableURL.parse("https://example.com/path?q=1#frag!"):
        case MutableURL(scheme="https") as m:
            assert m.query == "q=1"
            assert m.fragment == "frag!"
        case _ as wtf:
            assert False, f"What is this - {wtf!r}!~?!"

    match MutableURL.parse("https://example.com/path?q=1#frag!"):
        case MutableURL(_, "example.com"):
            pass
        case _ as wtf:
            assert False, f"What is this - {wtf!r}!~?!"
