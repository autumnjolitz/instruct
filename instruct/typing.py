import sys
import typing
from typing import Tuple, Dict, Type, Callable, Union, Any, TypeVar

if sys.version_info[:2] >= (3, 8):
    from typing import Protocol, Literal, runtime_checkable, TypedDict
else:
    from typing_extensions import Protocol, runtime_checkable, Literal, TypedDict

if sys.version_info[:2] >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated
if sys.version_info[:2] >= (3, 10):
    from typing import TypeGuard, TypeAlias
    from types import EllipsisType
else:
    from typing_extensions import TypeGuard, TypeAlias

    if typing.TYPE_CHECKING:

        class EllipsisType(Protocol):
            ...

    else:
        EllipsisType = type(Ellipsis)

if sys.version_info[:2] >= (3, 11):
    from typing import Self, Required, NotRequired
else:
    from typing_extensions import Self, Required, NotRequired

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

NoneType = type(None)
CoerceMapping = Dict[str, Tuple[Union[Type, Tuple[Type, ...]], Callable]]


@runtime_checkable
class ICustomTypeCheck(Protocol):
    """
    A runtime pseudo-type object that represents a complex type-hint.

    If ``isinstance(value, self)`` is called, it will execute a function that
    verifies if the value matches the type-hint.
    """

    @staticmethod
    def set_name(name: str) -> str:
        ...


class TypingDefinition(Protocol):
    __module__: Literal["typing", "typing_extensions"]
    __name__: str
    __qualname__: str


class AbstractCollectionType(Protocol):
    __module__: Literal["collections.abc"]


TypeHint: TypeAlias = Union[TypingDefinition, Type[Any]]

if typing.TYPE_CHECKING:
    from .types import AtomicImpl

    Atomic = TypeVar("Atomic", bound=AtomicImpl)
else:
    Atomic = TypeVar("Atomic", bound="AtomicImpl")
