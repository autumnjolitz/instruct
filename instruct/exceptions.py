import inflection
import builtins
from typing import Dict, Any, Tuple, Union


class ClassDefinitionError(ValueError):
    ...


class OrphanedListenersError(ClassDefinitionError):
    ...


class MissingGetterSetterTemplateError(ClassDefinitionError):
    ...


class InvalidPostCoerceAttributeNames(ClassDefinitionError):
    ...


class CoerceMappingValueError(ClassDefinitionError):
    ...


class ExceptionJSONSerializable:
    __slots__ = ()
    message: str

    def __str__(self) -> str:
        return self.message

    def __json__(self):
        return {"type": inflection.titleize(type(self).__name__), "message": str(self.message)}

    @classmethod
    def _convert_exception_to_json(cls, item: Exception) -> Dict[str, str]:
        assert isinstance(item, Exception), f"item {item!r} ({type(item)}) is not an exception!"
        if isinstance(item, cls):
            return item.__json__()
        elif hasattr(item, "__json__"):
            return item.__json__()
        elif hasattr(item, "to_json"):
            return item.to_json()
        return {"type": inflection.titleize(type(item).__name__), "message": str(item)}


class TypeError(builtins.TypeError, ExceptionJSONSerializable):
    data: Dict[str, Any]

    def __init__(self, message: str, name: Union[str, int], val: Any, **kwargs):
        self.message = message
        self.name = name
        self.value = val
        self.data = kwargs
        super().__init__(message)

    def __json__(self):
        return {**super().__json__(), "name": self.name, "value": self.value}


class ValueError(builtins.ValueError, ExceptionJSONSerializable):
    data: Dict[str, Any]

    def __init__(self, message: str, *args, **kwargs):
        self.message = message
        self.data = kwargs
        super().__init__(message)


class ClassCreationFailed(builtins.ValueError, builtins.TypeError, ExceptionJSONSerializable):
    errors: Tuple[Exception, ...]
    message: str
    data: Dict[str, Any]

    def __init__(self, message, *errors: Exception, **kwargs):
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
            item = cls._convert_exception_to_json(item)
            item["parent_message"] = self.message
            item["parent_type"] = inflection.titleize(cls.__name__)
            results.append(item)
        return tuple(results)


class RangeError(ValueError, TypeError):
    def __init__(self, value, ranges, message=""):
        ranges = tuple(rng.copy() for rng in ranges)
        self.ranges = ranges
        self.value = value
        if not message:
            message = "Unable to fit {!r} into {}".format(
                value, ", ".join(str(rng) for rng in ranges)
            )
        super().__init__(message, value, ranges)
