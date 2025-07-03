from __future__ import annotations
import sys
import inspect
from collections import UserDict
from collections.abc import (
    Mapping as AbstractMapping,
    Sequence as AbstractSequence,
    Container as AbstractContainer,
    Set as AbstractSet,
    Iterable as AbstractIterable,
)
from types import MethodType, new_class
from weakref import WeakValueDictionary, WeakKeyDictionary
from typing import (
    Any,
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
    overload,
)

from .utils import mark, as_collectable

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
    from typing import Iterator, Literal
    from .typing import Atomic, TypingDefinition, CustomTypeCheck


if sys.version_info[:2] >= (3, 12):
    from typing import Unpack
else:
    from typing_extensions import Unpack

UnionType = type(Union[str])

T = TypeVar("T")
U = TypeVar("U")


class AbstractAtomic:
    __slots__ = ()

    if TYPE_CHECKING:
        REGISTRY: ImmutableCollection[set[type[BaseAtomic]]]
        MIXINS: ImmutableMapping[str, BaseAtomic]
        BINARY_JSON_ENCODERS: dict[str, Callable[[bytearray | bytes], Any]]

        _set_defaults: Callable[[], None]
        _slots: Mapping[str, TypingDefinition]
        _columns: ImmutableMapping[str, CustomTypeCheck]
        _no_op_properties: tuple[str, ...]
        _column_types: ImmutableMapping[str, CustomTypeCheck]
        _all_coercions: ImmutableMapping[str, tuple[TypingDefinition | type, Callable]]
        _support_columns: tuple[str, ...]
        _annotated_metadata: ImmutableMapping[str, tuple[Any, ...]]
        _nested_atomic_collection_keys: ImmutableMapping[str, tuple[type[BaseAtomic], ...]]
        _skipped_fields: FrozenMapping[str, None]
        _modified_fields: frozenset[str]
        _properties: KeysView[str]
        _configuration: ImmutableMapping[str, type[BaseAtomic]]
        __extra_slots__: ImmutableCollection[str]
        _all_accessible_fields: ImmutableCollection[KeysView[str]]
        _listener_funcs: ImmutableMapping[str, Iterable[Callable]]
        _data_class: ImmutableValue[type[BaseAtomic]]
        _parent: ImmutableValue[type[BaseAtomic]]

        def __iter__(self) -> Iterator[tuple[str, Any]]: ...

        @overload
        def __getitem__(self: Self, key: str) -> Any: ...

        @overload
        def __getitem__(self: Self, key: int) -> Any: ...

        @overload
        def __getitem__(self: Self, key: slice) -> tuple[Any, ...]: ...

        def __getitem__(self, key): ...

        @overload
        def __setitem__(self: Self, key: str, val: Any) -> None: ...

        @overload
        def __setitem__(self: Self, key: int, val: Any) -> None: ...

        @overload
        def __setitem__(self: Self, key: slice, val: Iterable[Any]) -> None: ...

        def __setitem__(self, key, val): ...


Ts = TypeVarTuple("Ts")

