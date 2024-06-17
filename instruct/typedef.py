from __future__ import annotations
import collections.abc
from functools import wraps
import types
import sys
import typing
from collections.abc import (
    Mapping as AbstractMapping,
    Sequence as AbstractSequence,
    Iterable as AbstractIterable,
)
from typing import Union, Any, AnyStr, List, Tuple, cast, Optional, Callable, Type, TypeVar
from contextlib import suppress
from weakref import WeakKeyDictionary

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from typing_extensions import get_origin as _get_origin
from typing_extensions import get_args

from .utils import flatten_restrict as flatten
from .typing import CustomTypeCheck as ICustomTypeCheck
from .constants import Range
from .exceptions import RangeError

if sys.version_info >= (3, 11):
    from typing import TypeVarTuple, Unpack
else:
    from typing_extensions import TypeVarTuple, Unpack

if sys.version_info >= (3, 10):
    from typing import ParamSpec
    from types import UnionType

    UnionTypes = (Union, UnionType)

    # patch get_origin to always return a Union over a 'a | b'
    def get_origin(cls):
        t = _get_origin(cls)
        if isinstance(t, type) and issubclass(t, UnionType):
            return Union
        return t

else:
    UnionTypes = (Union,)
    get_origin = _get_origin


def is_union_typedef(t) -> bool:
    return _get_origin(t) in UnionTypes


_abstract_custom_types = WeakKeyDictionary()


class AbstractWrappedMeta(type):
    __slots__ = ()

    def set_name(t, name):
        return _abstract_custom_types[t][0](name)

    def set_type(t, type):
        return _abstract_custom_types[t][1](type)


def is_abstract_custom_typecheck(o: Type) -> bool:
    cls_type = type(o)
    return isinstance(cls_type, AbstractWrappedMeta)


def make_custom_typecheck(typecheck_func, typedef=None) -> Type[ICustomTypeCheck]:
    """Create a custom type that will turn `isinstance(item, klass)` into `typecheck_func(item)`"""
    typename = "WrappedType<{}>"
    bound_type = None
    registry = _abstract_custom_types

    class WrappedTypeMeta(AbstractWrappedMeta):
        __slots__ = ()

        def __instancecheck__(self, instance):
            return typecheck_func(instance)

        def __repr__(self):
            return typename.format(super().__repr__())

        def __getitem__(self, key):
            if bound_type is None:
                raise AttributeError(key)
            return parse_typedef(bound_type[key])

    class _WrappedType(metaclass=WrappedTypeMeta):
        __slots__ = ()

        def __class_getitem__(self, key):
            if bound_type is None:
                raise AttributeError(key)
            return parse_typedef(bound_type[key])

        def __new__(cls, *args):
            nonlocal bound_type
            if bound_type is None:
                raise TypeError("Unbound or abstract type!")
            return bound_type(*args)

    def set_name(name):
        nonlocal typename
        typename = name
        _WrappedType.__name__ = name
        _WrappedType._name__ = name
        return name

    def set_type(t):
        nonlocal bound_type
        bound_type = t
        return t

    registry.setdefault(_WrappedType, (set_name, set_type))
    return cast(Type[ICustomTypeCheck], _WrappedType)


def ismetasubclass(cls, metacls):
    return issubclass(type(cls), metacls)


def issubormetasubclass(type_cls, cls, metaclass=False):
    if metaclass is True:
        type_cls = type(type_cls)
    return issubclass(type_cls, cls)


