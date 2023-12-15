from __future__ import annotations
import collections.abc
import inspect
from contextlib import suppress
import typing
import warnings
from functools import wraps
from types import FunctionType
from collections.abc import (
    Mapping as AbstractMapping,
    MutableMapping as AbstractMutableMapping,
    Iterable as AbstractIterable,
    MutableSequence as AbstractMutableSequence,
    Collection as AbstractCollection,
)
from typing import (
    Union,
    Any,
    AnyStr,
    List,
    Tuple,
    cast,
    Optional,
    Callable,
    Type,
    TypeVar,
    Mapping,
    Iterable,
    overload,
    Generic,
    Generator,
    Set,
    Dict,
    _GenericAlias,
    cast as cast_type,
)

if typing.TYPE_CHECKING:
    from . import AtomicMeta

from .typing import Protocol, Literal, Annotated, TypeGuard, Self, is_typing_definition

from typing_extensions import get_origin, get_original_bases, is_protocol, get_protocol_members
from typing_extensions import get_args, get_type_hints

from .utils import flatten_restrict as flatten
from .typing import CustomTypeCheck, TypingDefinition, EllipsisType, Atomic, TypeHint
from .constants import Range
from .exceptions import RangeError, TypeError as InstructTypeError

T = TypeVar("T")
U = TypeVar("U")


class CustomTypeCheckMetaBase(type, Generic[T]):
    __slots__ = ()

    if typing.TYPE_CHECKING:

        @staticmethod
        def set_name(name: str) -> str:
            ...


def make_custom_typecheck(*args, is_abstract_type=False):
    if len(args) == 1 and callable(args[0]):
        caller = inspect.stack()[1]
        warnings.warn(
            f"{caller.filename}:{caller.function}:{caller.lineno}: change make_custom_typecheck(...) to have the type we're pretending to be!",
            DeprecationWarning,
        )
        args = (object, *args, ())
    return _make_custom_typecheck(*args, is_abstract_type=is_abstract_type)


@overload
def _make_custom_typecheck(
    typehint: TypingDefinition,
    func: Callable[[Union[Any, T]], bool],
    type_args: Union[Tuple[Any, ...], Tuple[Type, ...]],
    *,
    is_abstract_type: bool = False,
) -> Type[CustomTypeCheck[T]]:
    ...


@overload
def _make_custom_typecheck(
    typehint: Tuple[Type[T], ...],
    func: Callable[[Union[Any, T]], bool],
    type_args: Union[Tuple[Any, ...], Tuple[Type, ...]],
    *,
    is_abstract_type: bool = False,
) -> Type[CustomTypeCheck[T]]:
    ...


@overload
def _make_custom_typecheck(
    typehint: Type[T],
    func: Callable[[Union[Any, T]], bool],
    type_args: Union[Tuple[Any, ...], Tuple[Type, ...]],
    *,
    is_abstract_type: bool = False,
) -> Type[CustomTypeCheck[T]]:
    ...


