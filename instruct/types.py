from __future__ import annotations
import sys
from collections import UserDict
from collections.abc import (
    Mapping as AbstractMapping,
    Sequence as AbstractSequence,
    Container as AbstractContainer,
    Set as AbstractSet,
)
from types import MethodType, new_class
from weakref import WeakValueDictionary
from typing import (
    Any,
    Dict,
    Optional,
    Type,
    Generic,
    Callable,
    Mapping,
    FrozenSet,
    Union,
    TypeVar,
    MutableMapping,
    MutableSequence,
    Set,
    Iterable,
    Tuple,
    KeysView,
    Collection,
    cast as cast_type,
    TYPE_CHECKING,
)

if sys.version_info[:2] >= (3, 11):
    from typing import Self
    from typing import TypeVarTuple
else:
    from typing_extensions import Self
    from typing_extensions import TypeVarTuple


if sys.version_info[:2] >= (3, 10):
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard

if sys.version_info[:2] >= (3, 9):
    from typing import get_type_hints
else:
    from typing_extensions import get_type_hints


if TYPE_CHECKING:
    from typing import Iterator
    from .typing import Atomic, TypingDefinition, CustomTypeCheck


if sys.version_info[:2] >= (3, 12):
    from typing import Unpack
else:
    from typing_extensions import Unpack

UnionType = type(Union[str])

T = TypeVar("T")
U = TypeVar("U")


if TYPE_CHECKING:
    from weakref import WeakKeyDictionary as _WeakKeyDictionary

    class WeakKeyDictionary(_WeakKeyDictionary, Generic[T, U]):
        pass

else:
    from weakref import WeakKeyDictionary

_Marks: WeakKeyDictionary[Callable, Dict[str, Any]] = WeakKeyDictionary()


def mark(**kwargs: Any):
    def wrapper(func):
        try:
            _Marks[func] = {**_Marks[func], **kwargs}
        except KeyError:
            _Marks[func] = {**kwargs}
        return func

    return wrapper


def getmarks(func, *names, default=None):
    try:
        marks = _Marks[func]
    except KeyError:
        if names:
            return (default,) * len(names)
        return {}
    else:
        if not names:
            return {**marks}
        results = []
        for name in names:
            try:
                value = marks[name]
            except KeyError:
                results.append(default)
            else:
                results.append(value)
        return tuple(results)


class AbstractAtomic:
    __slots__ = ()

    if TYPE_CHECKING:
        REGISTRY: ImmutableCollection[Set[Type[BaseAtomic]]]
        MIXINS: ImmutableMapping[str, BaseAtomic]
        BINARY_JSON_ENCODERS: Dict[str, Callable[[Union[bytearray, bytes]], Any]]

        _set_defaults: Callable[[], None]
        _slots: Mapping[str, TypingDefinition]
        _columns: ImmutableMapping[str, CustomTypeCheck]
        _no_op_properties: Tuple[str, ...]
        _column_types: ImmutableMapping[str, CustomTypeCheck]
        _all_coercions: ImmutableMapping[str, Tuple[Union[TypingDefinition, Type], Callable]]
        _support_columns: Tuple[str, ...]
        _annotated_metadata: ImmutableMapping[str, Tuple[Any, ...]]
        _nested_atomic_collection_keys: ImmutableMapping[str, Tuple[Type[BaseAtomic], ...]]
        _skipped_fields: FrozenMapping[str, None]
        _modified_fields: FrozenSet[str]
        _properties: KeysView[str]
        _configuration: ImmutableMapping[str, Type[BaseAtomic]]
        __extra_slots__: ImmutableCollection[str]
        _all_accessible_fields: ImmutableCollection[KeysView[str]]
        _listener_funcs: ImmutableMapping[str, Iterable[Callable]]
        _data_class: ImmutableValue[Type[BaseAtomic]]
        _parent: ImmutableValue[Type[BaseAtomic]]

        def __iter__(self) -> Iterator[Tuple[str, Any]]:
            ...


Ts = TypeVarTuple("Ts")