def has_collect_class(
    type_hints: Union[Type, Tuple[Type, ...], List[Type]],
    root_cls: Type,
    *,
    _recursing=False,
    metaclass=False,
):
    if not isinstance(type_hints, (tuple, list)):
        type_hints = (type_hints,)
    for type_cls in type_hints:
        module = getattr(type_cls, "__module__", None)
        if module != "typing":
            continue
        origin_cls = get_origin(type_cls)
        args = get_args(type_cls)
        if origin_cls is Union:
            if _recursing:
                for child in args:
                    if isinstance(child, type) and issubormetasubclass(
                        child, root_cls, metaclass=metaclass
                    ):
                        return True
                    if has_collect_class(child, root_cls, _recursing=True, metaclass=metaclass):
                        return True
            continue
        elif isinstance(origin_cls, type) and (
            issubclass(origin_cls, collections.abc.Iterable)
            and issubclass(origin_cls, collections.abc.Container)
        ):
            if issubclass(origin_cls, collections.abc.Mapping):
                key_type, value_type = args
                if has_collect_class(value_type, root_cls, _recursing=True, metaclass=metaclass):
                    return True
            else:
                for child in args:
                    if isinstance(child, type) and issubormetasubclass(
                        child, root_cls, metaclass=metaclass
                    ):
                        return True
                    elif has_collect_class(child, root_cls, _recursing=True, metaclass=metaclass):
                        return True
    return False


def find_class_in_definition(
    type_hints: Union[Type, Tuple[Type, ...], List[Type]], root_cls: Type, *, metaclass=False
):
    if type_hints is Ellipsis:
        return
    assert (
        isinstance(type_hints, tuple)
        or is_typing_definition(type_hints)
        or isinstance(type_hints, type)
    ), f"{type_hints} is a {type(type_hints)}"

    test_func = lambda child: isinstance(child, type) and issubormetasubclass(
        child, root_cls, metaclass=metaclass
    )
    if issubclass(root_cls, TypeVar):
        test_func = lambda child: isinstance(child, TypeVar)

    if is_typing_definition(type_hints):
        type_cls: Type = cast(Type, type_hints)
        origin_cls = get_origin(type_cls)
        args = get_args(type_cls)
        if origin_cls is Annotated:
            type_cls, *_ = get_args(type_cls)
            origin_cls = get_origin(type_cls)
            args = get_args(type_cls)

        type_cls_copied: bool = False
        if origin_cls is Union:
            for index, child in enumerate(args):
                if test_func(child):
                    replacement = yield child
                else:
                    replacement = yield from find_class_in_definition(
                        child, root_cls, metaclass=metaclass
                    )
                if replacement is not None:
                    args = (*args[:index], replacement, *args[index + 1 :])
                    # args = args[:index] + (replacement,) + args[index + 1 :]
            if args != get_args(type_cls):
                type_cls = type_cls.copy_with(args)
                type_cls_copied = True

        elif isinstance(origin_cls, type) and (
            issubclass(origin_cls, collections.abc.Iterable)
            and issubclass(origin_cls, collections.abc.Container)
        ):
            if issubclass(origin_cls, collections.abc.Mapping):
                key_type, value_type = args
                if test_func(value_type):
                    replacement = yield value_type
                else:
                    replacement = yield from find_class_in_definition(
                        value_type, root_cls, metaclass=metaclass
                    )
                if replacement is not None:
                    args = (key_type, replacement)
                if args != get_args(type_cls):
                    type_cls = type_cls.copy_with(args)
                    type_cls_copied = True
            else:
                for index, child in enumerate(args):
                    if test_func(child):
                        replacement = yield child
                    else:
                        replacement = yield from find_class_in_definition(
                            child, root_cls, metaclass=metaclass
                        )
                    if replacement is not None:
                        args = (*args[:index], replacement, *args[index + 1 :])
                        # args = args[:index] + (replacement,) + args[index + 1 :]
                if args != get_args(type_cls):
                    type_cls = type_cls.copy_with(args)
                    type_cls_copied = True
        elif test_func(type_cls):
            replacement = yield type_cls
            if replacement is not None:
                return type_cls
            return None

        if type_cls_copied:
            return type_cls
        return None

    elif test_func(type_hints):
        replacement = yield type_hints
        if replacement is not None:
            return replacement
        return None

    elif isinstance(type_hints, (tuple, list)):
        for index, type_cls in enumerate(type_hints[:]):
            if test_func(type_cls):
                replacement = yield type_cls
            else:
                replacement = yield from find_class_in_definition(
                    type_cls, root_cls, metaclass=metaclass
                )
            if replacement is not None:
                type_hints = type_hints[:index] + (replacement,) + type_hints[index + 1 :]
        return type_hints