def _make_custom_typecheck(
    typehint: Union[TypingDefinition, Tuple[Type[T], ...], Type[T]],
    func: Callable[[Union[Any, T]], bool],
    type_args,
    *,
    is_abstract_type=False,
) -> Type[CustomTypeCheck[T]]:
    """
    Create a custom type that will turn `isinstance(item, klass)` into `func(item)`
    """
    assert (
        is_typing_definition(typehint)
        or isinstance(typehint, type)
        or (isinstance(typehint, tuple) and all(isinstance(x, type) for x in typehint))
    )
    if is_typing_definition(typehint):
        typehint_str = str(typehint)
        origin_cls = get_origin(typehint)
        if "typing." in typehint_str:
            typehint_str = typehint_str.replace("typing.", "")
        if "typing_extensions." in typehint_str:
            typehint_str = typehint_str.replace("typing_extensions.", "")
    else:
        if isinstance(typehint, type):
            typehint_str = typehint.__name__
            origin_cls = get_origin(typehint)
        elif isinstance(typehint, tuple):
            origin_cls = Union
            is_abstract_type = True
            typehint_str = str(Union[typehint])
        else:
            raise TypeError(f"Unknown type ({typehint!r}) {type(typehint)}")

    class CustomTypeCheckMeta(CustomTypeCheckMetaBase[T]):
        __slots__ = ()

        def __instancecheck__(self, instance: Union[Any, T]) -> TypeGuard[T]:
            return func(instance)

        def __str__(self):
            return f"{CustomTypeCheckType.__name__}"

        def __repr__(self):
            return f"<MaterializedMetaType {CustomTypeCheckType.__name__}>"

        __origin__ = origin_cls
        __args__ = get_args(typehint)

        if origin_cls in (Union, Literal):

            def __iter__(self):
                return iter(type_args)

            def __contains__(self, key):
                return key in type_args

        @staticmethod
        def set_name(name: str):
            CustomTypeCheckType.__name__ = name
            CustomTypeCheckMeta.__name__ = "CustomTypeCheck[{}]".format(name)
            return name

    bases: Tuple[Type, ...]
    if is_abstract_type:
        bases = (CustomTypeCheck, cast_type(Type, Generic[T]))  # type:ignore[misc]
    else:
        assert isinstance(typehint, type)
        type_cls: Type[T] = cast_type(Type[T], typehint)
        bases = (
            CustomTypeCheck,
            cast_type(Type, Generic[T]),  # type:ignore[misc]
            cast_type(Type, typehint),
        )  # type:ignore[misc]

    if not is_abstract_type:
        if issubclass(type_cls, AbstractMapping):
            key_type, value_type = type_args
            typehint_str = f"{type_cls.__name__}[{key_type}, {value_type}]"

            def validate_mapping(iterable, **kwargs):
                for key, value in iterable:
                    if not isinstance(key, key_type):
                        raise InstructTypeError(f"Key {key!r} is not a {key_type}", key, value)
                    if not isinstance(value, value_type):
                        raise InstructTypeError(
                            f"Value {value!r} is not a {value_type}", key, value
                        )
                    yield key, value

        elif issubclass(type_cls, AbstractIterable):
            if issubclass(type_cls, tuple) and Ellipsis in type_args:
                typehint_str = f"{Tuple[typehint]}"
            else:
                typehint_str = f'{type_cls.__name__}[{", ".join(x.__name__ for x in type_args)}]'

            def validate_iterable(values):
                for index, item in enumerate(values):
                    if not isinstance(item, type_args):
                        raise InstructTypeError(
                            f"{item!r} at index {index} is not a {typehint_str}", index, item
                        )
                    yield item

    class CustomTypeCheckType(*bases, metaclass=CustomTypeCheckMeta[T]):  # type:ignore[misc]
        __slots__ = ()

        def __new__(cls, iterable=None, **kwargs):
            if origin_cls is Union:
                raise TypeError(f"Cannot instantiate a {typehint_str} (UnionType) directly!")
            if is_abstract_type:
                raise TypeError(f"Cannot instantiate abstract class for {typehint}")
            if iterable:
                if issubclass(typehint, AbstractMapping):
                    iterable = {**iterable, **kwargs}
                    iterable = dict(validate_mapping(iterable.items()))
                elif issubclass(typehint, AbstractIterable):
                    iterable = tuple(validate_iterable(iterable))
            return super().__new__(cls, iterable, **kwargs)

        def __str__(self):
            return f"{CustomTypeCheckType.__name__}"

        def __repr__(self):
            return f"{CustomTypeCheckType.__name__}({super().__repr__()})"

        if not is_abstract_type:
            if issubclass(type_cls, AbstractMutableSequence):

                def __setitem__s(self, index_or_slice: Union[slice, int], value):
                    if isinstance(index_or_slice, slice):
                        return super().__setitem__(index_or_slice, validate_iterable(value))
                    if not isinstance(value, type_args):
                        raise InstructTypeError(
                            f"{value!r} is not a {type_args}", index_or_slice, value
                        )
                    super().__setitem__(index_or_slice, value)

                def insert(self, index, value):
                    if not isinstance(value, type_args):
                        raise InstructTypeError(f"{value!r} is not a {type_args}", index, value)
                    super().insert(index, value)

                def append(self, value):
                    if not isinstance(value, type_args):
                        index = len(self)
                        raise InstructTypeError(f"{value!r} is not a {type_args}", index, value)
                    return super().append(value)

                def extend(self, values):
                    return super().extend(validate_iterable(values))

                __setitem__ = __setitem__s

            elif issubclass(type_cls, AbstractMutableMapping):

                def __setitem__m(self, key, value):
                    if not isinstance(key, key_type):
                        raise InstructTypeError(f"Key {key!r} is not a {key_type}", key, value)
                    if not isinstance(value, value_type):
                        raise InstructTypeError(
                            f"Value {value!r} is not a {value_type}", key, value
                        )
                    return super().__setitem__(key, value)

                __setitem__ = __setitem__m

                if hasattr(type_cls, "setdefault"):

                    def setdefault(self, key, value):
                        if not isinstance(key, key_type):
                            raise InstructTypeError(f"Key {key!r} is not a {key_type}", key, value)
                        if not isinstance(value, value_type):
                            raise InstructTypeError(
                                f"Value {value!r} is not a {value_type}", key, value
                            )
                        return super().setdefault(key, value)

                if hasattr(type_cls, "update"):

                    def update(self, iterable):
                        if isinstance(iterable, AbstractMapping):
                            iterable = {**iterable}.items()
                        return super().update(validate_mapping(iterable))

    CustomTypeCheckType.__name__ = typehint_str
    CustomTypeCheckMeta.__name__ = "CustomTypeCheck[{}]".format(typehint_str)
    return CustomTypeCheckType