# ARJ: Because we cannot inherit Generic (due to a metaclass layout conflict),
# we must instead create a wrap-around type that can be used with
# the AtomicMeta class
if TYPE_CHECKING:

    class Genericizable(Generic[Unpack[Ts]]):
        ...

else:
    generic_cache = WeakKeyDictionary()

    class Genericizable:
        __slots__ = ()

        def __new__(cls, *args, **kwargs):
            args = ()
            try:
                args = cls.__args__
            except AttributeError:
                args = ()
            if len(cls.__parameters__) != len(args):
                return super(cls, cls).__new__(cls[cls.__default__])
            return super().__new__(cls)

        def __class_getitem__(self, key):
            from . import public_class

            if not isinstance(key, tuple):
                args = (key,)
            else:
                args = key
            if self is Genericizable:
                return new_class(
                    f"Genericable[{args!s}]",
                    (self,),
                    exec_body=lambda ns: ns.update({"__slots__": (), "__parameters__": args}),
                )

            self = public_class(self)
            if self.__parameters__ and len(args) == len(self.__parameters__):
                params = self.__parameters__
                param_mapping = {p: n for p, n in zip(self.__parameters__, args)}
                new_params = tuple(
                    t if not isinstance(param_mapping[t], TypeVar) else param_mapping[t]
                    for t in params
                )
                try:
                    cached_generics = generic_cache[self]
                    return cached_generics[args]
                except KeyError:
                    cached_generics = generic_cache[self] = WeakValueDictionary()

                new_annotations = {}
                complex_fields = []
                typehints = get_type_hints(self, include_extras=True)
                for field_name in self.__parameters_by_field__:
                    typevar_params = self.__parameters_by_field__[field_name]
                    typehint = typehints[field_name]
                    if isinstance(typehint, TypeVar):
                        new_annotations[field_name] = param_mapping[typehint]
                    else:
                        complex_fields.append(field_name)

                for attr_name in self.__parameters_by_field__.keys() & frozenset(complex_fields):
                    typevar_params = self.__parameters_by_field__[attr_name]
                    attr_type_args = []
                    for new_type, typevar in zip(args, typevar_params):
                        attr_type_args.append(new_type)
                    type_genericable = self._columns[attr_name]
                    new_annotations[attr_name] = type_genericable[tuple(attr_type_args)]
                new_cls = cached_generics[args] = type(
                    self.__name__,
                    (self - frozenset(new_annotations.keys()),),
                    {
                        "__annotations__": new_annotations,
                        "__args__": args,
                        "__parameters__": new_params,
                    },
                )

                return new_cls
            raise TypeError(f"{self} is not a generic class")


class BaseAtomic(AbstractAtomic):
    __slots__ = ()

    @mark(base_cls=True)
    def _clear(self: Self, fields: Optional[Iterable[str]] = None):
        pass

    if TYPE_CHECKING:
        __public_class__: Callable[[], Type[Atomic]]

    @mark(base_cls=True)
    def _set_defaults(self: Self) -> Self:
        # ARJ: Override to set defaults instead of inside the `__init__` function
        # Note: Always call ``super()._set_defaults()`` FIRST as if you
        # call it afterwards, the inheritance tree will zero initialize it first
        return self


class AttrsDict(UserDict, Generic[T]):
    def __getattr__(self, key: str) -> Optional[T]:
        try:
            return self.data[key]
        except KeyError:
            self.data[key] = None
            return None


ReadOnlyValue = Union[
    MutableMapping[T, U],
    MutableSequence[T],
    Set[T],
    Mapping[T, U],
    FrozenSet[T],
    Tuple[T, U],
    str,
    int,
    float,
    None,
]

ReadOnlyT = TypeVar("ReadOnlyT", bound="BaseReadOnly")


class BaseReadOnly:
    __slots__ = ("value", "cast_type")

    def __init__(self, value):
        self.value = value

    def __get__(self, obj, objtype=None):
        if self.cast_type is not None:
            return self.cast_type(self.value)
        return self.value


