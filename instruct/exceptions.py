import inflection


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


class ClassCreationFailed(ValueError, TypeError):
    def __init__(self, message, *errors):
        assert len(errors) > 0, "Must have varargs of errors!"
        self.errors = errors
        self.message = message
        super().__init__(message, *errors)

    @classmethod
    def _convert_exception_to_json(cls, item):
        assert isinstance(item, Exception), f"item {item!r} ({type(item)}) is not an exception!"
        if hasattr(item, "to_json"):
            return item.to_json()
        return {"type": inflection.titleize(type(item).__name__), "message": str(item)}

    def to_json(self):
        stack = list(self.errors)
        results = []
        while stack:
            item = stack.pop(0)
            if hasattr(item, "errors"):
                stack.extend(item.to_json())
                continue
            if isinstance(item, Exception):
                item = self.__class__._convert_exception_to_json(item)
            item["parent_message"] = self.message
            item["parent_type"] = inflection.titleize(type(self).__name__)
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