def create_custom_type(container_type, *args, check_ranges=()):
    if is_typing_definition(container_type):
        origin_cls = get_origin(container_type)
        if hasattr(container_type, "_name") and container_type._name is None:
            if origin_cls is Union:
                types = flatten(
                    (create_custom_type(arg) for arg in container_type.__args__), eager=True
                )
                if check_ranges:

                    def test_func(value) -> bool:
                        if not isinstance(value, types):
                            return False
                        failed_ranges = []
                        for rng in check_ranges:
                            if rng.applies(value):
                                try:
                                    in_range = value in rng
                                except TypeError:
                                    continue
                                else:
                                    if in_range:
                                        return True
                                    else:
                                        failed_ranges.append(rng)
                        if failed_ranges:
                            raise RangeError(value, failed_ranges)
                        return False

                else:

                    def test_func(value) -> bool:
                        """
                        Check if the value is of the type set
                        """
                        return isinstance(value, types)

            elif origin_cls is Literal:
                from . import AtomicMeta, public_class

                def test_func(value) -> bool:
                    """
                    Operate on a Literal type
                    """
                    for arg in args:
                        if arg is value:
                            # Exact match on ``is``, useful for enums
                            return True
                        elif arg == value:
                            # Equality by value. This may be part of an
                            # overridden __eq__, so check the types too!
                            if isinstance(arg, type):
                                arg_type = arg
                            else:
                                arg_type = type(arg)
                            if isinstance(arg_type, AtomicMeta):
                                arg_type = public_class(arg_type, preserve_subtraction=True)
                            if isinstance(value, arg_type):
                                return True
                    return False

        elif container_type is AnyStr:
            if check_ranges:

                def test_func(value) -> bool:
                    if not isinstance(value, (str, bytes)):
                        return False
                    failed_ranges = []
                    for rng in check_ranges:
                        if rng.applies(value):
                            try:
                                in_range = value in rng
                            except TypeError:
                                continue
                            else:
                                if in_range:
                                    return True
                                else:
                                    failed_ranges.append(rng)
                    if failed_ranges:
                        raise RangeError(value, failed_ranges)
                    return False

            else:
                return (str, bytes)
        elif container_type is Any:
            return object
        elif origin_cls is not None and (
            issubclass(origin_cls, collections.abc.Iterable)
            and issubclass(origin_cls, collections.abc.Container)
        ):
            return parse_typedef(container_type)
        elif isinstance(container_type, TypeVar):

            def test_func(value) -> bool:
                return False

        else:
            raise NotImplementedError(container_type, repr(container_type))
    elif isinstance(container_type, type) and (
        issubclass(container_type, collections.abc.Iterable)
        and issubclass(container_type, collections.abc.Container)
    ):
        test_func = create_typecheck_container(container_type, args)
    elif isinstance(container_type, type) and not args:
        if check_ranges:

            def test_func(value) -> bool:
                if not isinstance(value, container_type):
                    return False
                failed_ranges = []
                for rng in check_ranges:
                    if rng.applies(value):
                        try:
                            in_range = value in rng
                        except TypeError:
                            continue
                        else:
                            if in_range:
                                return True
                            else:
                                failed_ranges.append(rng)
                if failed_ranges:
                    raise RangeError(value, failed_ranges)
                return False

        else:
            return container_type
    else:
        assert isinstance(container_type, tuple), f"container_type is {container_type}"
        if check_ranges:
            # materialized = issubclass(container_type, collections.abc.Container) and issubclass(container_type, collections.abc.Iterable)

            def test_func(value):
                if not isinstance(value, container_type):
                    return False
                failed_ranges = []
                for rng in check_ranges:
                    if rng.applies(value):
                        try:
                            in_range = value in rng
                        except TypeError:
                            continue
                        else:
                            if in_range:
                                return True
                            else:
                                failed_ranges.append(rng)
                if failed_ranges:
                    raise RangeError(value, failed_ranges)
                return False

        else:

            def test_func(value):
                return isinstance(value, container_type)

    t = make_custom_typecheck(test_func)
    AbstractWrappedMeta.set_type(t, container_type)
    return t