@overload
def ismetasubclass(cls: Union[Type[Atomic], Type[Any]], metacls: Type[T]) -> TypeGuard[T]:
    ...


@overload
def ismetasubclass(cls: TypeHint, metacls: Type[T]) -> TypeGuard[T]:
    ...


def ismetasubclass(cls: Union[Type[Atomic], Type[Any], TypeHint], metacls: Type[U]) -> TypeGuard[T]:
    if not isinstance(cls, type):
        return False
    assert isinstance(cls, type)
    typecls = type(cls)
    return issubclass(typecls, metacls)


def issubormetasubclass(type_cls: type, cls: type, metaclass: bool = False) -> bool:
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


_NOT_SET = object()


@overload
def find_class_in_definition(
    type_hint: EllipsisType,
    root_cls: Union[Type[Atomic], Type["AtomicMeta"]],
    *,
    metaclass: bool = False,
) -> Generator[Type[Atomic], Optional[Type[Atomic]], None]:
    ...


@overload
def find_class_in_definition(
    type_hint: Union[TypingDefinition, Type[Atomic], Tuple[Type[Atomic], ...]],
    root_cls: Union[Type[Atomic], Type["AtomicMeta"]],
    *,
    metaclass: bool = False,
) -> Generator[Type[Atomic], Optional[Type[Atomic]], Union[Type[Atomic], Tuple[Type[Atomic], ...]]]:
    ...


def find_class_in_definition(type_hint, root_cls: Type, *, metaclass=False):
    if type_hint is Ellipsis:
        return  # type:ignore[return-value]
    assert (
        isinstance(type_hint, tuple)
        or is_typing_definition(type_hint)
        or isinstance(type_hint, type)
    ), f"{type_hint} is a {type(type_hint)}"

    if is_typing_definition(type_hint):
        type_cls: Type = cast(Type, type_hint)
        origin_cls = get_origin(type_cls)
        args = get_args(type_cls)
        if origin_cls is Annotated:
            type_cls, *_ = get_args(type_cls)
            origin_cls = get_origin(type_cls)
            args = get_args(type_cls)

        type_cls_copied: bool = False
        if origin_cls is Union:
            for index, child in enumerate(args):
                if isinstance(child, type) and issubormetasubclass(
                    child, root_cls, metaclass=metaclass
                ):
                    replacement = yield child
                else:
                    assert isinstance(child, type) or is_typing_definition(child)
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
                if isinstance(value_type, type) and issubormetasubclass(
                    value_type, root_cls, metaclass=metaclass
                ):
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
                    if isinstance(child, type) and issubormetasubclass(
                        child, root_cls, metaclass=metaclass
                    ):
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
        if type_cls_copied:
            return type_cls
        return None

    if isinstance(type_hint, type):
        if issubormetasubclass(type_hint, root_cls, metaclass=metaclass):
            replacement = yield type_hint
            if replacement is not None:
                return replacement
        return None

    assert isinstance(type_hint, tuple)

    for index, type_cls in enumerate(type_hint[:]):
        if isinstance(type_cls, type) and issubormetasubclass(
            type_cls, root_cls, metaclass=metaclass
        ):
            replacement = yield type_cls
        else:
            replacement = yield from find_class_in_definition(
                type_cls, root_cls, metaclass=metaclass
            )
        if replacement is not None:
            type_hint = type_hint[:index] + (replacement,) + type_hint[index + 1 :]
    return type_hint


