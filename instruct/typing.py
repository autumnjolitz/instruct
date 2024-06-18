import sys
import typing
from contextlib import suppress
from collections.abc import Collection as AbstractCollection
from typing import Collection, ClassVar, Tuple, Dict, Type, Callable, Union, Any, Generic, NewType

from typing_extensions import get_origin, get_args

if sys.version_info[:2] >= (3, 8):
    from typing import Protocol, Literal, runtime_checkable, TypedDict
else:
    from typing_extensions import Protocol, runtime_checkable, Literal, TypedDict

if sys.version_info[:2] >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated
if sys.version_info[:2] >= (3, 10):
    from typing import TypeGuard, TypeAlias, ParamSpec
    from types import EllipsisType
else:
    from typing_extensions import TypeGuard, TypeAlias, ParamSpec

    if typing.TYPE_CHECKING:

        class EllipsisType(Protocol):
            ...

    else:
        EllipsisType = type(Ellipsis)

if sys.version_info[:2] >= (3, 11):
    from typing import TypeVarTuple
    from typing import Self, Required, NotRequired
    from typing import Never
else:
    from typing_extensions import TypeVarTuple
    from typing_extensions import Self, Required, NotRequired
    from typing_extensions import Never

if sys.version_info[:2] >= (3, 12):
    from typing import TypeAliasType, Unpack, TypeVar
else:
    from typing_extensions import TypeAliasType, Unpack, TypeVar

NoDefaultType = NewType("NoDefaultType", object)
if sys.version_info[:2] >= (3, 13):
    from typing import NoDefault as _NoDefault

    NoDefault: NoDefaultType = NoDefaultType(_NoDefault)
elif sys.version_info[:2] >= (3, 8):
    from typing_extensions import NoDefault as _NoDefault  # type: ignore[attr-defined]

    NoDefault: NoDefaultType = NoDefaultType(_NoDefault)
else:
    NoDefault: NoDefaultType = NoDefaultType(None)

if typing.TYPE_CHECKING:
    if sys.version_info[:2] >= (3, 8):
        from types import CellType
    else:

        @runtime_checkable
        class CellType(Protocol):
            cell_contents: Any

else:
    if sys.version_info[:2] >= (3, 8):
        from types import CellType
    else:

        def foo():
            a = 1

            def bar():
                return a

            return bar

        CellType = type(foo().__closure__[0])
        del foo

from .types import AtomicImpl, IAtomic

NoneType = type(None)
CoerceMapping = Dict[str, Tuple[Union[Type, Tuple[Type, ...]], Callable]]

Annotated
TypedDict
IAtomic
Unpack
Required
NotRequired
Self

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


class InstanceMethod(Protocol[T]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs):
        ...

    __self__: T
    __name__: str
    __qualname__: str


class ClassMethod(Protocol[T_cta]):
    __self__: ClassVar[Type]
    __name__: str
    __qualname__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs):
        ...

    def __func__(self, cls: Type[T_cta], *args: P.args, **kwargs: P.kwargs):
        ...


class CastType(Protocol[T_co]):
    def __call__(self, value: Any, *args: P.args, **kwargs: P.kwargs) -> T_co:
        ...


# ARJ: Used to signal "I have done nothing to this function"
class ParentCastType(CastType[T_co]):
    __only_parent_cast__: Literal[True]


# ARJ: Used to signal "I have mutated this cast type"
class MutatedCastType(CastType[T_co], Protocol[T_co, U]):
    __union_subtypes__: Tuple[Union[Type[U], Tuple[Type[U], ...]], Callable[[Any], U]]


def is_cast_type(item: Callable[[Any], T]) -> TypeGuard[Type[CastType[T]]]:
    return callable(item)


def is_parent_cast_type(item: CastType[T]) -> TypeGuard[Type[ParentCastType[T]]]:
    return getattr(item, "__only_parent_cast__", False)


def is_mutated_cast_type(item: CastType[T]) -> TypeGuard[Type[MutatedCastType[T, U]]]:
    return getattr(item, "__union_subtypes__", False)


def isclassmethod(function: Callable[[Any], Any]) -> TypeGuard[ClassMethod]:
    return (
        callable(function)
        and hasattr(function, "__func__")
        and hasattr(function, "__self__")
        and isinstance(function.__self__, type)
    )


class TypingDefinition(Protocol):
    __module__: Literal["typing", "typing_extensions"]
    __name__: ClassVar[str]
    __qualname__: ClassVar[str]


def is_typing_definition(item: Any) -> TypeGuard[TypingDefinition]:
    """
    Check if the given item is a type hint.
    """

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
    o: Union[TypingDefinition, Type[Any], Type[T]]
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

Atomic = TypeVar("Atomic", bound=AtomicImpl)

if sys.version_info[:2] >= (3, 13):

    def typevar_has_no_default(t) -> TypeGuard[NoDefaultType]:
        return t.__default__ is NoDefault

else:

    def typevar_has_no_default(t) -> TypeGuard[NoDefaultType]:
        with suppress(AttributeError):
            return t.__default__ is NoDefault
        return False