def is_variable_tuple(decl) -> bool:
    origin_cls = get_origin(decl)
    with suppress(ValueError):
        t, ellipsis = get_args(decl)
        return origin_cls is tuple and ellipsis is Ellipsis
    return False


def create_typecheck_container(container_type, items):
    test_types = []
    test_func: Optional[Callable[[Any], bool]] = None

    if issubclass(container_type, tuple):
        container_type = tuple
        # Special support: Tuple[type, ...]
        if any(item is Ellipsis for item in items):
            if len(items) != 2:
                raise TypeError("Tuple[type, ...] is allowed but it must be a two pair tuple!")
            homogenous_type_spec, ellipsis = items
            if ellipsis is not Ellipsis or homogenous_type_spec is Ellipsis:
                raise TypeError(
                    "Tuple[type, ...] is allowed but it must have ellipsis as second arg"
                )
            homogenous_type = parse_typedef(homogenous_type_spec)

            def test_func(value):
                if not isinstance(value, container_type):
                    return False
                return all(isinstance(item, homogenous_type) for item in value)

            return test_func

        else:
            for some_type in items:
                test_types.append(create_custom_type(some_type))

            def test_func(value):
                if not isinstance(value, container_type):
                    return False
                if len(value) != len(test_types):
                    raise ValueError(f"Expecting a {len(test_types)} value tuple!")
                for index, (item, item_type) in enumerate(zip(value, test_types)):
                    if not isinstance(item, item_type):
                        # raise TypeError(f"{item!r} at index {index} should be a {item_type}")
                        return False
                return True

    elif issubclass(container_type, AbstractMapping):
        if items:
            key_type_spec, value_type_spec = items
            key_type = parse_typedef(key_type_spec)
            value_type = parse_typedef(value_type_spec)

            def test_func(mapping) -> bool:
                if not isinstance(mapping, container_type):
                    return False
                for key, value in mapping.items():
                    if not all((isinstance(key, key_type), isinstance(value, value_type))):
                        return False
                return True

    if test_func is None:
        if items:
            for some_type in items:
                test_types.append(create_custom_type(some_type))
            types = tuple(test_types)

            def test_func(value):
                if not isinstance(value, container_type):
                    return False
                return all(isinstance(item, types) for item in value)

        else:

            def test_func(value):
                return isinstance(value, container_type)

    return test_func


def is_typing_definition(item):
    with suppress(AttributeError):
        cls_module = type(item).__module__
        if cls_module in ("typing", "typing_extensions") or cls_module.startswith(
            ("typing.", "typing_extensions.")
        ):
            return True
    with suppress(AttributeError):
        module = item.__module__
        if module in ("typing", "typing_extensions") or module.startswith(
            ("typing.", "typing_extensions.")
        ):
            return True
    if isinstance(item, (TypeVar, TypeVarTuple, ParamSpec)):
        return True
    origin = get_origin(item)
    args = get_args(item)
    if origin is not None:
        return True
    elif args:
        return True
    return False