M = Union[TypingDefinition, Type[Iterable], Type[Any], Tuple[Type[Any], ...]]


def create_custom_type(container_type: M, *args: Union[Type[Atomic], Any, Type], check_ranges=()):
    # An abtract type is one that we cannot make real ourselves,
    # like a Union[str, int] cannot be initialized -- it's not real.
    is_abstract_type = False
    if get_origin(container_type) is not None and get_origin(container_type) is not Literal:
        assert get_args(container_type) in (
            args,
            None,
        ), f"{container_type} has {get_args(container_type)} != {args}"

    def _on_new_type(new_type: Type[CustomTypeCheck[T]]):
        if is_typing_definition(container_type):
            new_name = f"{container_type}"
        elif isinstance(container_type, tuple):
            new_name = f"{Union[container_type]}"
        elif isinstance(container_type, type):
            new_name = container_type.__qualname__
        for prefix in ("builtins.", "typing_extensions.", "typing."):
            new_name = remove_prefix(new_name, prefix)
        metaclass = cast(CustomTypeCheckMetaBase, type(new_type))
        metaclass.set_name(new_name)
        return new_type

    make_type = run_after(make_custom_typecheck, _on_new_type)
    test_func: Optional[Callable] = None
    if isinstance(container_type, tuple):
        assert not args
        assert all(isinstance(x, type) for x in container_type)
        return create_custom_type(
            cast_type(TypingDefinition, Union[container_type]),
            *container_type,
            check_ranges=check_ranges,
        )

    if is_typing_definition(container_type):
        origin_cls = get_origin(container_type)
        if origin_cls is Union:
            is_abstract_type = True

            assert args, f"Got empty args for a {container_type}"
            types = flatten((parse_typedef(arg) for arg in args), eager=True)
            is_simple_types = not any(issubclass(x, CustomTypeCheck) for x in types)
            assert types

            if check_ranges:

                def test_func_ranged_union(value: Union[Any, T]) -> TypeGuard[T]:
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

                test_func = test_func_ranged_union

            else:
                # ARJ: if we have Union[int, str, float], we really
                # should return
                #   types := (int, str, float) for the fastest ``isinstance(value, types)``
                if is_simple_types:
                    return types

                def test_func_union(value: Union[Any, T]) -> TypeGuard[T]:
                    """
                    Check if the value is of the type set
                    """
                    return isinstance(value, types)

                test_func = test_func_union

            return make_type(container_type, test_func, types, is_abstract_type=is_abstract_type)

        elif origin_cls is Literal:
            is_abstract_type = True
            from . import AtomicMeta, public_class

            assert args, "Literals require arguments"

            def test_func_literal(value: Union[Any, T]) -> TypeGuard[T]:
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
                            arg_type = public_class(
                                cast(Type["Atomic"], arg_type), preserve_subtraction=True
                            )
                        if isinstance(value, arg_type):
                            return True
                return False

            test_func = test_func_literal

        elif container_type is AnyStr:
            is_abstract_type = True
            assert not args
            if check_ranges:

                def test_ranged_anystr(value: Union[T, Any]) -> TypeGuard[T]:
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

                test_func = test_ranged_anystr

            else:
                return (str, bytes)
        elif container_type is Any:
            # is_abstract_type = True
            assert not args
            return object
        elif isinstance(origin_cls, type):
            if not args:
                return origin_cls
            return create_custom_type(origin_cls, *args, check_ranges=check_ranges)
        else:
            raise NotImplementedError(container_type, str(container_type))
    elif isinstance(container_type, type) and issubclass(container_type, cast(type, Protocol)):
        # Like P[int] where P = class P(Protocol[T])
        if isinstance(container_type, _GenericAlias):
            # ARJ: This is the case where someone is referring
            # to a specialized version of a protocol, like
            # class P(Protocol[T]):
            #    a: T
            # container_type = P[int]
            # parse_typedef(container_type)
            raise NotImplementedError("Specialized protocol-inheriting classes not implemented")
        elif is_simple_protocol(container_type):
            is_abstract_type = True

            attribute_types: Dict[str, CustomTypeCheck] = {}
            attribute_values: Dict[str, Any] = {}
            attribute_functions: Set[str] = set()
            hints = get_type_hints(container_type)

            for attribute in get_protocol_members(container_type):
                with suppress(KeyError):
                    hint = hints[attribute]
                    attribute_types[attribute] = parse_typedef(hint)
                with suppress(AttributeError):
                    attribute_value = getattr(container_type, attribute)
                    if isinstance(attribute_value, FunctionType):
                        attribute_functions.add(attribute)
                        continue
                    attribute_values[attribute] = attribute_value

            def test_simple_protocol(value):
                assert attribute_types or attribute_values or attribute_functions
                if attribute_types:
                    for attribute, type_cls in attribute_types.items():
                        try:
                            attr_value = getattr(value, attribute)
                        except AttributeError:
                            return False
                        else:
                            if not isinstance(attr_value, type_cls):
                                return False
                if attribute_values:
                    for attribute, expected_value in attribute_values.items():
                        try:
                            attr_value = getattr(value, attribute)
                        except AttributeError:
                            return False
                        else:
                            if expected_value != attr_value:
                                return False
                if attribute_functions:
                    value_type = type(value)
                    for attribute in attribute_functions:
                        try:
                            attr_value = getattr(value_type, attribute)
                        except AttributeError:
                            return False
                        else:
                            if not callable(attr_value):
                                return False
                return True

            test_func = test_simple_protocol

        elif is_protocol(container_type):
            # This implements Protocol[T]
            assert container_type.__parameters__
            ...
            raise NotImplementedError(
                f"generic protocol support not implemented ({container_type.__parameters__})"
            )

    # active (collection type, *(generic_types)) ?
    if test_func is None:
        assert isinstance(container_type, type)
        # ARJ: every built-in type implements AbstractCollection...
        if (issubclass(container_type, (AbstractIterable,))) and args:
            is_abstract_type = not (
                issubclass(container_type, AbstractCollection)
                and not container_type.__module__.startswith("collections.abc")
            )
            test_func, args = create_typecheck_for_container(container_type, args)
            if isinstance(args, type):
                args = (args,)

        elif not args:
            # This type has no args (i.e. like it's Dict or set or a custom simple class)
            if check_ranges:

                def test_regular_type(value: Union[Any, T]) -> TypeGuard[T]:
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

                test_func = test_regular_type

            else:
                return container_type
        else:
            is_abstract_type = True
            assert isinstance(container_type, type), f"must be a type - {container_type!r}"
            assert not args
            assert not get_args(container_type)
            if check_ranges:

                def test_ranged_abstract_type(value: Union[Any, T]) -> TypeGuard[T]:
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

                test_func = test_ranged_abstract_type

            else:

                def test_abstract_type(value: Union[T, Any]) -> TypeGuard[T]:
                    return isinstance(value, container_type)

                test_func = test_abstract_type

    new_type = make_type(container_type, test_func, args, is_abstract_type=is_abstract_type)
    return new_type


