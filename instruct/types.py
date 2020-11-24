from collections import UserDict
from collections.abc import (
    Mapping as AbstractMapping,
    Sequence as AbstractSequence,
    Container as AbstractContainer,
)
from types import MethodType
from weakref import WeakKeyDictionary, WeakValueDictionary
from typing import Any, Dict


class AttrsDict(UserDict):
    def __getattr__(self, key):
        try:
            return self.data[key]
        except KeyError:
            self.data[key] = None
            return None


class ReadOnly:
    __slots__ = ("value",)

    def __init__(self, value):
        self.value = value

    def __get__(self, obj, objtype=None):
        return self.value


def _caculate_hash(mapping):
    keys = sorted(mapping)
    return hash(tuple((hash(key), hash(mapping[key])) for key in keys))


FROZEN_MAPPING_SINGLETONS = WeakValueDictionary()


class FrozenMapping(AbstractMapping):
    __slots__ = "__value", "__hashcode", "__weakref__"

    __value: Dict[Any, Any]
    __hashcode: int

    def __new__(cls, *args, **kwargs):
        iterable = {}
        if args:
            try:
                iterable, = args
            except ValueError:
                raise TypeError(f"{cls.__name__} expected at most 1 arguments, got {len(args)}")
            if isinstance(iterable, cls) and not kwargs:
                return iterable
        if iterable is None:
            iterable = {}
        if isinstance(iterable, (set, frozenset, tuple, list)):
            iterable = {key: None for key in iterable}
        elif isinstance(iterable, str):
            iterable = {iterable: None}
        iterable = dict(iterable)
        iterable.update(kwargs)
        for key, value in iterable.items():
            if isinstance(value, cls):
                continue
            elif isinstance(value, AbstractMapping):
                iterable[key] = cls(value)
        hashcode = _caculate_hash(iterable)
        try:
            return FROZEN_MAPPING_SINGLETONS[hashcode]
        except KeyError:
            new_frozen_hash = super().__new__(cls)
            new_frozen_hash.__value = iterable
            new_frozen_hash.__hashcode = hashcode
            FROZEN_MAPPING_SINGLETONS[hashcode] = new_frozen_hash
        return new_frozen_hash

    def __sub__(self, other):
        # format: self - other
        if isinstance(other, str):
            other = frozenset((other,))
        if isinstance(other, AbstractContainer):
            if not isinstance(other, FrozenMapping):
                other = FrozenMapping(other)
            return deep_subtract_mappings(self, other, cls=type(self))
        return NotImplemented

    def __rsub__(self, other):
        # format: other - self
        if isinstance(other, str):
            other = frozenset((other,))
        if isinstance(other, AbstractContainer):
            if not isinstance(other, FrozenMapping):
                other = FrozenMapping(other)
            return deep_subtract_mappings(other, self, cls=type(self))
        return NotImplemented

    def __or__(self, other):
        # format: self | other
        if not isinstance(other, AbstractMapping):
            return NotImplemented
        if not isinstance(other, FrozenMapping):
            other = FrozenMapping(other)
        return deep_merge_mappings(self, other, cls=type(self))

    def __ror__(self, other):
        # format: other | self
        if not isinstance(other, AbstractMapping):
            return NotImplemented
        if not isinstance(other, FrozenMapping):
            other = FrozenMapping(other)
        return deep_merge_mappings(other, self, cls=type(self))

    def __reduce__(self):
        return type(self), (self.__value,)

    def keys(self):
        return self.__value.keys()

    def __repr__(self):
        return f"FrozenMapping<{self.__value!r}>"

    def __str__(self):
        return str(self.__value)

    def __hash__(self):
        return self.__hashcode

    def __getitem__(self, key):
        return self.__value[key]

    def __len__(self):
        return len(self.__value)

    def __contains__(self, key):
        return key in self.__value

    def items(self):
        return self.__value.items()

    def __iter__(self):
        return iter(self.keys())


EMPTY_TERMINUS = frozenset({frozenset(), FrozenMapping(), None, ""})


def deep_merge_mappings(left: FrozenMapping, right: FrozenMapping, *, cls=dict) -> FrozenMapping:
    unique_left = left.keys() - right.keys()
    shared_keys = left.keys() & right.keys()
    unique_right = right.keys() - left.keys()
    merged = {}
    for key in unique_left:
        merged[key] = left[key]
    for key in unique_right:
        merged[key] = right[key]
    for key in shared_keys:
        left_value = left[key]
        right_value = right[key]
        if left_value in EMPTY_TERMINUS:
            merged[key] = None
            continue
        elif right_value in EMPTY_TERMINUS:
            merged[key] = None
            continue
        if isinstance(left_value, (AbstractMapping, AbstractSequence)):
            if not isinstance(left_value, cls):
                left_value = cls(left_value)
        if isinstance(right_value, (AbstractMapping, AbstractSequence)):
            if not isinstance(right_value, cls):
                right_value = cls(right_value)
        if isinstance(left_value, cls) and isinstance(right_value, cls):
            merged[key] = deep_merge_mappings(left_value, right_value, cls=cls)
        else:
            merged[key] = right_value
    return cls(merged)


def deep_subtract_mappings(left: FrozenMapping, right: FrozenMapping, *, cls=dict) -> FrozenMapping:
    diverged = {}
    unique_left = left.keys() - right.keys()
    shared_keys = left.keys() & right.keys()
    for key in unique_left:
        diverged[key] = left[key]
    for key in shared_keys:
        left_value = left[key]
        right_value = right[key]
        if left_value in EMPTY_TERMINUS:
            continue
        elif right_value in EMPTY_TERMINUS:
            continue
        if isinstance(left_value, (AbstractMapping, AbstractSequence)):
            if not isinstance(left_value, cls):
                left_value = cls(left_value)
        if isinstance(right_value, (AbstractMapping, AbstractSequence)):
            if not isinstance(right_value, cls):
                right_value = cls(right_value)
        if isinstance(left_value, cls) and isinstance(right_value, cls):
            values = deep_subtract_mappings(left_value, right_value, cls=cls)
            if values:
                if values == left_value:
                    diverged[key] = left[key]
                else:
                    diverged[key] = values
    return cls(diverged)


class ClassOrInstanceFuncsDescriptor:
    __slots__ = "_class_function", "_instance_function", "_classes"

    def __init__(self, class_function=None, instance_function=None):
        self._classes = WeakKeyDictionary()
        self._class_function = class_function
        self._instance_function = instance_function

    def instance_function(self, instance_function):
        return type(self)(self._class_function, instance_function)

    def class_function(self, class_function):
        return type(self)(class_function, self._instance_function)

    def __get__(self, instance, owner=None):
        if instance is None:
            try:
                return self._classes[owner]
            except KeyError:
                value = self._classes[owner] = MethodType(self._class_function, owner)
                return value
        return MethodType(self._instance_function, instance)