class ImmutableCollection(BaseReadOnly, Generic[T]):
    __slots__ = ()

    value: Collection[T]
    cast_type: Union[Type[Tuple[T, ...]], Type[Set[T]], None]

    def __init__(self, value):
        self.cast_type = None
        if isinstance(value, MutableSequence):
            self.cast_type = cast_type(Type[Tuple[T, ...]], tuple)
        elif isinstance(value, AbstractSet):
            self.cast_type = cast_type(Type[FrozenSet[T]], frozenset)
        super().__init__(value)


class ImmutableMapping(BaseReadOnly, Generic[T, U]):
    __slots__ = ()

    value: Mapping[T, U]
    cast_type: Optional[Type[FrozenMapping[T, U]]]

    def __init__(self, value):
        self.cast_type = None
        if isinstance(value, MutableMapping):
            self.cast_type = FrozenMapping[T, U]
        super().__init__(value)


class ImmutableValue(BaseReadOnly, Generic[T]):
    __slots__ = ()
    value: T
    cast_type: None

    def __init__(self, val):
        self.cast_type = None
        super().__init__(val)


ReadOnly = Union[ImmutableMapping, ImmutableCollection, ImmutableValue]


def is_readonly_mapping(item: BaseReadOnly) -> TypeGuard[ImmutableMapping[T, U]]:
    if isinstance(item.value, AbstractMapping):
        return True
    return False


def is_readonly_sequence(
    item: BaseReadOnly, cls: Type[Collection[T]]
) -> TypeGuard[ImmutableCollection[T]]:
    return isinstance(item.value, cls)


def _caculate_hash(mapping) -> int:
    keys = sorted(mapping)
    return hash(tuple((hash(key), hash(mapping[key])) for key in keys))


FROZEN_MAPPING_SINGLETONS: Mapping[int, Any] = WeakValueDictionary()


class FrozenMapping(Mapping[T, U]):
    __slots__ = "__value", "__hashcode", "__weakref__"

    __value: Dict[T, U]
    __hashcode: int

    def __new__(cls, *args, **kwargs):
        iterable = {}
        if args:
            try:
                (iterable,) = args
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


EMPTY_TERMINUS: FrozenSet[Union[frozenset, FrozenMapping, None, str]] = frozenset(
    {frozenset(), FrozenMapping(), None, ""}
)


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


if sys.version_info[:2] >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol


T_co = TypeVar("T_co", covariant=True)
T_cta = TypeVar("T_cta", contravariant=True)


class InstanceCallable(Protocol[T_cta]):
    def __call__(self, instance: T_cta, *args, **kwargs) -> Any:
        ...


class ClassCallable(Protocol[T_cta]):
    def __call__(self, cls: Type[T_cta], *args, **kwargs) -> Any:
        ...


class ClassOrInstanceFuncsDescriptor(Generic[T]):
    __slots__ = "_class_function", "_instance_function", "_classes"
    _class_function: Union[ClassCallable[T], None]
    _instance_function: Optional[InstanceCallable[T]]

    def __init__(
        self,
        class_function: Union[ClassCallable[T], None] = None,
        instance_function: Optional[InstanceCallable[T]] = None,
    ) -> None:
        self._classes: MutableMapping[Type[T], MethodType] = WeakKeyDictionary()
        self._class_function = class_function
        self._instance_function = instance_function

    def instance_function(
        self, instance_function: InstanceCallable
    ) -> ClassOrInstanceFuncsDescriptor[T]:
        return type(self)(self._class_function, instance_function)

    def class_function(self, class_function: ClassCallable) -> ClassOrInstanceFuncsDescriptor[T]:
        return type(self)(class_function, self._instance_function)

    def __get__(self, instance: Optional[T], owner: Optional[Type[T]] = None) -> MethodType:
        if instance is None:
            assert owner is not None
            assert self._class_function is not None
            try:
                return self._classes[owner]
            except KeyError:
                value = self._classes[owner] = MethodType(self._class_function, owner)
                return value
        assert self._instance_function is not None
        return MethodType(self._instance_function, instance)
