from typing import Union
from instruct import Base
import timeit

test_statement = '''
t.name_or_id = 1
'''


class Test(Base):
    __slots__ = {
        'name_or_id': Union[int, str]
    }

    def __init__(self, **kwargs):
        self.name_or_id = 1
        super().__init__(**kwargs)


class TestOptimized(Base, fast=True):
    __slots__ = {
        'name_or_id': Union[int, str]
    }

    def __init__(self, **kwargs):
        self.name_or_id = 1
        super().__init__(**kwargs)


def main():
    ttl = timeit.timeit('t = Test(name_or_id="ben")', setup='from __main__ import Test')
    per_round_ms = (ttl / timeit.default_number) * 1000000
    print('Overhead of allocation, one field, safeties on: {:.2f}ms'.format(per_round_ms))

    ttl = timeit.timeit('t = Test(name_or_id="ben")', setup='from __main__ import TestOptimized as Test')
    per_round_ms = (ttl / timeit.default_number) * 1000000
    print('Overhead of allocation, one field, safeties off: {:.2f}ms'.format(per_round_ms))

    print('Overhead of setting a field:')
    ttl = timeit.timeit(test_statement, setup='from __main__ import Test;t = Test()')
    per_round_ms = (ttl / timeit.default_number) * 1000000
    print('Test with safeties: {:.2f} us'.format(per_round_ms))

    ttl = timeit.timeit(test_statement, setup='from __main__ import TestOptimized as Test;t = Test()')
    per_round_ms = (ttl / timeit.default_number) * 1000000
    print('Test without safeties: {:.2f} us'.format(per_round_ms))

    print('Overhead of clearing/setting')
    ttl = timeit.timeit(
        't.clear();t.name_or_id = 1', setup='from __main__ import Test;t = Test(name_or_id="ben")')
    per_round_ms = (ttl / timeit.default_number) * 1000000
    print('Test with safeties: {:.2f} us'.format(per_round_ms))

    ttl = timeit.timeit(
        't.clear();t.name_or_id = 1', setup='from __main__ import TestOptimized as Test;t = Test(name_or_id="ben")')
    per_round_ms = (ttl / timeit.default_number) * 1000000
    print('Test without safeties: {:.2f} us'.format(per_round_ms))


if __name__ == '__main__':
    main()
