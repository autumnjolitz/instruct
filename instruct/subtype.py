"""
Approaches for automatic subtype specialization through nested type conversion.
"""
import collections.abc
import functools
import inspect
from typing import Type, Any, Callable, TypeVar, Iterable, Mapping, Union
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


def handle_union(*functions):
    """
    Since our approach is to create depth-first cast functions,
    we will need to make traces that will do exactly what we want.

    Union[Type, Type] complicate this. If we assume a trace is unique,
    then we can simply run both traces from the difference point
    and expect that it will only mutate the appropriate members.

    In effect, this function assumes an embedded function set will only
    mutate if it precisely matches.
    """

    def handler(item):
        for function in functions:
            item = function(item)
        return item

    return handler


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
    if cls.__module__ == "collections.abc":
        cls = dict
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
    if cls.__module__ == "collections.abc":
        cls = list
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


def wrapper_for_type(type_hint, class_mapping):
    if is_typing_definition(type_hint):
        if hasattr(type_hint, "_name") and type_hint._name is None:
            if type_hint.__origin__ is Union:
                return handle_union(
                    *[
                        wrapper_for_type(arg, class_mapping=class_mapping)
                        for arg in type_hint.__args__
                    ]
                )
        container_type = getattr(type_hint, "__origin__", None)
        if isinstance(container_type, type) and issubclass(
            container_type, collections.abc.Container
        ):
            if issubclass(container_type, collections.abc.Mapping):
                return handle_mapping(
                    container_type,
                    wrapper_for_type(type_hint.__args__[0], class_mapping=class_mapping),
                    wrapper_for_type(type_hint.__args__[1], class_mapping=class_mapping),
                )
            else:
                return handle_collection(
                    container_type,
                    wrapper_for_type(type_hint.__args__[0], class_mapping=class_mapping),
                )
        else:
            raise NotImplementedError(f"{type_hint} unsupported!")
    elif isinstance(type_hint, type) and issubclass(type(type_hint), Atomic):
        return handle_instruct(type_hint, class_mapping[type_hint])
    return handle_object(type_hint)


def transform_typing_to_coerce(
    type_hints, class_mapping: Mapping[Type, Type]
) -> Callable[[Any], Any]:
    """
    Given an origin mapping type like:

    - Item
    - List[Item]
    - Dict[str, Tuple[Item, ...]]
    - Dict[str, Tuple[Union[Item, str], ...]]

    where class_mapping is like:
        Item: Item - {"fields"}

    and generate a function that returns:
    - handle_instruct(Item, Item - {"fields"})
    - handle_collection(list, handle_instruct(Item, Item - {"fields"}))
    - handle_mapping(dict, str, handle_collection(tuple, handle_instruct(Item, Item - {"fields"})))
    - handle_mapping(dict, str, handle_collection(tuple, handle_object(str, handle_instruct(Item, Item - {"fields"}))))
    """
    if isinstance(type_hints, tuple):
        assert all(is_typing_definition(item) or isinstance(item, type) for item in type_hints)
        type_hints = Union[type_hints]
    assert is_typing_definition(type_hints) or isinstance(type_hints, type)

    return type_hints, wrapper_for_type(type_hints, class_mapping)
