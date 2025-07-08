from contextlib import suppress
import sys
from collections.abc import Collection as AbstractCollection, Callable as AbstractCallable
from types import SimpleNamespace as _SimpleNamespace
import uuid
import inspect
from typing import (
    Collection,
    ClassVar,
    Tuple,
    Dict,
    Type,
    Callable,
    Union,
    Any,
    Generic,
    Optional,
    List,
    get_type_hints,
    ForwardRef,
    overload,
)
from typing import Final, TYPE_CHECKING

from .compat import (
    TypeVar,
    TypeVarTuple,
    Protocol,
    ParamSpec,
    Literal,
    TypeGuard,
    TypeAliasType,
    EllipsisType,
    TypeAlias,
    Self,
    get_args,
    get_origin as _get_origin,
    Annotated,
    typevar_has_no_default,
)
from .types import BaseAtomic

NoneType = type(None)
CoerceMapping = Dict[str, Tuple[Union[Type, Tuple[Type, ...]], Callable]]

HAS_GET_ANNOTATIONS = callable(getattr(inspect, "get_annotations", None))

T = TypeVar("T")
Ts = TypeVarTuple("Ts")
U = TypeVar("U")
T_co = TypeVar("T_co", covariant=True)
U_co = TypeVar("U_co", covariant=True)
T_cta = TypeVar("T_cta", contravariant=True)


class CustomTypeCheck(Generic[T]):
    """
    A runtime pseudo-type object that represents a complex type-hint.

    If ``isinstance(value, self)`` is called, it will execute a function that
    verifies if the value matches the type-hint.
    """

    __slots__ = ()


P = ParamSpec("P")


class InstanceMethod(Protocol[T, P]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs): ...

    __self__: T
    __name__: str
    __qualname__: str


class ClassMethod(Protocol[T]):
    __self__: Type[Self]
    __name__: str
    __qualname__: str
    __func__: Callable[[Type[T]], T]

    def __call__(self: Self, *args, **kwargs) -> T: ...


class CastType(Protocol[T_co, U_co]):
    def __call__(self: T_co, value: Any, *args, **kwargs) -> U_co: ...


# ARJ: Used to signal "I have done nothing to this function"
class ParentCastType(CastType[T_co, U_co]):
    __only_parent_cast__: Literal[True]


# ARJ: Used to signal "I have mutated this cast type"
class MutatedCastType(CastType[T_co, U_co]):
    __union_subtypes__: Tuple[Union[Type[U_co], Tuple[Type[U_co], ...]], Callable[[Any], U_co]]


def is_cast_type(item: Callable[[Any], T]) -> TypeGuard[Type[CastType[T, T]]]:
    return callable(item)


def is_parent_cast_type(item: CastType[T, T]) -> TypeGuard[Type[ParentCastType[T, T]]]:
    return getattr(item, "__only_parent_cast__", False)


def is_mutated_cast_type(
    item: CastType[T, U],
) -> TypeGuard[Type[MutatedCastType[T, U]]]:
    return getattr(item, "__union_subtypes__", False)


def isclassmethod(function: Callable[[Any], T]) -> TypeGuard[ClassMethod[T]]:
    return (
        callable(function)
        and hasattr(function, "__func__")
        and hasattr(function, "__self__")
        and isinstance(function.__self__, type)
    )


TYPING_MODULE_NAME: Final = "typing"
TYPING_EXTENSIONS_MODULE_NAME: Final = "typing_extensions"


class TypingDefinition(Protocol):
    __module__: Literal["typing", "typing_extensions"]
    __name__: ClassVar[str]
    __qualname__: ClassVar[str]


