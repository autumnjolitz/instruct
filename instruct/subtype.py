"""
Approaches for automatic subtype specialization through nested type conversion.
"""

import collections.abc
import functools
import inspect
import itertools
from copy import copy
from typing import Type, Any, Callable, TypeVar, Iterable, Mapping, Union, cast, overload
from typing_extensions import get_args

from .typedef import is_typing_definition, parse_typedef, ismetasubclass

from .typing import (
    EllipsisType,
    TypeHint,
    Atomic,
    isabstractcollectiontype,
    get_origin,
)

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


def handle_union(*type_function_pairs):
    """
    Since our approach is to create depth-first cast functions,
    we will need to make traces that will do exactly what we want.

    Union[Type, Type] complicate this. If we assume a trace is unique,
    then we can simply run both traces from the difference point
    and expect that it will only mutate the appropriate members.

    In effect, this function assumes an embedded function set will only
    mutate if it precisely matches.
    """
    pairings = []
    pairs_to_zip = []
    for item in type_function_pairs:
        if isinstance(item, tuple):
            pairings.append(item)
        else:
            pairs_to_zip.append(item)
    if pairs_to_zip:
        if len(pairs_to_zip) % 2 != 0:
            raise TypeError("Must provide an even number of type/callable pairings")
        pairings.extend((left, right) for left, right in zip(pairs_to_zip[::2], pairs_to_zip[1::2]))
    for index, (type_cls, func) in enumerate(pairings):
        if is_typing_definition(type_cls):
            pairings[index] = (parse_typedef(type_cls), func)
    type_callable_pairs = tuple(pairings)
    del pairings, pairs_to_zip

    if not all((isinstance(left, type)) and callable(right) for left, right in type_callable_pairs):
        raise TypeError("Must be a type/callable pairings!")

    def handler(item):
        for type_cls, function in type_callable_pairs:
            if isinstance(item, type_cls):
                return function(item)
        return item

    return handler


@curry
def handle_object(cls, cast_function=identity):
    assert issubclass(cls, object)

    def handler(item):
        if isinstance(item, cls):
            return cls(cast_function(item))
        return item

    return handler


@curry
def handle_instruct(metaclass, from_cls, to_cls, cast_function=identity):
    from . import public_class

    assert ismetasubclass(from_cls, metaclass)
    if not issubclass(to_cls, from_cls):
        if public_class(to_cls) is not public_class(from_cls):
            raise TypeError(f"{to_cls} is not a child of {from_cls}")
    assert to_cls is not from_cls

    def handler(item):
        if isinstance(item, from_cls):
            return to_cls(**dict(iter(cast_function(item))))
        return item

    return handler


@curry
def handle_mapping(
    cls, key_cast_function=identity, value_cast_function=identity
) -> Callable[[Mapping[Any, Any]], Mapping[Any, Any]]:
    if cls.__module__ == "collections.abc":
        cls = dict
    check_cls = collections.abc.Mapping
    if is_typing_definition(cls):
        origin_cls = get_origin(cls)
        assert origin_cls is not None
        assert issubclass(origin_cls, check_cls)
        check_cls = parse_typedef(cls)
        cls = origin_cls
    else:
        assert issubclass(cls, check_cls)

    def handler(item):
        if isinstance(item, check_cls):
            return cls(
                (key_cast_function(k), value_cast_function(v))
                for k, v in ((key, item[key]) for key in item)
            )
        return item

    return handler


def handle_collection(cls: Type[T], *cast_functions) -> Callable[[Iterable[T]], Iterable[T]]:
    if isabstractcollectiontype(cls):
        # ARJ: We can't materialize an MutableMapping, Sequence, et al because it is
        # an abstract class.
        if issubclass(cls, collections.abc.Mapping):
            return handle_mapping(cls, *cast_functions)
        # So now it's just things like List[T], Set[T], ...
        cls = cast(Type[T], list)

    check_cls = collections.abc.Collection
    if is_typing_definition(cls):
        origin_cls = get_origin(cls)
        assert origin_cls is not None
        assert issubclass(origin_cls, check_cls)
        check_cls = parse_typedef(cls)
        cls = origin_cls
    else:
        assert issubclass(cls, check_cls)
    if not cast_functions:
        cast_functions = (identity,)
    if len(cast_functions) == 2 and cast_functions[-1] == Ellipsis:
        cast_functions = (cast_functions[0],)
    if not all(callable(function) for function in cast_functions):
        raise TypeError("handle_collection expects cast_functions to be all callables")

    def handler(item):
        if isinstance(item, check_cls):
            num_items = len(item)
            # ARJ: Note, that zip_longest will apply fillvalue to BOTH sides of the
            # iterable. So if you've an empty `item`, you can get the last cast_function.
            # nasty, isn't it? This guard limits that from occurring.
            return cls(
                cast_function(value)
                for index, (value, cast_function) in enumerate(
                    itertools.zip_longest(item, cast_functions, fillvalue=cast_functions[-1])
                )
                if index < num_items
            )
        return item

    return handler


@overload
def wrapper_for_type(
    type_hint: EllipsisType, class_mapping: Mapping[Type[Atomic], Type[Atomic]], metaclass
) -> EllipsisType: ...


@overload
def wrapper_for_type(
    type_hint: TypeHint, class_mapping: Mapping[Type[Atomic], Type[Atomic]], metaclass
) -> Callable[[Any], Any]: ...


def wrapper_for_type(
    type_hint: Union[TypeHint, EllipsisType],
    class_mapping: Mapping[Type[Atomic], Type[Atomic]],
    metaclass,
) -> Union[Callable[[Any], Any], EllipsisType]:
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

    if type_hint is Ellipsis:
        return type_hint
    if is_typing_definition(type_hint):
        container_type = get_origin(type_hint)
        if container_type is Union:
            return handle_union(
                *[
                    (parse_typedef(arg), wrapper_for_type(arg, class_mapping, metaclass))
                    for arg in get_args(type_hint)
                ]
            )
        elif isinstance(container_type, type) and issubclass(
            container_type, collections.abc.Container
        ):
            if issubclass(container_type, collections.abc.Mapping):
                assert len(get_args(type_hint)) == 2
                return handle_mapping(
                    container_type,
                    wrapper_for_type(get_args(type_hint)[0], class_mapping, metaclass),
                    wrapper_for_type(get_args(type_hint)[1], class_mapping, metaclass),
                )
            else:
                return handle_collection(
                    container_type,
                    *(
                        wrapper_for_type(arg, class_mapping, metaclass)
                        for arg in get_args(type_hint)
                    ),
                )
        else:
            raise NotImplementedError(f"{type_hint} unsupported!")
    elif isinstance(type_hint, type) and ismetasubclass(type_hint, metaclass):
        from_cls: Type[Atomic]

        try:
            from_cls, to_cls = (
                cast(Type[Atomic], type_hint),
                class_mapping[cast(Type[Atomic], type_hint)],
            )
        except KeyError as e:
            raise ValueError(
                f"Unable to find the counterpart for {type_hint}! Currently have {class_mapping}"
            ) from e
        return handle_instruct(metaclass, from_cls, to_cls)
    return handle_object(type_hint)