# ARJ: Because we cannot inherit Generic (due to a metaclass layout conflict),
# we must instead create a wrap-around type that can be used with
# the AtomicMeta class
if TYPE_CHECKING:

    class Genericizable(Generic[Unpack[Ts]]): ...

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

        def __class_getitem__(cls, key):
            from . import public_class

            if not isinstance(key, tuple):
                args = (key,)
            else:
                args = key
            if cls is Genericizable:
                return new_class(
                    f"Genericable[{args!s}]",
                    (cls,),
                    exec_body=lambda ns: ns.update(
                        {
                            "__slots__": (),
                            "__parameters__": args,
                        }
                    ),
                )

            cls = public_class(cls)
            if cls.__parameters__ and len(args) == len(cls.__parameters__):
                params = cls.__parameters__
                param_mapping = {p: n for p, n in zip(cls.__parameters__, args)}
                new_params = tuple(
                    t if not isinstance(param_mapping[t], TypeVar) else param_mapping[t]
                    for t in params
                )
                try:
                    cached_generics = generic_cache[cls]
                    return cached_generics[args]
                except KeyError:
                    cached_generics = generic_cache[cls] = WeakValueDictionary()

                new_annotations = {}
                complex_fields = []
                typehints = get_type_hints(cls, include_extras=True)
                for field_name in cls.__parameters_by_field__:
                    typevar_params = cls.__parameters_by_field__[field_name]
                    typehint = typehints[field_name]
                    if isinstance(typehint, TypeVar):
                        new_annotations[field_name] = param_mapping[typehint]
                    else:
                        complex_fields.append(field_name)

                for attr_name in cls.__parameters_by_field__.keys() & frozenset(complex_fields):
                    typevar_params = cls.__parameters_by_field__[attr_name]
                    attr_type_args = []
                    for new_type, typevar in zip(args, typevar_params):
                        attr_type_args.append(new_type)
                    type_genericable = cls._columns[attr_name]
                    new_annotations[attr_name] = type_genericable[tuple(attr_type_args)]
                new_cls = cached_generics[args] = type(
                    cls.__name__,
                    (cls - frozenset(new_annotations.keys()),),
                    {
                        "__annotations__": new_annotations,
                        "__args__": args,
                        "__parameters__": new_params,
                        "__module__": cls.__module__,
                    },
                )

                return new_cls
            raise TypeError(f"{cls} is not a generic class")


class BaseAtomic(AbstractAtomic):
    __slots__ = ()

    @mark(base_cls=True)
    def _clear(self: Self, fields: Iterable[str] | None = None):
        pass

    if TYPE_CHECKING:
        __public_class__: Callable[[], type[Atomic]]

        def _asdict(self: Self) -> dict[str, Any]: ...

        def _astuple(self: Self) -> tuple[Any, ...]: ...

        def _aslist(self: Self) -> list[Any]: ...

    @mark(base_cls=True)
    def _set_defaults(self: Self) -> Self:
        # ARJ: Override to set defaults instead of inside the `__init__` function
        # Note: Always call ``super()._set_defaults()`` FIRST as if you
        # call it afterwards, the inheritance tree will zero initialize it first
        return self


@overload
def is_atomic_instance(item: type) -> TypeGuard[type[Atomic]]: ...


@overload
def is_atomic_instance(item: object) -> TypeGuard[Atomic]: ...


def is_atomic_instance(item):
    if isinstance(item, type):
        return BaseAtomic in item.mro()
    cls = type(item)
    return BaseAtomic in cls.mro()


class AttrsDict(UserDict, Generic[T]):
    def __getattr__(self, key: str) -> T | None:
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
    cast_type: type[tuple[T, ...]] | type[set[T]] | None

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
    cast_type: type[FrozenMapping[T, U]] | None

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
    item: BaseReadOnly, cls: type[Collection[T]]
) -> TypeGuard[ImmutableCollection[T]]:
    return isinstance(item.value, cls)


def _caculate_hash(mapping) -> int:
    keys = sorted(mapping)
    return hash(tuple((hash(key), hash(mapping[key])) for key in keys))


FROZEN_MAPPING_SINGLETONS: Mapping[int, Any] = WeakValueDictionary()


class FrozenMapping(Mapping[T, U]):
    __slots__ = "__value", "__hashcode", "__weakref__"

    __value: dict[T, U]
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