def is_typing_definition(item: Any) -> TypeGuard[TypingDefinition]:
    """
    Check if the given item is a type hint.
    """

    with suppress(AttributeError):
        cls_module = type(item).__module__
        if cls_module in (
            TYPING_MODULE_NAME,
            TYPING_EXTENSIONS_MODULE_NAME,
        ) or cls_module.startswith((f"{TYPING_MODULE_NAME}.", f"{TYPING_EXTENSIONS_MODULE_NAME}.")):
            return True
    with suppress(AttributeError):
        module = item.__module__
        if module in (
            TYPING_MODULE_NAME,
            TYPING_EXTENSIONS_MODULE_NAME,
        ) or module.startswith((f"{TYPING_MODULE_NAME}.", f"{TYPING_EXTENSIONS_MODULE_NAME}.")):
            return True
    if isinstance(item, (TypeVar, TypeVarTuple, ParamSpec)):
        return True
    origin = get_origin(item)
    args = get_args(item)
    if origin is not None:
        return True
    elif args:
        return True
    return False


assert isinstance(T, TypeVar)
assert isinstance(U, TypeVar)

HeterogenousTuple = TypeAliasType("HeterogenousTuple", Tuple[T, U], type_params=(T, U))
VariadicTupleHint = TypeAliasType(
    "VariadicTupleHint", HeterogenousTuple[T, EllipsisType], type_params=(T,)
)
HomogenousTuple = TypeAliasType("HomogenousTuple", Tuple[T, T], type_params=(T,))


def is_anonymous_pair(t: Union[Any, Tuple[T, U]]) -> TypeGuard[Tuple[T, U]]:
    if isinstance(t, tuple) and len(t) == 2:
        a, b = t
        if isinstance(b, EllipsisType):
            assert isinstance(a, type) or is_typing_definition(a)
            return True
        return True
    return False


def isabstractcollectiontype(
    o: Union[TypingDefinition, Type[Any], Type[T]],
) -> TypeGuard[Type[Collection[T]]]:
    cls: Union[Type[Any], Type[T]]
    if is_typing_definition(o):
        origin = get_origin(o)
        if origin is not None:
            return isabstractcollectiontype(origin)
        return False
    if not isinstance(o, type):
        return False
    assert isinstance(o, type)
    cls = o
    if not cls.__module__.startswith("collections.abc"):
        return False
    return issubclass(cls, AbstractCollection)


TypeHint: TypeAlias = Union[TypingDefinition, Type]

if TYPE_CHECKING:

    class Atomic(BaseAtomic, Generic): ...
else:
    Atomic = BaseAtomic

JSONValue: TypeAlias = Optional[Union[str, int, float, bool]]
JSON: TypeAlias = Union[
    Dict[str, Union[JSONValue, "JSON"]],
    Tuple[Union["JSON", JSONValue], ...],
    List[Union["JSON", JSONValue]],
    JSONValue,
]

_GET_TYPEHINTS_ALLOWS_EXTRA = "include_extras" in inspect.signature(get_type_hints).parameters

Annotated  # noqa

typevar_has_no_default  # noqa


class HasJSONMagicMethod(Protocol):
    def __json__(self) -> Dict[str, JSON]: ...


class HasToJSON(Protocol):
    def to_json(self) -> Dict[str, JSON]: ...


class ExceptionJSONSerializable(Protocol):
    def __json__(self) -> Dict[str, JSON]: ...


class ExceptionHasDebuggingInfo(Protocol):
    debugging_info: Dict[str, JSON]


class ExceptionHasMetadata(Protocol):
    metadata: Dict[str, JSON]


def exception_is_jsonable(
    e: Exception,
) -> TypeGuard[Union[HasJSONMagicMethod, HasToJSON]]:
    return callable(getattr(e, "__json__", None)) or callable(getattr(e, "to_json", None))


class ICopyWithable(Protocol[T_co]):
    def copy_with(self: T_co, args) -> T_co: ...


def is_copywithable(
    t: Union[Type[Any], TypeHint],
) -> TypeGuard[ICopyWithable[TypeHint]]:
    return callable(getattr(t, "copy_with", None))


