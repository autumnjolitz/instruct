from typing import Union
from instruct import Base, clear
import timeit

clear

test_statement = """
t.name_or_id = 1
"""


class TestH(Base, history=True):
    name_or_id: Union[int, str]

    def __init__(self, **kwargs):
        self.name_or_id = 1
        super().__init__(**kwargs)


class Test(Base):
    name_or_id: Union[int, str]

    def __init__(self, **kwargs):
        self.name_or_id = 1
        super().__init__(**kwargs)


class TestOptimized(Base, fast=True):
    name_or_id: Union[int, str]

    def __init__(self, **kwargs):
        self.name_or_id = 1
        super().__init__(**kwargs)


class ComplexTest(Base):
    id: int
    name: str
    type: int
    value: float

    def __init__(self, **kwargs):
        self.id = 0
        self.name = ""
        self.type = -1
        self.value = 0.1
        super().__init__(**kwargs)


class Next(ComplexTest):
    next: int


def main(count=1_000_000):
    ttl = timeit.timeit(
        't = Test(name_or_id="name")', setup="from __main__ import Test", number=count
    )
    print("Overhead of allocation")
    per_round_ms = (ttl / count) * count
    print("one field, safeties on: {:.2f} us".format(per_round_ms))

    ttl = timeit.timeit(
        't = Test(name_or_id="name")',
        setup="from __main__ import TestOptimized as Test",
        number=count,
    )
    per_round_ms = (ttl / count) * count
    print("one field, safeties off: {:.2f} us".format(per_round_ms))

    print("Overhead of setting a field")
    ttl = timeit.timeit(test_statement, setup="from __main__ import Test;t = Test()")
    per_round_ms = (ttl / count) * count
    print("Test with safeties: {:.2f} us".format(per_round_ms))

    ttl = timeit.timeit(
        test_statement,
        setup="from __main__ import TestOptimized as Test;t = Test()",
        number=count,
    )
    per_round_ms = (ttl / count) * count
    print("Test without safeties: {:.2f} us".format(per_round_ms))

    print("Overhead of clearing/setting")
    ttl = timeit.timeit(
        "clear(t);t.name_or_id = 1",
        setup='from __main__ import Test, clear;t = Test(name_or_id="name")',
        number=count,
    )
    per_round_ms = (ttl / count) * count
    print("Test with safeties: {:.2f} us".format(per_round_ms))

    ttl = timeit.timeit(
        "clear(t);t.name_or_id = 1",
        setup='from __main__ import TestOptimized as Test,clear;t = Test(name_or_id="name")',
        number=count,
    )
    per_round_ms = (ttl / count) * count
    print("Test without safeties: {:.2f} us".format(per_round_ms))


if __name__ == "__main__":
    import argparse
    import random

    try:
        from pycallgraph import PyCallGraph  # type:ignore
        from pycallgraph.output import GraphvizOutput  # type:ignore
    except ImportError:
        PyCallGraph = None

    parser = argparse.ArgumentParser()
    parser.set_defaults(mode=None)
    subparsers = parser.add_subparsers()
    benchmark = subparsers.add_parser("benchmark")
    benchmark.set_defaults(mode="benchmark")
    benchmark.add_argument("count", default=1_000_000, type=int, nargs="?")
    if PyCallGraph is not None:
        callgraph = subparsers.add_parser("callgraph")
        callgraph.set_defaults(mode="callgraph")
        callgraph.add_argument("filename", default="callgraph.png", nargs="?")

    args = parser.parse_args()
    if not args.mode:
        raise SystemExit("Use benchmark or callgraph")
    if args.mode == "benchmark":
        main(args.count)
    if PyCallGraph and args.mode == "callgraph":
        names = [random.choice((("test",) * 10) + (-1, None)) for _ in range(1000)]
        ids = [random.randint(1, 232) for _ in range(1000)]
        values = [random.random() for _ in range(1000)]
        with PyCallGraph(GraphvizOutput(output_file="callgraph.png")):
            for i in range(1000):
                try:
                    item = ComplexTest(id=ids[i], name=names[i], value=values[i])
                except Exception:
                    pass
