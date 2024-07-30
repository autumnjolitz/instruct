from __future__ import annotations

import sys
import timeit
from typing import Union

from instruct import SimpleBase, clear

if sys.version_info[:2] >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info[:2] >= (3, 11):
    from typing import assert_never
else:
    from typing_extensions import assert_never

clear

test_statement = """
t.name_or_id += 1
"""


class TestH(SimpleBase, history=True):
    name_or_id: Union[int, str]

    def __init__(self, **kwargs):
        self.name_or_id = 1
        super().__init__(**kwargs)


class Test(SimpleBase):
    name_or_id: Union[int, str]

    def __init__(self, **kwargs):
        self.name_or_id = 1
        super().__init__(**kwargs)


class TestOptimized(SimpleBase, fast=True):
    name_or_id: Union[int, str]

    def __init__(self, **kwargs):
        self.name_or_id = 1
        super().__init__(**kwargs)


class ComplexTest(SimpleBase):
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


US_IN_S: int = 1_000_000


def main(unit: Literal["ns", "us"] = "us", limit: int = 10_000):
    if "us" == unit:
        multiplier = 1
        fmt = "{:.2f}"
    elif "ns" == unit:
        multiplier = 1000
        fmt = "{:.0f}"
    else:
        assert_never(unit)
    ttl = timeit.timeit('t = Test(name_or_id="name")', number=limit, globals={"Test": Test})
    print("Overhead of allocation")
    per_round_us = (ttl * US_IN_S) / limit
    print("one field, safeties on: {} {}".format(fmt.format(per_round_us * multiplier), unit))

    ttl = timeit.timeit(
        't = TestOptimized(name_or_id="name")',
        number=limit,
        globals={"TestOptimized": TestOptimized},
    )
    per_round_us = (ttl * US_IN_S) / limit
    print("one field, safeties off: {} {}".format(fmt.format(per_round_us * multiplier), unit))

    unit = "ns"
    multiplier = 1_000
    fmt = "{:.0f}"

    print("Overhead of setting a field")
    ttl = timeit.timeit(test_statement, number=limit, globals={"t": Test()})
    per_round_us = (ttl * US_IN_S) / limit
    print("Test with safeties: {} {}".format(fmt.format(per_round_us * multiplier), unit))

    ttl = timeit.timeit(
        test_statement,
        number=limit,
        globals={
            "t": TestOptimized(),
        },
    )
    per_round_us = (ttl * US_IN_S) / limit
    print("Test without safeties: {} {}".format(fmt.format(per_round_us * multiplier), unit))

    print("Overhead of clearing/setting")
    ttl = timeit.timeit(
        "clear(t);t.name_or_id = 1",
        number=limit,
        globals={
            "t": Test(name_or_id="name"),
            "clear": clear,
        },
    )
    per_round_us = (ttl * US_IN_S) / limit
    print("Test with safeties: {} {}".format(fmt.format(per_round_us * multiplier), unit))

    ttl = timeit.timeit(
        "clear(t);t.name_or_id = 1",
        number=limit,
        globals={
            "t": TestOptimized(name_or_id="name"),
            "clear": clear,
        },
    )
    per_round_us = (ttl * US_IN_S) / limit
    print("Test without safeties: {} {}".format(fmt.format(per_round_us * multiplier), unit))


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
    benchmark.add_argument("unit", choices=["us", "ns"], default="us", nargs="?")
    assert main.__defaults__ is not None
    benchmark.add_argument("limit", type=int, default=main.__defaults__[-1], nargs="?")
    if PyCallGraph is not None:
        callgraph = subparsers.add_parser("callgraph")
        callgraph.set_defaults(mode="callgraph")
        callgraph.add_argument("filename", default="callgraph.png", nargs="?")

    args = parser.parse_args()
    if not args.mode:
        raise SystemExit("Use benchmark or callgraph")
    if args.mode == "benchmark":
        main(args.unit, args.limit)
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