EMPTY_TERMINUS: frozenset[frozenset | FrozenMapping | None | str] = frozenset(
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
    def __call__(self, instance: T_cta, *args, **kwargs) -> Any: ...


class ClassCallable(Protocol[T_cta]):
    def __call__(self, cls: type[T_cta], *args, **kwargs) -> Any: ...


class BoundClassOrInstanceAttribute(Generic[T]):
    """
    simple __get__ descriptor to branch between calling
    an instance method (from inside the instance) and a classmethod when
    accessed from outside the instance.
    """

    __slots__ = "_class_attribute", "_instance_attribute", "_classes", "_attr_names"
    _class_attribute: ClassCallable[T] | None | Any
    _instance_attribute: InstanceCallable[T] | Any | None
    _classes: WeakKeyDictionary[type[T], MethodType]
    _attr_names: WeakKeyDictionary[type[T], str]
    _call_immediately: bool

    def __set_name__(self: Self, owner: type[T], name: str):
        self._attr_names[owner] = name

    def __init__(
        self,
        class_attr: ClassCallable[T] | None = None,
        instance_attr: InstanceCallable[T] | None = None,
    ) -> None:
        self._classes = WeakKeyDictionary()
        self._attr_names = WeakKeyDictionary()
        self._class_attribute = class_attr
        self._instance_attribute = instance_attr

    def getter(self, func, *, to: Literal["self", "class", ""] = ""):
        if not callable(func):
            raise TypeError(func)
        sig = inspect.signature(func)
        is_instance_func = "self" == to
        is_class_func = "class" == to
        if not any((is_instance_func, is_class_func)):
            for param_name in sig.parameters:
                if param_name == "self":
                    is_instance_func = True
                    break
                elif param_name == "cls":
                    is_class_func = True
                    break
        if is_class_func:
            return self.class_attr(func)
        elif is_instance_func:
            return self.instance_attr(func)
        raise ValueError(f"Unable to locate self or cls param in {func.__name__}{sig!s}")

    def instance_attr(self, instance_attr) -> Self:
        self._instance_attribute = instance_attr
        return self

    def class_attr(self, class_attr) -> Self:
        self._class_attribute = class_attr
        return self

    def __get__(self, instance: T | None, owner: type[T]) -> MethodType:
        if is_atomic_instance(instance):
            assert is_atomic_instance(owner)
            owner = cast_type(type[T], owner.__public_class__())
        try:
            attr_name = self._attr_names[owner]
        except KeyError:
            attr_name = "??? (__set_name__ not called!)"

        if instance is None:
            assert owner is not None
            if self._class_attribute is None:
                raise AttributeError(
                    f"property '{attr_name}' of '{owner.__name__}' object has no class_attr set!"
                )
            try:
                return self._classes[owner]
            except KeyError:
                class_attr = self._class_attribute
                if callable(class_attr):
                    class_attr = MethodType(class_attr, owner)
                value = self._classes[owner] = class_attr
                return value
        if self._instance_attribute is None:
            raise AttributeError(
                f"property '{attr_name}' of '{owner.__name__}' object has no instance_attr set!"
            )
        if callable(self._instance_attribute):
            return MethodType(self._instance_attribute, instance)
        return self._instance_attribute


class ClassOrInstanceFuncsDescriptor(BoundClassOrInstanceAttribute[T]):
    __slots__ = ()

    def instance_function(
        self, instance_attr: InstanceCallable
    ) -> BoundClassOrInstanceAttribute[T]:
        self._instance_attribute = instance_attr
        return self

    def class_function(self, class_attr: ClassCallable) -> BoundClassOrInstanceAttribute[T]:
        self._class_attribute = class_attr
        return self

    def __get__(self, instance: T | None, owner: type[T]) -> MethodType:
        thunk = super().__get__(instance, owner)
        assert thunk is not None
        return thunk()


class ClassOrInstanceFuncsDataDescriptor(ClassOrInstanceFuncsDescriptor):
    __slots__ = (
        "_instance_setter_function",
        "_instance_deleter_function",
        "_class_setter_function",
        "_class_deleter_function",
    )

    def __init__(
        self,
        class_function: ClassCallable[T] | None = None,
        instance_function: InstanceCallable[T] | None = None,
        *,
        instance_setter: InstanceCallable[T] | None = None,
        instance_deleter: InstanceCallable[T] | None = None,
        class_setter: ClassCallable[T] | None = None,
        class_deleter: ClassCallable[T] | None = None,
    ) -> None:
        super().__init__(class_function, instance_function)
        self._instance_setter_function = instance_setter
        self._instance_deleter_function = instance_deleter
        self._class_setter_function = class_setter
        self._class_deleter_function = class_deleter

    def setter(self, func, *, to: Literal["self", "class", ""] = ""):
        if not callable(func):
            raise TypeError(func)
        sig = inspect.signature(func)
        is_instance_func = "self" == to
        is_class_func = "class" == to
        if not any((is_instance_func, is_class_func)):
            for param_name in sig.parameters:
                if param_name == "self":
                    is_instance_func = True
                    break
                elif param_name == "cls":
                    is_class_func = True
                    break
        if is_class_func:
            self._class_setter_function = func
            return
        if is_instance_func:
            self._instance_setter_function = func
            return
        raise ValueError(f"Unable to locate self or cls param in {func.__name__}{sig!s}")

    def deleter(self, func, *, to: Literal["self", "class", ""] = ""):
        if not callable(func):
            raise TypeError(func)
        sig = inspect.signature(func)
        is_instance_func = "self" == to
        is_class_func = "class" == to
        if not any((is_instance_func, is_class_func)):
            for param_name in sig.parameters:
                if param_name == "self":
                    is_instance_func = True
                    break
                elif param_name == "cls":
                    is_class_func = True
                    break
        if is_class_func:
            self._class_deleter_function = func
            return
        if is_instance_func:
            self._instance_deleter_function = func
            return
        raise ValueError(f"Unable to locate self or cls param in {func.__name__}{sig!s}")

    def __set__(self, instance, value):
        cls = type(instance)
        if isinstance(instance, BaseAtomic):
            cls = cls.__public_class__()
        try:
            attr_name = self._attr_names[cls]
        except KeyError:
            attr_name = "??? (__set_name__ not called!)"

        if self._instance_setter_function is None:
            raise AttributeError(
                f"property '{attr_name}' of '{cls.__name__}' "
                "object has no instance_setter_function set!"
            )
        bound_thunk = MethodType(self._instance_setter_function, instance)
        return bound_thunk(value)

    def __delete__(self, instance: T | Atomic) -> MethodType:
        cls: type[Atomic] | type[T]
        if isinstance(instance, BaseAtomic):
            cls = type(instance).__public_class__()
        else:
            cls = type(instance)
        try:
            attr_name = self._attr_names[cls]
        except KeyError:
            attr_name = "??? (__set_name__ not called!)"

        if self._instance_setter_function is None:
            raise AttributeError(
                f"property '{attr_name}' of '{cls.__name__}' "
                "object has no instance_setter_function set!"
            )
        assert self._instance_deleter_function is not None
        return MethodType(self._instance_deleter_function, instance)


@as_collectable(FrozenMapping)
def flatten_fields(item) -> Iterable[tuple[str, None | FrozenMapping]]:
    if isinstance(item, str):
        yield (item, None)
    elif isinstance(item, (AbstractIterable, AbstractMapping)) and not isinstance(
        item, (bytearray, bytes)
    ):
        iterable: Iterable[Any] | Iterable[tuple[Any, Any]]
        is_mapping = False
        if isinstance(item, AbstractMapping):
            iterable = ((key, item[key]) for key in item)
            is_mapping = True
        else:
            iterable = item
        for element in iterable:
            if is_mapping:
                key, value = element
                if isinstance(value, str):
                    yield (key, FrozenMapping({value: None}))
                    continue
                values = flatten_fields.collect(value)
                if len(values) == 0:
                    yield (key, None)
                    continue
                yield (key, values)
                continue
            if isinstance(element, str):
                yield (element, None)
            else:
                yield from flatten_fields(element)
    elif item is None:
        return
    else:
        raise NotImplementedError(f"Unsupported type {type(item).__qualname__}")