if sys.version_info[:2] >= (3, 10):
    from types import UnionType

    UnionTypes = (Union, UnionType)

    def _forward_union_ref_for(hint_ref_name: str, hint: Tuple[Type, ...]):
        return " | ".join(f"{hint_ref_name}[{i}]" for i in range(len(hint))), hint

    # patch get_origin to always return a Union over a 'a | b'
    def get_origin(cls):  # type:ignore[no-redef]
        t = _get_origin(cls)
        if isinstance(t, type) and issubclass(t, UnionType):
            return Union
        return t

    def copy_with(hint: TypeHint, args) -> TypeHint:
        if isinstance(hint, UnionType):
            return Union[args]
        if is_copywithable(hint):
            return hint.copy_with(args)
        type_cls = get_origin(hint)
        with suppress(AttributeError):
            if type_cls is not None:
                return type_cls[args]
        raise NotImplementedError(f"Unable to copy with new type args on {hint!r} ({type(hint)!r})")

    def make_union(
        *args,
        locals=None,
        globals=None,
        frame=None,
    ):
        if locals is None or globals is None:
            if frame is None:
                frame = inspect.currentframe()
                if frame.f_back:
                    frame = frame.f_back
            try:
                if locals is None:
                    locals = {**frame.f_locals}
                if globals is None:
                    globals = {**frame.f_globals}
            finally:
                del frame
        parsed_hints = resolve(*args, locals=locals, globals=globals)
        if len(args) == 1:
            return parsed_hints
        ns = {}
        hint_parts = []
        for arg in parsed_hints:
            key = f"id_{id(arg)}"
            if isinstance(arg, str):
                raise TypeError(arg)
            ns[key] = arg
            hint_parts.append(key)
        hint = " | ".join(hint_parts)
        return resolve(hint, locals=ns)

    def make_tuple(*args, locals=None, globals=None, frame=None):
        if locals is None or globals is None:
            if frame is None:
                frame = inspect.currentframe()
                if frame.f_back:
                    frame = frame.f_back
            try:
                if locals is None:
                    locals = {**frame.f_locals}
                if globals is None:
                    globals = {**frame.f_globals}
            finally:
                del frame
        parsed_hints = resolve(*args, locals=locals, globals=globals)
        return tuple[*parsed_hints]


else:
    UnionTypes = (Union,)
    get_origin = _get_origin

    def _forward_union_ref_for(hint_ref_name: str, hint: Tuple[Type, ...]):
        return hint_ref_name, Union[*hint]

    def copy_with(hint, args):
        return hint.copy_with(args)

    def make_union(*args, locals=None, globals=None, frame=None):
        if locals is None or globals is None:
            if frame is None:
                frame = inspect.currentframe()
                if frame.f_back:
                    frame = frame.f_back
            try:
                if locals is None:
                    locals = {**frame.f_locals}
                if globals is None:
                    globals = {**frame.f_globals}
            finally:
                del frame

        args = resolve(*args, locals=locals, globals=globals)
        if len(args) == 1:
            return args[0]
        ns = {}
        hint_parts = []
        for arg in args:
            key = f"id_{id(arg)}"
            ns[key] = arg
            hint_parts.append(key)
        hint = " , ".join(hint_parts)
        return resolve(f"typing.Union[{hint}]", locals=ns)

    def make_tuple(*args, locals=None, globals=None, frame=None):
        if locals is None or globals is None:
            if frame is None:
                frame = inspect.currentframe()
                if frame.f_back:
                    frame = frame.f_back
            try:
                if locals is None:
                    locals = {**frame.f_locals}
                if globals is None:
                    globals = {**frame.f_globals}
            finally:
                del frame
        parsed_hints = resolve(*args, locals=locals, globals=globals)
        return Tuple[*parsed_hints]


@overload
def resolve(hint: TypeHint | str, locals=None, globals=None) -> TypeHint:
    pass


