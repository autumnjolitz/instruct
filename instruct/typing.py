import typing

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
