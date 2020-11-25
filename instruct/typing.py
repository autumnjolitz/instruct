import typing

try:
    from types import CellType
except ImportError:

    def foo():
        a = 1

        def bar():
            return a

        return bar

    CellType = type(foo().__closure__[0])
    del foo

if typing.TYPE_CHECKING:
    from typing import Protocol
else:
    try:
        from typing import Protocol
    except ImportError:
        from typing_extensions import Protocol


T = typing.TypeVar("T")


class ICustomTypeCheck(Protocol):
    @staticmethod
    def set_name(name: str) -> str:
        ...
