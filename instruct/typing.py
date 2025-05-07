from contextlib import suppress
import sys
from collections.abc import Collection as AbstractCollection
from typing import (
    Collection,
    ClassVar,
    Tuple,
    Dict,
    Type,
    Callable,
    Union,
    Any,
    Generic,
    Optional,
    List,
)

from .compat import (
    TypeVar,
    TypeVarTuple,
    Protocol,
    ParamSpec,
    Literal,
    TypeGuard,
    TypeAliasType,
    EllipsisType,
    TypeAlias,
    Self,
    get_args,
    get_origin as _get_origin,
)
from .types import BaseAtomic

NoneType = type(None)
CoerceMapping = Dict[str, Tuple[Union[Type, Tuple[Type, ...]], Callable]]


T = TypeVar("T")
Ts = TypeVarTuple("Ts")
U = TypeVar("U")
T_co = TypeVar("T_co", covariant=True)
U_co = TypeVar("U_co", covariant=True)
T_cta = TypeVar("T_cta", contravariant=True)


class CustomTypeCheck(Generic[T]):
    """
    A runtime pseudo-type object that represents a complex type-hint.

    If ``isinstance(value, self)`` is called, it will execute a function that
    verifies if the value matches the type-hint.
    """

    __slots__ = ()


P = ParamSpec("P")


class InstanceMethod(Protocol[T, P]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs): ...

    __self__: T
    __name__: str
    __qualname__: str


class ClassMethod(Protocol[T]):
    __self__: Type[Self]
    __name__: str
    __qualname__: str
    __func__: Callable[[Type[T]], T]

    def __call__(self: Self, *args, **kwargs) -> T: ...


class CastType(Protocol[T_co, U_co]):
    def __call__(self: T_co, value: Any, *args, **kwargs) -> U_co: ...


# ARJ: Used to signal "I have done nothing to this function"
class ParentCastType(CastType[T_co, U_co]):
    __only_parent_cast__: Literal[True]


# ARJ: Used to signal "I have mutated this cast type"
class MutatedCastType(CastType[T_co, U_co]):
    __union_subtypes__: Tuple[Union[Type[U_co], Tuple[Type[U_co], ...]], Callable[[Any], U_co]]


def is_cast_type(item: Callable[[Any], T]) -> TypeGuard[Type[CastType[T, T]]]:
    return callable(item)


def is_parent_cast_type(item: CastType[T, T]) -> TypeGuard[Type[ParentCastType[T, T]]]:
    return getattr(item, "__only_parent_cast__", False)


def is_mutated_cast_type(
    item: CastType[T, U],
) -> TypeGuard[Type[MutatedCastType[T, U]]]:
    return getattr(item, "__union_subtypes__", False)


def isclassmethod(function: Callable[[Any], T]) -> TypeGuard[ClassMethod[T]]:
    return (
        callable(function)
        and hasattr(function, "__func__")
        and hasattr(function, "__self__")
        and isinstance(function.__self__, type)
    )


TYPING_MODULE_NAME = "typing"
TYPING_EXTENSIONS_MODULE_NAME = "typing_extensions"


class TypingDefinition(Protocol):
    __module__: Literal[TYPING_MODULE_NAME, TYPING_EXTENSIONS_MODULE_NAME]
    __name__: ClassVar[str]
    __qualname__: ClassVar[str]


def is_typing_definition(item: Any) -> TypeGuard[TypingDefinition]:
    """
    Check if the given item is a type hint.
    """

    with suppress(AttributeError):
        cls_module = type(item).__module__
        if cls_module in (
            TYPING_MODULE_NAME,
            TYPING_EXTENSIONS_MODULE_NAME,
        ) or cls_module.startswith((f"{TYPING_MODULE_NAME}.", f"{TYPING_EXTENSIONS_MODULE_NAME}.")):
            return True
    with suppress(AttributeError):
        module = item.__module__
        if module in (
            TYPING_MODULE_NAME,
            TYPING_EXTENSIONS_MODULE_NAME,
        ) or module.startswith((f"{TYPING_MODULE_NAME}.", f"{TYPING_EXTENSIONS_MODULE_NAME}.")):
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