def run_after(func: Callable, *thunks: Callable):
    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            v = func(*args, **kwargs)
        except Exception:
            raise
        else:
            for thunk in thunks:
                r = thunk(v)
                if r is not None:
                    v = r
        return v

    return wrapped


def remove_prefix(s: str, prefix: str):
    if s.startswith(prefix):
        return s[len(prefix) :]
    return s


V = TypeVar("V")


@overload
def create_typecheck_for_container(
    container_cls: Tuple[Type[V], ...], value_types: Tuple[Type[Any], ...] = ()
) -> Tuple[Callable[[Any], TypeGuard[Tuple[V, ...]]], Tuple[Any, ...]]:
    ...


@overload
def create_typecheck_for_container(
    container_cls: Type[Tuple[V, EllipsisType]], value_types: Tuple[Type, ...] = ()
) -> Tuple[Callable[[Any], TypeGuard[Tuple[V, ...]]], Tuple[Any, ...]]:
    ...


@overload
def create_typecheck_for_container(
    container_cls: Type[Mapping[T, U]], value_types: Tuple[Type, ...] = ()
) -> Tuple[Callable[[Any], TypeGuard[Mapping[T, U]]], Tuple[Any, ...]]:
    ...


@overload
def create_typecheck_for_container(
    container_cls: Type[Iterable[T]], value_types: Tuple[Type, ...] = ()
) -> Tuple[Callable[[Any], TypeGuard[Iterable[T]]], Tuple[Any, ...]]:
    ...