def assert_never_null(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        val = func(*args, **kwargs)
        assert val is not None, f"{func.__name__} returned None!"
        return val

    return wrapped


@assert_never_null
def parse_typedef(
    typedef: Union[Tuple[Type, ...], List[Type]], *, check_ranges: Tuple[Range, ...] = ()
) -> Union[Type, Tuple[Type]]:
    """
    Break a type def into types suitable for doing an isinstance(item, ...) check.

    typeA -> typeA
    (typeA, typeB) -> (typeA, typeB)
    Union[typeA, typeB] -> (typeA, typeB)
    Optional[typeA] -> (NoneType, typeA)

    Support collection typelimiting like

    List[int] -> (IntList,) where IntList is a custom type with a special
    metaclass that executes an embedded function for checking if all members
    of the collection is the right type. i.e all(isintance(item, int) for item in object)
    """

    if not is_typing_definition(typedef):
        # ARJ: Okay, we're not a typing module descendant.
        # Are we a type itelf?
        if isinstance(typedef, type):
            if check_ranges:
                return create_custom_type(typedef, check_ranges=check_ranges)
            return typedef
        elif isinstance(typedef, tuple):
            with suppress(ValueError):
                (single_type,) = typedef
                return parse_typedef(single_type)
            return tuple(parse_typedef(decl) for decl in typedef)
        else:
            raise NotImplementedError(f"Unknown typedef definition {typedef!r} ({type(typedef)})!")

    as_origin_cls = get_origin(typedef)
    args = get_args(typedef)

    if typedef is AnyStr:
        return create_custom_type(typedef, check_ranges=check_ranges)
    elif typedef is Any:
        return object
    elif typedef is Union:
        raise TypeError("A bare union means nothing!")
    elif as_origin_cls is Annotated:
        typedef, *raw_metadata = args
        # Skip to the internal type:
        # flags = []
        p_check_ranges = []
        for annotation in raw_metadata:
            if isinstance(annotation, Range):
                p_check_ranges.append(annotation)
            # elif (getattr(annotation, '__module__', '') or '').startswith('instruct.constants'):
            #     flags.append(annotation)
        check_ranges = tuple(p_check_ranges)
        del p_check_ranges
        new_type = parse_typedef(typedef, check_ranges=check_ranges)
        if check_ranges:
            if is_typing_definition(typedef):
                new_name = str(typedef)
                if new_name.startswith(("typing_extensions.")):
                    new_name = new_name[len("typing_extensions.") :]
                if new_name.startswith(("typing.")):
                    new_name = new_name[len("typing.") :]
            else:
                new_name = typedef.__name__
            AbstractWrappedMeta.set_name(new_type, new_name)
            AbstractWrappedMeta.set_type(new_type, typedef)
        return new_type
    elif as_origin_cls is Union:
        args = get_args(typedef)
        assert args
        if check_ranges:
            return create_custom_type(typedef, check_ranges=check_ranges)
        return flatten((parse_typedef(argument) for argument in args), eager=True)
    elif as_origin_cls is Literal:
        args = get_args(typedef)
        if not args:
            raise NotImplementedError("Literals must be non-empty!")
        items = []
        # ARJ: We *really* should make one single type, however,
        # this messes with the message in the test_typedef::test_literal
        # and I'm not comfortable with changing the public messages globally.
        for arg in args:
            new_type = create_custom_type(typedef, arg)
            if isinstance(arg, str):
                arg = f'"{arg}"'
            AbstractWrappedMeta.set_name(new_type, f"{arg!s}")
            items.append(new_type)
        return tuple(items)
    elif as_origin_cls is not None or isinstance(typedef, TypeVar):
        if is_typing_definition(typedef) and hasattr(typedef, "_name") and typedef._name is None:
            # special cases!
            raise NotImplementedError(
                f"The type definition for {typedef} is not supported, report as an issue."
            )
        args = get_args(typedef)
        if args or as_origin_cls is None:
            if as_origin_cls is not None:
                cls = create_custom_type(as_origin_cls, *args, check_ranges=check_ranges)
            else:
                cls = create_custom_type(typedef, check_ranges=check_ranges)
            new_name = str(typedef)
            if new_name.startswith(("typing_extensions.")):
                new_name = new_name[len("typing_extensions.") :]
            if new_name.startswith(("typing.")):
                new_name = new_name[len("typing.") :]
            AbstractWrappedMeta.set_name(cls, new_name)
            AbstractWrappedMeta.set_type(cls, typedef)
            return cls
        return as_origin_cls

    raise NotImplementedError(
        f"The type definition for {typedef!r} ({type(typedef)}) is not supported yet, report as an issue."
    )