assert isinstance(T, TypeVar)
assert isinstance(U, TypeVar)

HeterogenousTuple = TypeAliasType("HeterogenousTuple", Tuple[T, U], type_params=(T, U))
VariadicTupleHint = TypeAliasType(
    "VariadicTupleHint", HeterogenousTuple[T, EllipsisType], type_params=(T,)
)
HomogenousTuple = TypeAliasType("HomogenousTuple", Tuple[T, T], type_params=(T,))


def is_anonymous_pair(t: Union[Any, Tuple[T, U]]) -> TypeGuard[Tuple[T, U]]:
    if isinstance(t, tuple) and len(t) == 2:
        a, b = t
        if isinstance(b, EllipsisType):
            assert isinstance(a, type) or is_typing_definition(a)
            return True
        return True
    return False


def isabstractcollectiontype(
    o: Union[TypingDefinition, Type[Any], Type[T]],
) -> TypeGuard[Type[Collection[T]]]:
    cls: Union[Type[Any], Type[T]]
    if is_typing_definition(o):
        origin = get_origin(o)
        if origin is not None:
            return isabstractcollectiontype(origin)
        return False
    if not isinstance(o, type):
        return False
    assert isinstance(o, type)
    cls = o
    if not cls.__module__.startswith("collections.abc"):
        return False
    return issubclass(cls, AbstractCollection)


TypeHint: TypeAlias = Union[TypingDefinition, Type]

Atomic = TypeVar("Atomic", bound=BaseAtomic)

JSONValue: TypeAlias = Optional[Union[str, int, float, bool]]
JSON: TypeAlias = Union[
    Dict[str, Union[JSONValue, "JSON"]],
    Tuple[Union["JSON", JSONValue], ...],
    List[Union["JSON", JSONValue]],
    JSONValue,
]


class HasJSONMagicMethod(Protocol):
    def __json__(self) -> Dict[str, JSON]: ...


class HasToJSON(Protocol):
    def to_json(self) -> Dict[str, JSON]: ...


class ExceptionJSONSerializable(Protocol):
    def __json__(self) -> Dict[str, JSON]: ...


class ExceptionHasDebuggingInfo(Protocol):
    debugging_info: Dict[str, JSON]


class ExceptionHasMetadata(Protocol):
    metadata: Dict[str, JSON]


def exception_is_jsonable(
    e: Exception,
) -> TypeGuard[Union[HasJSONMagicMethod, HasToJSON]]:
    return callable(getattr(e, "__json__", None)) or callable(getattr(e, "to_json", None))


class ICopyWithable(Protocol[T_co]):
    def copy_with(self: T_co, args) -> T_co: ...


def is_copywithable(
    t: Union[Type[Any], TypeHint],
) -> TypeGuard[ICopyWithable[TypeHint]]:
    return callable(getattr(t, "copy_with", None))


if sys.version_info[:2] >= (3, 10):
    from types import UnionType

    UnionTypes = (Union, UnionType)

    # patch get_origin to always return a Union over a 'a | b'
    def get_origin(cls):  # type:ignore[no-redef]
        t = _get_origin(cls)
        if isinstance(t, type) and issubclass(t, UnionType):
            return Union
        return t

    def copy_with(hint: TypeHint, args) -> TypeHint:
        if isinstance(hint, UnionType):
            return Union[args]
        if is_copywithable(hint):
            return hint.copy_with(args)
        type_cls = get_origin(hint)
        with suppress(AttributeError):
            if type_cls is not None:
                return type_cls[args]
        raise NotImplementedError(f"Unable to copy with new type args on {hint!r} ({type(hint)!r})")

else:
    UnionTypes = (Union,)
    get_origin = _get_origin

    def copy_with(hint, args):
        return hint.copy_with(args)
