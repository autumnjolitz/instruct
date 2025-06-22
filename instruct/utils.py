import functools
import types
import weakref
from collections.abc import Iterable as AbstractIterable
from enum import EnumMeta
from typing import Any, TypeVar, Dict, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Generic
    from weakref import WeakKeyDictionary as _WeakKeyDictionary

    T = TypeVar("T")
    U = TypeVar("U")

    class WeakKeyDictionary(_WeakKeyDictionary, Generic[T, U]):
        pass

else:
    from weakref import WeakKeyDictionary


def deduplicate(items, *others):
    if not isinstance(items, AbstractIterable):
        raise TypeError(f"{items!r} is not iterable!")
    if others:
        for index, o in enumerate(others):
            if not isinstance(o, AbstractIterable):
                raise TypeError(f"{o!r} at {index} is not iterable!")
        del index, o
    iterables = (items, *others)
    by_hash = set()
    by_eq = []
    by_weakref = set()
    hashable_types = ()
    weakref_types = ()
    eq_only_types = ()
    for iterable in iterables:
        for item in iterable:
            if hashable_types and isinstance(item, hashable_types):
                if item in by_hash:
                    continue
                yield item
                by_hash.add(item)
                continue
            if weakref_types and isinstance(item, weakref_types):
                r = weakref.ref(item)
                weakref_types = (*weakref_types, type(item))
                if r in by_weakref:
                    continue
                yield item
                by_weakref.add(r)
                continue
            if eq_only_types and isinstance(item, eq_only_types):
                if item in by_eq:
                    continue
                by_eq.append(item)
                yield item
                continue

            try:
                r = weakref.ref(item)
            except TypeError:
                pass
            else:
                weakref_types = (*weakref_types, type(item))
                if r in by_weakref:
                    continue
                yield item
                by_weakref.add(r)
                continue
            try:
                hash(item)
            except TypeError:
                pass
            else:
                hashable_types = (*hashable_types, type(item))
                if item in by_hash:
                    continue
                yield item
                by_hash.add(item)
                continue
            eq_only_types = (*eq_only_types, type(item))
            if item in by_eq:
                continue
            by_eq.append(item)
            yield item


def invert_mapping(mapping):
    inverted = {}
    for key, value in mapping.items():
        try:
            inverted[value].append(key)
        except KeyError:
            inverted[value] = [key]
    return {key: tuple(value) for key, value in inverted.items()}


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


if TYPE_CHECKING:
    _Marks: WeakKeyDictionary[Callable, Dict[str, Any]]

_Marks = WeakKeyDictionary()


def mark(**kwargs: Any):
    def wrapper(func):
        try:
            _Marks[func] = {**_Marks[func], **kwargs}
        except KeyError:
            _Marks[func] = {**kwargs}
        return func

    return wrapper


def getmarks(func, *names, default=None):
    try:
        marks = _Marks[func]
    except KeyError:
        if names:
            return (default,) * len(names)
        return {}
    else:
        if not names:
            return {**marks}
        results = []
        for name in names:
            try:
                value = marks[name]
            except KeyError:
                results.append(default)
            else:
                results.append(value)
        return tuple(results)


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
