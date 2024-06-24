from __future__ import annotations
import builtins
import traceback
import typing
import weakref
import abc
from typing import cast
from contextlib import suppress

from .lang import titleize, humanize
from .typing import JSON

if typing.TYPE_CHECKING:
    from typing import Dict, Any, Tuple, Union, Optional, Type, TypeVar, Generic
    from types import TracebackType
    from .compat import Self, TypeGuard, Protocol
    from .typing import ExceptionHasDebuggingInfo, ExceptionHasMetadata

if typing.TYPE_CHECKING:
    T = TypeVar("T")

    class WeakSet(weakref.WeakSet, Generic[T]):
        ...

else:
    from weakref import WeakSet


@titleize.register
def _(e: Exception) -> str:
    """
    >>> titleize(Exception("Foo!"))
    'Exception'
    >>> titleize(OSError("Baz!"))
    'OS Error'
    >>> class ExceptionJSONSerializationError(Exception):
    ...     pass
    ...
    >>> titleize(ExceptionJSONSerializationError())
    'Exception JSON Serialization Error'
    """
    type_name: str = type(e).__name__
    return " ".join(_preserve_type_acronyms_in(titleize(type_name), type_name))


@humanize.register
def _(e: Exception) -> str:
    return titleize(e)


def _preserve_type_acronyms_in(s: str, reference: str):
    index = 0
    for part in s.split():
        u_part = part.upper()
        if reference[index : len(part) + index] == u_part:
            yield u_part
        else:
            yield part
        index += len(part)


class JSONSerializableMeta(type):
    def __init__(self, name, bases, attrs, **kwargs):
        self.registry = weakref.WeakSet()
        super().__init__(name, bases, attrs, **kwargs)

    def __instancecheck__(self, instance):
        if super().__instancecheck__(instance):
            return True
        cls = type(instance)
        if issubclass(cls, tuple(self.registry)):
            return True
        with suppress(AttributeError):
            if callable(cls.__json__):
                self.register(cls)
                return True
        return False

    def register(self, cls):
        if isinstance(cls, self):
            return cls
        if issubclass(cls, tuple(self.registry)):
            return cls
        self.registry.add(cls)
        return cls


class JSONSerializable(metaclass=JSONSerializableMeta):
    __slots__ = ()

    def __init_subclass__(cls, abstract=False, **kwargs):
        if abstract:
            return super().__init_subclass__(**kwargs)
        if not hasattr(cls, "__json__"):

            def __json__(self) -> Dict[str, JSON]:
                return _default_exc_json(self, message=str(self))

            cls.__json__ = __json__
        elif not callable(cls.__json__):
            raise TypeError("__json__ must be a method!")
        return super().__init_subclass__(**kwargs)


class ExceptionJSONSerializable(JSONSerializable, abstract=True):
    __slots__ = ()


class InstructError(Exception, ExceptionJSONSerializable):
    message: str
    metadata: Dict[str, JSON]
    debugging_info: Dict[str, JSON]

    def __str__(self) -> str:
        return self.message

    def __new__(cls: Type[Self], *args, **kwargs) -> Self:
        self = super().__new__(cls, *args, **kwargs)
        self.debugging_info = {}
        self.metadata = {}
        self.message = ""
        return self

    def set_debugging_info(self: Self, val: Dict[str, JSON]) -> Self:
        self.debugging_info = val
        return self

    def set_metadata(self: Self, val: Dict[str, JSON]) -> Self:
        self.metadata = val
        return self


class ClassDefinitionError(InstructError, ValueError):
    ...


class OrphanedListenersError(ClassDefinitionError):
    ...


class MissingGetterSetterTemplateError(ClassDefinitionError):
    ...


class InvalidPostCoerceAttributeNames(ClassDefinitionError):
    ...


class CoerceMappingValueError(ClassDefinitionError):
    ...


def _exception_has_debugging_info(e: Exception) -> TypeGuard[ExceptionHasDebuggingInfo]:
    if isinstance(e, ExceptionJSONSerializable):
        return True
    return hasattr(e, "debugging_info") and isinstance(e.debugging_info, dict)


def _exception_has_metadata(e: Exception) -> TypeGuard[ExceptionHasMetadata]:
    if isinstance(e, ExceptionJSONSerializable):
        return True
    return hasattr(e, "metadata") and isinstance(e.metadata, dict)


def _default_exc_json(e: Exception, message: Optional[str] = None) -> Dict[str, JSON]:
    if message is None:
        message = str(e)
    extra_debugging_info = {}
    if _exception_has_debugging_info(e):
        extra_debugging_info = e.debugging_info
    value = {
        "type": titleize(e),
        "message": message,
        "debugging_info": {
            "stack": traceback.format_exception(type(e), e, e.__traceback__, limit=10),
            **extra_debugging_info,
        },
    }
    if _exception_has_metadata(e):
        value["metadata"] = e.metadata
    return value


def asjson(item: Exception) -> Dict[str, JSON]:
    if not isinstance(item, Exception):
        raise TypeError(f"{item!r} ({type(item).__name__}) is not an Exception!")
    if isinstance(item, JSONSerializable):
        return item.__json__()
    return _default_exc_json(item)


class TypeError(InstructError, builtins.TypeError, ExceptionJSONSerializable):
    data: Dict[str, Any]

    def __init__(self, message: str, name: Union[str, int], val: Any, **kwargs):
        self.message = message
        self.name = name
        self.value = val
        self.data = kwargs
        super().__init__(message)

    def __json__(self):
        defaults = super().__json__()
        return {**defaults, "metadata": {"name": self.name, "value": self.value}}


class ValueError(InstructError, builtins.ValueError, ExceptionJSONSerializable):
    data: Dict[str, Any]

    def __init__(self, message: str, *args, **kwargs):
        self.message = message
        self.data = kwargs
        super().__init__(message)


class ValidationError(
    InstructError, builtins.ValueError, builtins.TypeError, ExceptionJSONSerializable
):
    errors: Tuple[Exception, ...]
    message: str
    data: Dict[str, Any]

    def __init__(self, message: str, *errors: Exception, **kwargs):
        assert len(errors) > 0, "Must have varargs of errors!"
        assert all(isinstance(x, Exception) for x in errors)
        self.errors = errors
        self.message = message
        self.data = kwargs
        super().__init__(message, *errors)

    def __json__(self):
        cls = type(self)
        stack = list(self.errors)
        results = []
        while stack:
            item = stack.pop(0)
            if hasattr(item, "errors"):
                stack.extend(item.__json__())
                continue
            item = asjson(item)
            item["parent_message"] = self.message
            item["parent_type"] = titleize(cls.__name__)
            results.append(item)
        return tuple(results)


def validation_error_if_multiple(message, *errors, **kwargs):
    if len(errors) > 1:
        return ValidationError(message, *errors, **kwargs)
    return errors[0]


class ClassCreationFailed(ValidationError):
    pass


class RangeError(InstructError, builtins.TypeError, builtins.ValueError, ExceptionJSONSerializable):
    def __init__(self, value, ranges, message: str = ""):
        ranges = tuple(rng.copy() for rng in ranges)
        self.ranges = ranges
        self.value = value
        if not message:
            message = "Unable to fit {!r} into {}".format(
                value, ", ".join(str(rng) for rng in ranges)
            )
        super().__init__(message, value, ranges)
