"""
Approaches for automatic subtype specialization through nested type conversion.
"""
import collections.abc
import functools
import inspect
from typing import Type, Any, Callable, TypeVar, Iterable, Mapping
from copy import copy

from . import Atomic
from .typedef import is_typing_definition, parse_typedef

T = TypeVar("T")
U = TypeVar("U")


def curry(function):
    def inner(*args, **kwargs):
        partial = functools.partial(function, *args, **kwargs)
        signature = inspect.signature(partial.func)
        try:
            signature.bind(*partial.args, **partial.keywords)
        except TypeError:
            return curry(copy(partial))
        return partial()

    return inner


def identity(item: T) -> T:
    return item


@curry
def handle_object(cls, cast_function=identity):
    assert issubclass(cls, object)

    def handler(item):
        if isinstance(item, cls):
            return cls(cast_function(item))
        return cast_function(item)

    return handler


@curry
def handle_instruct(from_cls: Type[T], to_cls: Type[U], cast_function=identity):
    assert issubclass(type(from_cls), Atomic)
    assert issubclass(to_cls, from_cls), f"{to_cls} is not a child of {from_cls}"
    assert to_cls is not from_cls

    def handler(item: T) -> U:
        if isinstance(item, from_cls):
            return to_cls(**dict(iter(cast_function(item))))
        return cast_function(item)

    return handler


@curry
def handle_mapping(
    cls, key_cast_function=identity, value_cast_function=identity
) -> Callable[[Mapping[Any, Any]], Mapping[Any, Any]]:
    check_cls = collections.abc.Mapping
    if is_typing_definition(cls):
        assert issubclass(cls.__origin__, check_cls)
        check_cls = parse_typedef(cls)
        cls = cls.__origin__
    else:
        assert issubclass(cls, check_cls)

    def handler(item):
        if isinstance(item, check_cls):
            return cls(
                (key_cast_function(k), value_cast_function(v))
                for k, v in ((key, item[key]) for key in item)
            )
        return value_cast_function(key_cast_function(item))

    return handler


@curry
def handle_collection(cls: Type[T], cast_function=identity) -> Callable[[Iterable[T]], Iterable[T]]:
    check_cls = collections.abc.Collection
    if is_typing_definition(cls):
        assert issubclass(cls.__origin__, check_cls)
        check_cls = parse_typedef(cls)
        cls = cls.__origin__
    else:
        assert issubclass(cls, check_cls)

    def handler(item):
        if isinstance(item, check_cls):
            return cls(cast_function(x) for x in item)
        return cast_function(item)

    return handler


def chain(*functions):
    result = functions[-1]
    for func in functions[:-1][::-1]:
        result = func(result)
    return result


def transform_typing_to_coerce(type_hints, mappings: Mapping[Type, Type]) -> Callable[[Any], Any]:
    """
    Given an origin mapping type like:

    - Item
    - List[Item]
    - Dict[str, Tuple[Item, ...]]
    - Dict[str, Tuple[Union[Item, str], ...]]

    where mappings is like:
        Item: Item - {"fields"}

    and generate a function that returns:
    - handle_instruct(Item, Item - {"fields"})
    - handle_collection(list, handle_instruct(Item, Item - {"fields"}))
    - handle_mapping(dict, str, handle_collection(tuple, handle_instruct(Item, Item - {"fields"})))
    - handle_mapping(dict, str, handle_collection(tuple, handle_object(str, handle_instruct(Item, Item - {"fields"}))))
    """
    assert is_typing_definition(type_hints)
