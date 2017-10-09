from typing import Union
from instruct import Base, add_event_listener
import timeit

test_statement = '''
t.name_or_id = 1
'''

class TestH(Base, history=True):
    __slots__ = {
        'name_or_id': Union[int, str]
    }

    def __init__(self, **kwargs):
        self.name_or_id = 1
        super().__init__(**kwargs)


class Test(Base):
    __slots__ = {
        'name_or_id': Union[int, str]
    }

    def __init__(self, **kwargs):
        self.name_or_id = 1
        super().__init__(**kwargs)

Test(name_or_id=1).clear()

class TestOptimized(Base, fast=True):
    __slots__ = {
        'name_or_id': Union[int, str]
    }

    def __init__(self, **kwargs):
        self.name_or_id = 1
        super().__init__(**kwargs)


class ComplexTest(Base):
    __slots__ = {
        'id': int,
        'name': str,
        'type': int,
        'value': float
    }


    @add_event_listener('id')
    def _handle_id(self, old, new):
        pass

    def __init__(self, **kwargs):
        self.id = 0
        self.name = ''
        self.type = -1
        self.value = 0.1
        super().__init__(**kwargs)

def main():
    ttl = timeit.timeit('t = Test(name_or_id="autumn")', setup='from __main__ import Test')
    per_round_ms = (ttl / timeit.default_number) * 1000000
    print('Overhead of allocation, one field, safeties on: {:.2f}us'.format(per_round_ms))

    ttl = timeit.timeit('t = Test(name_or_id="autumn")', setup='from __main__ import TestOptimized as Test')
    per_round_ms = (ttl / timeit.default_number) * 1000000
    print('Overhead of allocation, one field, safeties off: {:.2f}us'.format(per_round_ms))

    print('Overhead of setting a field:')
    ttl = timeit.timeit(test_statement, setup='from __main__ import Test;t = Test()')
    per_round_ms = (ttl / timeit.default_number) * 1000000
    print('Test with safeties: {:.2f} us'.format(per_round_ms))

    ttl = timeit.timeit(test_statement, setup='from __main__ import TestOptimized as Test;t = Test()')
    per_round_ms = (ttl / timeit.default_number) * 1000000
    print('Test without safeties: {:.2f} us'.format(per_round_ms))

    print('Overhead of clearing/setting')
    ttl = timeit.timeit(
        't.clear();t.name_or_id = 1', setup='from __main__ import Test;t = Test(name_or_id="autumn")')
    per_round_ms = (ttl / timeit.default_number) * 1000000
    print('Test with safeties: {:.2f} us'.format(per_round_ms))

    ttl = timeit.timeit(
        't.clear();t.name_or_id = 1', setup='from __main__ import TestOptimized as Test;t = Test(name_or_id="autumn")')
    per_round_ms = (ttl / timeit.default_number) * 1000000
    print('Test without safeties: {:.2f} us'.format(per_round_ms))


if __name__ == '__main__':
    import argparse
    import random
    from pycallgraph import PyCallGraph
    from pycallgraph.output import GraphvizOutput
    parser = argparse.ArgumentParser()
    parser.set_defaults(mode=None)
    subparsers = parser.add_subparsers()
    benchmark = subparsers.add_parser('benchmark')
    benchmark.set_defaults(mode='benchmark')
    callgraph = subparsers.add_parser('callgraph')
    callgraph.set_defaults(mode='callgraph')
    callgraph.add_argument('filename', default='callgraph.png', nargs='?')

    args = parser.parse_args()
    if not args.mode:
        raise SystemExit('Use benchmark or callgraph')
    if args.mode == 'benchmark':
        main()
    if args.mode == 'callgraph':
        with PyCallGraph(GraphvizOutput(output_file='callgraph.png')):
            for _ in range(1000):
                try:
                    item = ComplexTest(
                        id=random.randint(1, 232), name=random.choice(
                             (('test',) * 10) + (-1, None)), value=random.random())
                except Exception:
                    pass


