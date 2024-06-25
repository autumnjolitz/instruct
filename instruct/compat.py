import sys
import typing
from contextlib import suppress
from typing import NewType, Any, TypeVar as IntTypeVar, Union

from typing_extensions import get_origin, get_args
from typing_extensions import TypeVar as ExtTypeVar

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

if sys.version_info[:2] >= (3, 13):

    def typevar_has_no_default(t: Union[IntTypeVar, ExtTypeVar]) -> TypeGuard[NoDefaultType]:
        return t.__default__ is NoDefault

else:

    def typevar_has_no_default(t: Union[IntTypeVar, ExtTypeVar]) -> TypeGuard[NoDefaultType]:
        with suppress(AttributeError):
            return t.__default__ is NoDefault  # type:ignore[union-attr]
        return False


__all__ = [
    "Annotated",
    "TypedDict",
    "Unpack",
    "Required",
    "NotRequired",
    "Self",
    "Literal",
    "TypeAlias",
    "ParamSpec",
    "TypeVarTuple",
    "Never",
    "get_origin",
    "get_args",
    "TypeAliasType",
    "typevar_has_no_default",
    "TypeVar",
    "Protocol",
    "TypeGuard",
    "EllipsisType",
]