@overload
def resolve(
    hint: TypeHint | str, *hints: TypeHint | str, locals=None, globals=None
) -> Tuple[TypeHint, ...]:
    pass


@overload
def resolve(hint: dict[str, TypeHint | str], locals=None, globals=None) -> dict[str, TypeHint]: ...


def resolve(*hints, locals=None, globals=None, frame=None):
    """
    Parse a hint into a hint type
    """

    if locals is None or globals is None:
        if frame is None:
            frame = inspect.currentframe()
            if frame.f_back:
                frame = frame.f_back
        try:
            if locals is None:
                locals = frame.f_locals.copy()
            if globals is None:
                globals = frame.f_globals.copy()
        finally:
            del frame

    if len(hints) == 1:
        if isinstance(hints[0], dict):
            m = hints[0]
            m_keys = tuple(m)
            m_values = resolve((m[key] for key in m_keys), globals=globals, locals=locals)
            if not isinstance(m_values, tuple):
                m_values = (m_values,)
            return {key: value for key, value in zip(m_keys, m_values)}
        elif inspect.isgenerator(hints[0]):
            return resolve(*tuple(hints[0]), globals=globals, locals=locals)

    ann = {}
    parsed_hint_refs = []
    for hint in hints:
        hint_ref_name = f"hint_{uuid.uuid4().hex}"
        if isinstance(hint, str):
            hint_forward = ForwardRef(hint)
            ann[hint_ref_name] = hint_forward
            parsed_hint_refs.append(hint_ref_name)
        else:
            hint_ref_value = hint_ref_name
            # Python 3.12 doesn't like a ForwardRef returning a tuple,
            # so rewrite it...
            if isinstance(hint, tuple):
                hint_ref_value, hint = _forward_union_ref_for(hint_ref_name, hint)
            locals[hint_ref_name] = hint
            ann[hint_ref_name] = ForwardRef(hint_ref_value)
            parsed_hint_refs.append(hint_ref_name)

    o = _SimpleNamespace(__annotations__=ann)
    if _GET_TYPEHINTS_ALLOWS_EXTRA:
        m = get_type_hints(o, locals, globals, include_extras=True)
    else:
        m = get_type_hints(o, locals, globals)
    parsed_hints = []
    for ref in parsed_hint_refs:
        parsed_hint = m[ref]
        parsed_hints.append(parsed_hint)
    if len(hints) == 1:
        return parsed_hints[0]
    return tuple(parsed_hints)


if HAS_GET_ANNOTATIONS:

    def get_annotations(item, *, globals=None, locals=None, eval_str=False, frame=None):
        if locals is None or globals is None:
            if frame is None:
                frame = inspect.currentframe()
                if frame.f_back:
                    frame = frame.f_back
            try:
                if locals is None:
                    locals = frame.f_locals.copy()
                if globals is None:
                    globals = frame.f_globals.copy()
            finally:
                del frame

        if isinstance(item, str) or is_typing_definition(item):
            item = resolve(item, globals=globals, locals=locals)
        if isinstance(item, (type, AbstractCallable)) or inspect.ismodule(item):
            return inspect.get_annotations(item, globals=globals, locals=locals, eval_str=eval_str)
        raise TypeError(item)
else:
    _uniq = object()

    def get_annotations(item, *, globals=None, locals=None, eval_str=False, frame=None):
        if locals is None or globals is None:
            if frame is None:
                frame = inspect.currentframe()
                if frame.f_back:
                    frame = frame.f_back
            try:
                if locals is None:
                    locals = frame.f_locals.copy()
                if globals is None:
                    globals = frame.f_globals.copy()
            finally:
                del frame

        if isinstance(item, str) or is_typing_definition(item):
            item = resolve(item, globals=globals, locals=locals)
        if isinstance(item, (type, AbstractCallable)) or inspect.ismodule(item):
            v = inspect.getattr_static(item, "__annotations__", _uniq)
            if v is _uniq:
                return {}
            return v
        raise TypeError(item)
