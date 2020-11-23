import functools
import types
from collections.abc import Iterable as AbstractIterable, Mapping as AbstractMapping
from enum import EnumMeta
from typing import Union, Iterable, Any, Mapping
from .types import FrozenMapping


def support_eager_eval(func):
    @functools.wraps(func)
    def wrapper(*args, eager=False, **kwargs):
        if eager:
            return tuple(func(*args, **kwargs))
        return func(*args, **kwargs)

    return wrapper


def as_collectable(cls=tuple):
    def decorator(func):
        @functools.wraps(func)
        def collect(*args, **kwargs):
            return cls(func(*args, **kwargs))

        func.collect = collect
        return func

    return decorator


@support_eager_eval
def flatten(iterable):
    for item in iterable:
        if isinstance(item, AbstractIterable) and not isinstance(
            item, (str, bytes, bytearray, EnumMeta)
        ):
            yield from item
        else:
            yield item


@support_eager_eval
def flatten_restrict(iterable):
    for item in iterable:
        if isinstance(item, AbstractIterable) and isinstance(
            item, (tuple, list, types.GeneratorType)
        ):
            yield from item
        else:
            yield item


@as_collectable(FrozenMapping)
def flatten_fields(item: Union[Mapping[str, Any], Iterable[Union[str, Iterable[Any]]]]):
    if isinstance(item, str):
        yield (item, None)
    elif isinstance(item, (AbstractIterable, AbstractMapping)) and not isinstance(
        item, (bytearray, bytes)
    ):

        is_mapping = False
        if isinstance(item, AbstractMapping):
            iterable = ((key, item[key]) for key in item)
            is_mapping = True
        else:
            iterable = iter(item)
        for element in iterable:
            if is_mapping:
                key, value = element
                if isinstance(value, str):
                    yield (key, FrozenMapping({value: None}))
                    continue
                values = flatten_fields.collect(value)
                if len(values) == 0:
                    yield (key, None)
                    continue
                yield (key, values)
                continue
            if isinstance(element, str):
                yield (element, None)
            else:
                values = flatten_fields(element)
                yield from values
    elif item is None:
        return
    else:
        raise NotImplementedError(f"Unsupported type {type(item).__qualname__}")


# def merge_fields(
#     *items: Union[Mapping[str, Any], Iterable[Union[str, Iterable[Any]]]]
# ):
#     items = tuple(flatten_fields(item) for item in items)
#     if len(items) > 2:
#         merged = items[0]
#         for item in items[1:]:
#             merged = merge_fields(merged, item)
#         return merged
#     elif len(items) == 1:
#         return items[0]
#     elif len(items) == 2:
#         left, right = items
#         merged = []