def create_typecheck_for_container(container_cls, value_types=()):
    """
    Determine a function to determine if given value V is an instance of some container type
    and values within are within the
    """
    assert isinstance(container_cls, type), f"{container_cls!r} is not a type"
    assert issubclass(
        container_cls, (AbstractMapping, AbstractIterable, tuple)
    ), f"Not a supported container type - {container_cls!r}"

    test_types = []
    test_func: Optional[Callable[[Any], bool]] = None

    if issubclass(container_cls, tuple):
        container_cls = tuple
        # Special support: Tuple[type, ...]
        if any(item is Ellipsis for item in value_types):
            if len(value_types) != 2:
                raise TypeError("Tuple[type, ...] is allowed but it must be a two pair tuple!")
            homogenous_type_spec, ellipsis = value_types
            if ellipsis is not Ellipsis or homogenous_type_spec is Ellipsis:
                raise TypeError(
                    "Tuple[type, ...] is allowed but it must have ellipsis as second arg"
                )
            homogenous_type = parse_typedef(homogenous_type_spec)

            def test_func(value):
                if not isinstance(value, container_cls):
                    return False
                return all(isinstance(item, homogenous_type) for item in value)

            return test_func, homogenous_type

        else:
            test_types = flatten(
                (parse_typedef(some_type) for some_type in value_types), eager=True
            )

            def test_func(value):
                if not isinstance(value, container_cls):
                    return False
                if len(value) != len(test_types):
                    raise ValueError(f"Expecting a {len(test_types)} value tuple!")
                for index, (item, item_type) in enumerate(zip(value, test_types)):
                    if not isinstance(item, item_type):
                        # raise TypeError(f"{item!r} at index {index} should be a {item_type}")
                        return False
                return True

            assert all(
                isinstance(x, type) for x in test_types
            ), f"some test types are invalid - {test_types}"
            return test_func, tuple(test_types)

    elif issubclass(container_cls, AbstractMapping):
        if value_types:
            key_type_spec, value_type_spec = value_types
            key_type = parse_typedef(key_type_spec)
            value_type = parse_typedef(value_type_spec)

            def test_func(mapping) -> bool:
                if not isinstance(mapping, container_cls):
                    return False
                for key, value in mapping.items():
                    if not all((isinstance(key, key_type), isinstance(value, value_type))):
                        return False
                return True

            return test_func, (key_type, value_type)

    if test_func is None:
        if value_types:
            for some_type in value_types:
                args = get_args(some_type)
                test_types.append(create_custom_type(some_type, *args))
            test_types = flatten(test_types, eager=True)

            def test_func(value):
                if not isinstance(value, container_cls):
                    return False
                return all(isinstance(item, test_types) for item in value)

            assert all(isinstance(x, type) for x in test_types)
            return test_func, test_types

        else:

            def test_func(value):
                return isinstance(value, container_cls)

    return test_func, None


def is_genericizable(item: TypingDefinition):
    """
    Tell us if this definition is an unspecialized generic-capable type like

    >>> T = TypeVar('T')
    >>> U = TypeVar('U')
    >>> is_genericizable(Generic[T])
    False
    >>> is_genericizable(Protocol[T])
    False
    >>> class PairedNamespace(Generic[T, U]):
    ...     first: T
    ...     second: U
    ...
    >>> is_genericizable(PairedNamespace)
    True
    >>> class PairedProtocol(Protocol[T, U]):
    ...     first: T
    ...     second: U
    ...     def bar(self, val: T) -> U:
    ...         ...
    ...
    >>> is_genericizable(PairedProtocol)
    True
    >>>


    This will reject Generic[T], Protocol[T] but allow a class that inherits one
    of those.
    """
    if isinstance(item, type):
        generic_or_protocol = ()
        with suppress(TypeError):
            generic_or_protocol = get_original_bases(item)
        cls: Type
        for cls in generic_or_protocol:
            args = get_args(cls)
            if any(isinstance(arg, TypeVar) for arg in args):
                return True
            origin_cls = get_origin(cls)
            if origin_cls is Generic:
                return True
    return False


