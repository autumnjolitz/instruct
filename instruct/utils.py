import functools
from collections.abc import Iterable
from enum import EnumMeta

def support_eager_eval(func):

    @functools.wraps(func)
    def wrapper(*args, eager=False, **kwargs):
        if eager:
            return tuple(func(*args, **kwargs))
        return func(*args, **kwargs)
    return wrapper


@support_eager_eval
def flatten(iterable):
    for item in iterable:
        if isinstance(item, Iterable) and \
                not isinstance(item, (str, bytes, bytearray, EnumMeta)):
            yield from item
        else:
            yield item