def is_simple_protocol(item: TypingDefinition):
    """
    Tell us if this class is like:

    class X(Protocol):
        required_field: int

    excludes:

    class Y(Protocol[T]): ...

    >>> T = TypeVar('T')
    >>> class X(Protocol):
    ...     required_field: int
    ...
    >>> class Y(Protocol[T]):
    ...     required_field: T
    ...
    >>> is_simple_protocol(X)
    True
    >>> is_simple_protocol(Y)
    False

    """
    if isinstance(item, type):
        generic_or_protocol = ()
        with suppress(TypeError):
            generic_or_protocol = get_original_bases(item)
        return Protocol in generic_or_protocol
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
    hint: Union[Tuple[Type, ...], List[Type]], *, check_ranges: Tuple[Range, ...] = ()
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
    # ARJ: short-circuit a list/tuple of types
    if type(hint) in (tuple, list):
        return flatten((parse_typedef(typehint) for typehint in hint), eager=True)
    if isinstance(hint, type) and issubclass(hint, CustomTypeCheck):
        return hint

    if not is_typing_definition(hint):
        # ARJ: Okay, we're not a typing module descendant.
        # Are we a type itelf?
        if isinstance(hint, type):
            cls = hint
            # if is_genericizable(hint):
            #     # special cases!
            #     raise NotImplementedError(
            #         f"Generic-types are not supported, report as an issue."
            #     )
            if check_ranges or issubclass(cls, cast(type, Protocol)):
                return create_custom_type(cls, check_ranges=check_ranges)
            return cls
        raise NotImplementedError(f"Unknown typedef definition {hint!r} ({type(hint)})!")

    typedef: TypingDefinition = hint
    as_origin_cls = get_origin(typedef)
    type_args = get_args(typedef)
    if typedef is AnyStr:
        return create_custom_type(typedef, check_ranges=check_ranges)
    elif typedef is Any:
        return object
    elif typedef is Union:
        raise TypeError("A bare union means nothing!")
    elif as_origin_cls is Annotated:
        actual_typedef: Union[Type, TypingDefinition]
        actual_typedef, *raw_metadata = type_args
        # Skip to the internal type:
        # flags = []
        pending_check_ranges = []
        for annotation in raw_metadata:
            if isinstance(annotation, Range):
                pending_check_ranges.append(annotation)
            # elif (getattr(annotation, '__module__', '') or '').startswith('instruct.constants'):
            #     flags.append(annotation)
        check_ranges = tuple(pending_check_ranges)
        del pending_check_ranges
        new_type = parse_typedef(actual_typedef, check_ranges=check_ranges)
        if check_ranges:
            if is_typing_definition(actual_typedef):
                new_name = str(actual_typedef)
                if new_name.startswith(("typing_extensions.")):
                    new_name = new_name[len("typing_extensions.") :]
                if new_name.startswith(("typing.")):
                    new_name = new_name[len("typing.") :]
            else:
                new_name = actual_typedef.__name__
            type(new_type).set_name(new_name)
        return new_type
    elif as_origin_cls is Union:
        assert type_args, "empty unions unsupported"
        return create_custom_type(typedef, *type_args, check_ranges=check_ranges)
    elif as_origin_cls is Literal:
        if not type_args:
            raise NotImplementedError("Literals must be non-empty!")
        # ARJ: We *really* should make one single type, however,
        # this messes with the message in the test_typedef::test_literal
        # and I'm not comfortable with changing the public messages globally.
        new_type = create_custom_type(typedef, *type_args)
        return new_type
    elif as_origin_cls in (Generic, Protocol):
        raise TypeError("Arbitrary generics are not supported - report an issue with a use case.")
    elif as_origin_cls is not None:
        # This is Tuple[str, str], Tuple, List, List[Any], etc,...
        # Could also be a custom type that implements a generic interface
        if is_typing_definition(as_origin_cls):
            raise NotImplementedError(
                f"The type definition for {typedef} ({as_origin_cls}) is not supported, report as an issue."
            )
        if type_args:
            cls = create_custom_type(as_origin_cls, *type_args, check_ranges=check_ranges)
            new_name = str(typedef)
            if new_name.startswith(("typing_extensions.")):
                new_name = new_name[len("typing_extensions.") :]
            if new_name.startswith(("typing.")):
                new_name = new_name[len("typing.") :]
            metaclass = cast_type(CustomTypeCheckMetaBase, type(cls))
            metaclass.set_name(new_name)
            return cls
        return as_origin_cls
    raise NotImplementedError(
        f"The type definition for {typedef!r} is not supported yet, report as an issue."
    )
