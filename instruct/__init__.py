from __future__ import annotations

import inspect
import logging
import os
import tempfile
import time
import sys
import types
import typing

from base64 import urlsafe_b64encode
from collections.abc import (
    Mapping as AbstractMapping,
    Sequence,
    ItemsView as _ItemsView,
    MappingView,
    Set as AbstractSet,
    KeysView,
)
from collections import ChainMap
from enum import IntEnum
from importlib import import_module
from itertools import chain
from types import CodeType, FunctionType, SimpleNamespace
from typing import (
    Any,
    Callable,
    cast,
    Dict,
    FrozenSet,
    get_type_hints,
    Iterable,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    Type,
    TYPE_CHECKING,
    Union,
)
from weakref import WeakValueDictionary

import inflection
from jinja2 import Environment, PackageLoader

from .about import __version__
from .typedef import (
    parse_typedef,
    ismetasubclass,
    is_typing_definition,
    find_class_in_definition,
    get_origin,
    get_args,
    Annotated,
)
from .typing import T, CellType, CoerceMapping, NoneType
from .types import FrozenMapping, ReadOnly, AttrsDict, ClassOrInstanceFuncsDescriptor
from .utils import flatten_fields
from .subtype import wrapper_for_type
from .exceptions import (
    OrphanedListenersError,
    MissingGetterSetterTemplateError,
    InvalidPostCoerceAttributeNames,
    CoerceMappingValueError,
    ClassCreationFailed,
    RangeError,
)
from .constants import NoPickle, NoJSON, NoIterable, Range, NoHistory, RangeFlags

__version__  # Silence unused import warning.

logger = logging.getLogger(__name__)
env = Environment(loader=PackageLoader(__name__, "templates"))
env.globals["tuple"] = tuple
env.globals["repr"] = repr
env.globals["frozenset"] = frozenset
env.globals["chain"] = chain

AFFIRMATIVE = frozenset(("1", "true", "yes", "y", "aye"))

# Public helpers

_GET_TYPEHINTS_ALLOWS_EXTRA = "include_extras" in inspect.signature(get_type_hints).parameters
_NATIVE_CLOSURE_SUPPORT = "closure" in inspect.signature(exec).parameters
_SUPPORTED_CELLTYPE = hasattr(types, "CellType")


def public_class(
    instance_or_type: Union[Type[T], T], *property_path: str, preserve_subtraction: bool = False
) -> Type[T]:
    """
    Given a data class or instance of, give us the public facing
    class.

    preserve_subtraction indicates that we want the public facing subtracted class as opposed
    to its root parent.
    """
    if not isinstance(instance_or_type, type):
        cls: Type[T] = type(instance_or_type)
    else:
        cls: Type[T] = instance_or_type
    if not isinstance(cls, Atomic):
        raise TypeError(f"Can only call on Atomic-metaclassed types!, {cls}")
    if property_path:
        key, *rest = property_path
        if key not in cls._slots:
            raise ValueError(f"{key!r} is not a field on {cls.__name__}!")
        next_cls = cls._slots[key]
        if get_origin(next_cls) is Annotated:
            next_cls, *_ = get_args(next_cls)
        if key in cls._nested_atomic_collection_keys:
            atomic_classes = cls._nested_atomic_collection_keys[key]
            if len(atomic_classes) > 1:
                if rest:
                    if isinstance(rest[0], int):
                        next_cls = atomic_classes[rest[0]]
                        del rest[0]
                    else:
                        raise AttributeError(
                            f"Unknown property {rest[0]} on class collection tuple for {key}"
                        )
                else:
                    public_atomic_classes = tuple(
                        public_class(typecls, preserve_subtraction=preserve_subtraction)
                        for typecls in atomic_classes
                    )
                    if (
                        len(frozenset(public_atomic_classes)) == 1
                        and len(public_atomic_classes) > 1
                    ):
                        return public_atomic_classes[0]
                    return public_atomic_classes
            else:
                next_cls, = atomic_classes
        return public_class(next_cls, *rest, preserve_subtraction=preserve_subtraction)
    cls = cls.__public_class__()
    if preserve_subtraction and any((cls._skipped_fields, cls._modified_fields)):
        return cls
    if any((cls._skipped_fields, cls._modified_fields)):
        bases = tuple(x for x in cls.__bases__ if ismetasubclass(x, Atomic))
        while len(bases) == 1 and any((bases[0]._skipped_fields, bases[0]._modified_fields)):
            bases = tuple(x for x in cls.__bases__ if ismetasubclass(x, Atomic))
        if len(bases) == 1:
            return bases[0]
    return cls


def clear(instance: T, fields: Optional[Iterable[str]] = None) -> T:
    """
    Clear all fields on an instruct class instance.
    """
    if isinstance(instance, type):
        raise TypeError("Can only call on an Atomic-metaclassed instance! You passed in a type!")
    if not isinstance(instance.__class__, Atomic):
        raise TypeError("Can only call on an Atomic-metaclassed type!")
    if fields:
        unrecognized_keys = frozenset(fields) - frozenset(keys(instance))
        if unrecognized_keys:
            instance._handle_init_errors([], [], unrecognized_keys)
    instance._clear(fields=fields)
    return instance


def reset_to_defaults(instance: T, *, call_init_again: bool = False) -> T:
    """
    Clears an object and reinitializes to the values specified by
    ``_set_defaults``.

    call_init_again: call the instances `__init__` again (useful if you did
    default initialization inside `__init__`).
    """
    clear(instance)
    instance._set_defaults()
    if call_init_again:
        instance.__init__()
    return instance


def keys(
    instance_or_cls: Union[Type[T], T], *property_path: str, all: bool = False
) -> Union[AtomicKeysView, KeysView, Mapping[Type, KeysView]]:
    """
    Return the public class fields on an instance or type.

    If passed a field name string, then reach into it and attempt to call
    keys(...) on it.
    """
    if not isinstance(instance_or_cls, type):
        cls = type(instance_or_cls)
        instance = instance_or_cls
    else:
        cls = instance_or_cls
        instance = None
    if not isinstance(cls, Atomic):
        raise TypeError(f"Can only call on Atomic-metaclassed types!, {cls}")
    if not property_path:
        if instance is not None and not all:
            return AtomicKeysView(instance)
        if all:
            # Known as a KeysView as well
            return cls._all_accessible_fields
        return KeysView(tuple(cls._slots))
    if len(property_path) == 1:
        key, = property_path
        if key not in cls._nested_atomic_collection_keys:
            return keys(cls._slots[key])
        if len(cls._nested_atomic_collection_keys[key]) == 1:
            return keys(cls._nested_atomic_collection_keys[key][0])
        return {type_cls: keys(type_cls) for type_cls in cls._nested_atomic_collection_keys[key]}
    key, *property_path = property_path
    if key in cls._nested_atomic_collection_keys:
        return keys(cls._nested_atomic_collection_keys[key], *property_path)
    return keys(cls._slots[key], *property_path)


def values(instance) -> AtomicValuesView:
    """
    Analogous to dict.values(...)
    """
    cls = type(instance)
    if not isinstance(cls, Atomic):
        raise TypeError("Can only call on Atomic-metaclassed types!")
    if instance is not None:
        return AtomicValuesView(instance)
    raise TypeError(f"values of a {cls} object needs to be called on an instance of {cls}")


def items(instance: T) -> ItemsView:
    """
    Analogous to dict.items(...)
    """
    cls: Type[T] = type(instance)
    if not isinstance(cls, Atomic):
        raise TypeError("Can only call on Atomic-metaclassed types!")
    if instance is not None:
        return ItemsView(instance)
    raise TypeError(f"items of a {cls} object needs to be called on an instance of {cls}")


def get(instance: T, key, default=None) -> Optional[Any]:
    """
    Access the field at the key given, return the default value if it does not
    exist on the type.
    """
    cls: Type[T] = type(instance)
    if not isinstance(cls, Atomic):
        raise TypeError("Can only call on Atomic-metaclassed types!")
    if instance is None:
        raise TypeError(f"items of a {cls} object needs to be called on an instance of {cls}")
    try:
        return instance[key]
    except KeyError:
        return default


def asdict(instance: T) -> Dict[str, Any]:
    """
    Return a dictionary version of the instance
    """
    cls: Type[T] = type(instance)
    if not isinstance(cls, Atomic):
        raise TypeError("Must be an Atomic-metaclassed type!")
    return instance._asdict()


def astuple(instance: T) -> Tuple[Any, ...]:
    """
    Return a tuple of values from the instance
    """
    cls: Type[T] = type(instance)
    if not isinstance(cls, Atomic):
        raise TypeError("Must be an Atomic-metaclassed type!")
    return instance._astuple()


def aslist(instance: T) -> List[Any]:
    """
    Return a list of values from the instance
    """
    cls: Type[T] = type(instance)
    if not isinstance(cls, Atomic):
        raise TypeError("Must be an Atomic-metaclassed type!")
    return instance._aslist()


def show_all_fields(
    instance_or_cls: Union[T, Type[T]], *, deep_traverse_on: Optional[Mapping[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a tree of all the fields supported in the instruct class and any
    embedded instruct classes.

    deep_traverse_on: only descend if the same key exists in the provided mapping,
        if None, always descend.
    """
    if not isinstance(instance_or_cls, type):
        cls = type(instance_or_cls)
    else:
        cls = instance_or_cls
    if not isinstance(cls, Atomic):
        raise TypeError("Must be an Atomic-metaclassed type!")
    all_fields = {}
    for key, value in cls._slots.items():
        all_fields[key] = {}
        if deep_traverse_on is None or key in deep_traverse_on:
            next_deep_level = None
            if deep_traverse_on is not None:
                next_deep_level = deep_traverse_on[key]
            if key in cls._nested_atomic_collection_keys:
                for item in cls._nested_atomic_collection_keys[key]:
                    all_fields[key].update(show_all_fields(item, deep_traverse_on=next_deep_level))
            elif ismetasubclass(value, Atomic):
                all_fields[key].update(show_all_fields(value, deep_traverse_on=next_deep_level))
        if not all_fields[key]:
            all_fields[key] = None
    return all_fields


# End of public helpers


def _dump_skipped_fields(cls) -> Optional[FrozenMapping[str, Any]]:
    assert isinstance(cls, type), f"{cls} is not a class"
    skipped = {key: None for key in cls._skipped_fields}
    for key in cls._slots:
        typedef = cls._slots[key]
        if key in cls._nested_atomic_collection_keys:
            skipped_on_typedef_merged = {}
            for typedef in cls._nested_atomic_collection_keys[key]:
                skipped_on_typedef = _dump_skipped_fields(typedef)
                if skipped_on_typedef:
                    skipped_on_typedef_merged.update(skipped_on_typedef)
            if skipped_on_typedef_merged:
                skipped[key] = skipped_on_typedef_merged
        elif ismetasubclass(typedef, Atomic):
            skipped_on_typedef = _dump_skipped_fields(typedef)
            if skipped_on_typedef:
                skipped[key] = skipped_on_typedef
    if not skipped:
        return None
    return FrozenMapping(skipped)


class ItemsView(_ItemsView):
    __slots__ = ()
    if TYPE_CHECKING:
        _mapping: Mapping[str, Any]

    def __iter__(self):
        yield from self._mapping


class AtomicValuesView(MappingView):
    __slots__ = ()

    def __contains__(self, value):
        for key, current_value in self._mapping:
            if current_value == value:
                return True
        return False

    def __iter__(self):
        for key, value in self._mapping:
            yield value


class AtomicKeysView(MappingView, AbstractSet):
    __slots__ = ()

    @classmethod
    def _from_iterable(self, it):
        return set(it)

    def __contains__(self, key):
        return key in self._mapping

    def __iter__(self):
        yield from keys(self._mapping.__class__)


def make_fast_clear(fields, set_block, class_name):
    set_block = set_block.format(key="%(key)s")
    code_template = env.get_template("fast_clear.jinja").render(
        fields=fields, setter_variable_template=set_block, class_name=class_name
    )
    return code_template


def make_fast_dumps(fields, class_name):
    code_template = env.get_template("fast_dumps.jinja").render(
        fields=fields, class_name=class_name
    )
    return code_template


def make_fast_getset_item(
    fields: List[str],
    properties: List[str],
    class_name: str,
    get_variable_template: str,
    set_variable_template: str,
):
    code_template = env.get_template("fast_getitem.jinja").render(
        fields=fields,
        properties=properties,
        class_name=class_name,
        get_variable_template=get_variable_template,
        set_variable_template=set_variable_template,
    )
    return code_template


def make_fast_eq(fields):
    code_template = env.get_template("fast_eq.jinja").render(fields=fields)
    return code_template


def make_fast_iter(fields):
    code_template = env.get_template("fast_iter.jinja").render(fields=fields)
    return code_template


def make_set_get_states(fields):
    code_template = env.get_template("raw_get_set_state.jinja").render(fields=fields)
    return code_template


DEFAULTS_FRAGMENT = """
def _set_defaults(self):
    result = self
    {{item|indent(4)}}
    return super()._set_defaults()
""".strip()

if sys.version_info >= (3, 11):
    DEFAULTS_FRAGMENT = """
def make_defaults():
    # ARJ: This is necessary to make the function have a replaceable class
    # cell via free vars.
    __class__ = None

    def _set_defaults(self):
        result = self
        {{item|indent(8)}}
        return super()._set_defaults()
    return _set_defaults

_set_defaults = make_defaults()

""".strip()


def make_defaults(fields, defaults_var_template):
    defaults_var_template = env.from_string(defaults_var_template).render(fields=fields)
    code = env.from_string(DEFAULTS_FRAGMENT).render(item=defaults_var_template)
    return code


def _order_by_mro_position(parent_cls: Type) -> Callable[[Type], int]:
    def key_func(item: Type) -> int:
        return item.__mro__.index(parent_cls)

    return key_func


if _SUPPORTED_CELLTYPE:

    def make_class_cell():
        return CellType(None)


else:

    def make_class_cell() -> CellType:
        """
        Create a CellType reference through a throwaway closure, suitable
        for replacing in a function's __closure__ definition.
        """

        def closure_maker():
            __class__ = type

            def bar():
                return __class__

            return bar

        fake_function = closure_maker()
        class_cell, = fake_function.__closure__
        del fake_function
        return class_cell


KLASS_CLOSURE_BINDING_WRONG = "We should've moved this out of load_from_scope_names and into free_binding_closure_names as an atomic operation!"  # noqa
NOT_SET = object()


def find_class_in_cell(classes: Iterable[Type], cell: CellType) -> Optional[Type]:
    if not classes:
        return None
    for cls in classes:
        if class_in_cell(cls, cell):
            return cls
    return None


def find_class_in_value(classes: Iterable[Type], value: Any) -> Optional[Type]:
    if not classes:
        return None
    for cls in classes:
        if cls is value:
            return cls
    return None


def class_in_cell(cls: Type, cell: CellType) -> bool:
    value: Any = cell.cell_contents
    return cls is value


CODE_BITFLAGS = {name: getattr(inspect, name) for name in dir(inspect) if name.startswith("CO_")}


def _sanitize_flags(flags):
    newval = 0
    for name, flag in CODE_BITFLAGS.items():
        if flag & flags:
            newval |= flag
    return newval


def replace_class_references(
    function: Callable[[Any], Any], *references: Tuple[Type, Type], return_classmethod=False
):
    """
    Given a vector of (generic_class, specialized_class), replace any LOAD_GLOBAL or __closure__
    references to generic_class with specialized_class.
    """
    if function is None:
        return None
    if not references:
        return function

    dest_func_name = function.__name__
    is_classmethod = hasattr(function, "__func__") and hasattr(function, "__self__")
    if is_classmethod:
        classmethod_owner = function.__self__
        function = function.__func__
        class_owner_descendents = tuple(
            sorted(
                frozenset(after for _, after in references if issubclass(after, classmethod_owner)),
                key=_order_by_mro_position(classmethod_owner),
            )
        )
        if not class_owner_descendents or class_owner_descendents[0] is classmethod_owner:
            classmethod_dest = classmethod_owner
            dest_func_name = f"{dest_func_name}_{hash(tuple(after for _, after in references))}"
        else:
            classmethod_dest = class_owner_descendents[0]

    code = function.__code__
    function_globals: Mapping[str, Any] = function.__globals__

    # If our class reference is in here, it will load
    # from the code's namespace. We will need to intercept it
    # and move it to a closure
    load_from_scope_names: List[str] = list(code.co_names)
    # If our class refer is in here, it will load from a closure (and reference
    # the value in __closure__ at the index of the co_freevars tuple name)
    free_binding_closure_names: List[str] = list(code.co_freevars)

    if function.__closure__ is None:
        current_closures: List[CellType] = []
    else:
        current_closures: List[CellType] = list(function.__closure__)

    changed = False
    old_klass_refs = {old: new for old, new in references}
    old_klass_names = {old.__name__: old for old in old_klass_refs}

    for index, cell in enumerate(current_closures):
        closure_name: str = free_binding_closure_names[index]
        oldklass: Optional[Type] = None
        if closure_name in old_klass_names:
            oldklass = old_klass_names[closure_name]
        else:
            oldklass = find_class_in_cell(old_klass_refs.keys(), cell)
        if oldklass is None:
            continue
        newklass = old_klass_refs[oldklass]
        # okay, we'll need to spawn a new class cell and rebind
        # the closure
        class_cell = make_class_cell()
        class_cell.cell_contents = newklass
        # Replace the reference of the old class to the new one:
        current_closures[index] = class_cell
        changed = True

    for index, global_varname in enumerate(load_from_scope_names):
        oldklass = None
        if global_varname in old_klass_names:
            oldklass = old_klass_names[global_varname]
        else:
            try:
                global_varvalue = function_globals[global_varname]
            except KeyError:
                continue
            oldklass = find_class_in_value(old_klass_refs.keys(), global_varvalue)
        if oldklass is None:
            continue
        newklass = old_klass_refs[oldklass]
        # In this case, we need to change the global load name
        # to the specialized one and ensure the clobbered name is in global()
        # scope for the function
        # Warning: Creates strong reference.
        # TODO: Bytecode rewrite to change from `expr(oldklass)` to `expr((oldklass - fields))`.
        new_name = f"{oldklass.__name__}->{hash(newklass)}"
        function_globals[new_name] = newklass
        load_from_scope_names[index] = new_name
        changed = True

    if not changed:
        if is_classmethod and classmethod_dest is not classmethod_owner:
            return getattr(classmethod_dest, function.__name__)
        return function
    args = (
        code.co_argcount,
        # co_posonlyargcount (3.8+)
        code.co_kwonlyargcount,
        code.co_nlocals,
        code.co_stacksize,
        _sanitize_flags(code.co_flags),
        code.co_code,
        code.co_consts,
        tuple(load_from_scope_names),
        code.co_varnames,
        code.co_filename,
        code.co_name,
        # qualname (3.10+)
        code.co_firstlineno,
        code.co_lnotab,
        # exception table (3.10+)
        tuple(free_binding_closure_names),
        code.co_cellvars,
    )
    if hasattr(CodeType, "co_posonlyargcount"):
        # Python3.8 with PEP570
        args = (*args[:1], code.co_posonlyargcount, *args[1:])
    if hasattr(CodeType, "co_qualname"):
        args = (*args[:12], code.co_qualname, *args[12:])
    if hasattr(CodeType, "co_exceptiontable"):
        args = (*args[:15], code.co_exceptiontable, *args[15:])
    code = CodeType(*args)

    # Resynthesize the errant __class__ cell with the correct one in the CORRECT position
    # This will allow for overridden functions to be called with super()
    new_function = FunctionType(
        code, function_globals, function.__name__, function.__defaults__, tuple(current_closures)
    )
    new_function.__kwdefaults__ = function.__kwdefaults__
    new_function.__annotations__ = function.__annotations__
    if is_classmethod:
        if return_classmethod:
            return classmethod(new_function)
        # Assign the classmethod then return its wrapped form:
        setattr(classmethod_dest, dest_func_name, classmethod(new_function))
        wrapped = getattr(classmethod_dest, dest_func_name)
        return wrapped
    return new_function


def insert_class_closure(
    klass: Atomic, function: Optional[Callable[..., Any]]
) -> Optional[Callable[..., Any]]:
    """
    an implicit super() works by looking at __class__ to fill in the
    arguments, becoming super(__class__, self)

    Since we're messing with the function space, __class__ is most
    likely undefined or pointing to the incorrect specialized class
    instead of the base/public class.
    """
    if function is None:
        return None

    code: CodeType = function.__code__
    # Make the cell to hold the replacement klass value:
    class_cell: CellType = make_class_cell()
    class_cell.cell_contents = klass

    closure_var_names: List[str] = list(code.co_freevars)

    current_closure: List[CellType]
    if function.__closure__ is None:
        current_closure = []
    else:
        current_closure = list(function.__closure__)

    # Insert the class cell into the closure references:
    if "__class__" not in code.co_freevars:
        if sys.version_info >= (3, 12):
            if any(tainted in target for target in (code.co_names,) for tainted in ("super",)):
                raise SyntaxError(f"restructure {function} to be in a closure!")
            return function
        closure_var_names.append("__class__")
        current_closure.append(class_cell)
    else:
        index = closure_var_names.index("__class__")
        current_closure[index] = class_cell

    # recreate the function using its guts
    args = (
        code.co_argcount,
        # co_posonlyargcount (3.8+)
        code.co_kwonlyargcount,
        code.co_nlocals,
        code.co_stacksize,
        _sanitize_flags(code.co_flags),
        code.co_code,
        code.co_consts,
        code.co_names,
        code.co_varnames,
        code.co_filename,
        code.co_name,
        # qualname (3.10+)
        code.co_firstlineno,
        code.co_lnotab,
        # exception table (3.10+)
        tuple(closure_var_names),
        code.co_cellvars,
    )
    if hasattr(CodeType, "co_posonlyargcount"):
        # Python3.8 with PEP570
        args = (*args[:1], code.co_posonlyargcount, *args[1:])
    if hasattr(CodeType, "co_qualname"):
        args = (*args[:12], code.co_qualname, *args[12:])
    if hasattr(CodeType, "co_exceptiontable"):
        args = (*args[:15], code.co_exceptiontable, *args[15:])
    code = CodeType(*args)
    new_function = FunctionType(
        code, function.__globals__, function.__name__, function.__defaults__, tuple(current_closure)
    )
    # Copy the module name:
    if function.__module__:
        new_function.__module__ = function.__module__
    new_function.__kwdefaults__ = function.__kwdefaults__
    new_function.__annotations__ = function.__annotations__
    return new_function


def explode(*args, **kwargs):
    raise TypeError("This shouldn't happen!")


def _dedupe(iterable):
    seen = set()
    for item in iterable:
        if item not in seen:
            seen.add(item)
            yield item


class Flags(IntEnum):
    UNCONSTRUCTED = 0
    IN_CONSTRUCTOR = 1
    DEFAULTS_SET = 2
    INITIALIZED = 4
    DISABLE_HISTORY = 8
    UNPICKLING = 16


def gather_listeners(class_name, attrs, class_columns, combined_class_columns, inherited_listeners):
    listeners = {}
    post_coerce_failure_handlers = {}

    lost_listeners = []
    invalid_on_error_funcs = []

    for key, value in attrs.items():
        if callable(value):
            if hasattr(value, "_event_listener_funcs"):
                for field in value._event_listener_funcs:
                    if field not in class_columns and field in inherited_listeners:
                        lost_listeners.append(field)
                        continue
                    try:
                        listeners[field].append(key)
                    except KeyError:
                        listeners[field] = [key]
            if hasattr(value, "_post_coerce_failure_funcs"):
                for field in value._post_coerce_failure_funcs:
                    if field not in combined_class_columns:
                        invalid_on_error_funcs.append(field)
                        continue
                    try:
                        post_coerce_failure_handlers[field].append(key)
                    except KeyError:
                        post_coerce_failure_handlers[field] = [key]
    if lost_listeners:
        if len(lost_listeners) == 1:
            lost_listeners_friendly = lost_listeners[0]
        else:
            lost_listeners_friendly = f"{', '.join(lost_listeners[:-1])} and {lost_listeners[-1]}"
        raise OrphanedListenersError(
            "Unable to attach listeners to the following fields without redefining them in "
            f"__slots__ for {class_name}: {lost_listeners_friendly}"
        )

    if invalid_on_error_funcs:
        if len(invalid_on_error_funcs) == 1:
            invalid_on_error_funcs_friendly = invalid_on_error_funcs[0]
        else:
            invalid_on_error_funcs_friendly = (
                f"{', '.join(invalid_on_error_funcs[:-1])} and {invalid_on_error_funcs[-1]}"
            )
        raise InvalidPostCoerceAttributeNames(
            "Unable to attach a post-coerce failure function to missing attributes "
            f"for {class_name}: {invalid_on_error_funcs_friendly}"
        )
    return listeners, post_coerce_failure_handlers


def is_debug_mode(mode=None, class_name=None, field=None) -> bool:
    if os.environ.get("INSTRUCT_DEBUG", "").lower() in AFFIRMATIVE:
        return True
    mode_debug: str = os.environ.get(f"INSTRUCT_DEBUG_{mode.upper()}", "").lower()
    if mode_debug in AFFIRMATIVE:
        return True
    if field is None:
        field = "*"
    if class_name is None:
        return False
    if "." in mode_debug:
        debug_class_name, debug_field = mode_debug.split(".")
    else:
        debug_class_name = mode_debug
        debug_field = "*"
    if class_name == debug_class_name:
        if field == debug_field or debug_field == "*":
            return True
    return False


def create_proxy_property(
    env: Environment,
    class_name: str,
    key: str,
    value: Union[Type, Tuple[Type, ...], Dict[str, Type]],
    isinstance_compatible_coerce_type: Optional[Union[Tuple[Type, ...]], Type],
    coerce_func: Optional[Callable],
    derived_type: Optional[Type],
    listener_funcs: Optional[Tuple[Callable, ...]],
    coerce_failure_funcs: Optional[Tuple[Callable, ...]],
    local_getter_var_template: str,
    local_setter_var_template: str,
    *,
    fast: bool,
) -> Tuple[property, Type, Type]:
    ns_globals = {"NoneType": NoneType, "Flags": Flags, "typing": typing}
    setter_template = env.get_template("setter.jinja")
    getter_template = env.get_template("getter.jinja")

    ns = {"make_getter": explode, "make_setter": explode}
    getter_code = getter_template.render(
        field_name=key, get_variable_template=local_getter_var_template
    )
    setter_code = setter_template.render(
        field_name=key,
        setter_variable_template=local_setter_var_template,
        on_sets=listener_funcs,
        post_coerce_failure_handlers=coerce_failure_funcs,
        has_coercion=isinstance_compatible_coerce_type is not None,
    )
    filename = "<getter-setter>"
    if is_debug_mode("codegen", class_name, key):
        with tempfile.NamedTemporaryFile(
            delete=False, mode="w", prefix=f"{class_name}-{key}", suffix=".py", encoding="utf8"
        ) as fh:
            fh.write(getter_code)
            fh.write("\n")
            fh.write(setter_code)
            filename = fh.name
            logger.debug(f"{class_name}.{key} at {filename}")

    code = compile("{}\n{}".format(getter_code, setter_code), filename, mode="exec")
    exec(code, ns_globals, ns)

    isinstance_compatible_types = parse_typedef(value)
    new_property = property(
        ns["make_getter"](value),
        ns["make_setter"](
            value,
            fast,
            derived_type,
            isinstance_compatible_types,
            isinstance_compatible_coerce_type,
            coerce_func,
        ),
    )
    return new_property, isinstance_compatible_types


EMPTY_FROZEN_SET = frozenset()
EMPTY_MAPPING = FrozenMapping({})


def __no_op_skip_get__(self):
    return


def __no_op_skip_set__(self, value):
    return


def unpack_coerce_mappings(mappings):
    """
    Transform:
    {
        "foo": (str, lambda val: item.encode("utf8")),
        ("bar", "baz"): ((int, float), lambda val: f"{val}")
    }
    to
    {
        "foo": (str, lambda val: item.encode("utf8")),
        "bar": ((int, float), lambda val: f"{val}"),
        "baz": ((int, float), lambda val: f"{val}")
    }
    """
    for key in mappings.keys():
        if not isinstance(key, (str, tuple)):
            raise CoerceMappingValueError(
                f"Coerce mapping keys must either be a string or tuple of strings (Got {key!r})"
            )
        if isinstance(key, tuple) and not all(isinstance(prop_name, str) for prop_name in key):
            raise CoerceMappingValueError(
                f"Coerce mapping keys must either be a string or tuple of strings (Got {key!r})"
            )
        value = mappings[key]
        if not isinstance(value, tuple) or len(value) != 2:
            raise CoerceMappingValueError(
                f"Coerce mapping key {key} must be Tuple[Union[Type, Tuple[Type, ...]], Callable[[T], U]], not {value!r}"
            )
        if isinstance(key, tuple):
            for prop_name in key:
                yield prop_name, value
        else:
            yield key, value


def transform_typing_to_coerce(
    type_hints: T, class_mapping: Mapping[Type, Type]
) -> Tuple[T, Callable[[Any], Any]]:
    """
    Use for consuming the prior slotted trace and returning a tuple
    suitable for Union[coerce_type, current_coerce_types] with a callable function.
    """
    if isinstance(type_hints, tuple):
        assert all(is_typing_definition(item) or isinstance(item, type) for item in type_hints)
        type_hints = Union[type_hints]
    assert is_typing_definition(type_hints) or isinstance(type_hints, type)

    return type_hints, wrapper_for_type(type_hints, class_mapping, Atomic)


class ModifiedSkipTypes(NamedTuple):
    replacement_type_definition: Atomic
    replacement_coerce_definition: Optional[Tuple[Any, Callable]]
    mutant_classes: FrozenSet[Tuple[Atomic, Atomic]]


def create_union_coerce_function(
    prior_complex_type_path: T,
    complex_type_cast: Callable,
    custom_cast_types: Optional[T],
    custom_cast_function: Optional[Callable],
):
    if custom_cast_types is None:
        complex_type_cast.__only_parent_cast__ = True
        return prior_complex_type_path, complex_type_cast

    cast_type_cls = parse_typedef(prior_complex_type_path)

    def cast_values(value):
        if isinstance(value, cast_type_cls):
            # The current value is already the parent type, so apply a down coerce
            # The function is probably not ready for encountering the parent type
            # as normal use would be a no-op.
            return complex_type_cast(value)
        value = custom_cast_function(value)
        # Did the original coerce function make a parent type?
        if isinstance(value, cast_type_cls):
            # Yes, so let's down down-coerce it to the end type:
            return complex_type_cast(value)
        return value

    cast_values.__union_subtypes__ = (custom_cast_types, custom_cast_function)
    if isinstance(custom_cast_types, tuple):
        return Union[(prior_complex_type_path,) + custom_cast_types], cast_values
    return Union[prior_complex_type_path, custom_cast_types], cast_values


def apply_skip_keys(
    skip_key_fields: Union[FrozenSet[str], Set[str], Dict[str, Any]],
    current_definition: Atomic,
    current_coerce: Optional[Tuple[Any, Callable[[Any], Any]]],
) -> ModifiedSkipTypes:
    """
    If the current definition is Atomic, then Atomic - fields should be compatible with Atomic.

    So we will cast the base class to it's child class as the child should be compatible.

    Current issues:
        - How do we unpack a Tuple[Union[Atomic1, Atomic2], ...] and transform to
            Tuple[Union[Atomic1 - skip_fields, Atomic2 - skip_fields]] ?
        - How do we handle Dict[str, Atomic1] -> Dict[str, Atomic1 - skip_fields] ?

    Basically this has to traverse the graph, branching out and replacing nodes.
    """

    if current_coerce is not None:
        current_coerce_types, current_coerce_cast_function = current_coerce
        # Unpack to the original cast type, coerce function (in case we're subtracting a subtraction)

        if hasattr(current_coerce_cast_function, "__only_parent_cast__"):
            # If this is only for casting a parent typecls function, kill it.
            current_coerce = None
        else:
            while hasattr(current_coerce_cast_function, "__union_subtypes__"):
                current_coerce_types, current_coerce_cast_function = (
                    current_coerce_cast_function.__union_subtypes__
                )
            current_coerce = (current_coerce_types, current_coerce_cast_function)
            del current_coerce_types, current_coerce_cast_function

    if (
        isinstance(current_definition, type)
        and ismetasubclass(current_definition, Atomic)
        or is_typing_definition(current_definition)
        or isinstance(current_definition, tuple)
    ):
        new_coerce_definition = None
        original_definition = current_definition
        gen = find_class_in_definition(current_definition, Atomic, metaclass=True)
        replace_class_refs = []
        try:
            result = None
            while True:
                result = gen.send(result)
                before = result
                result = result - skip_key_fields
                after = result
                if before is not after:
                    replace_class_refs.append((before, after))
        except StopIteration as e:
            current_definition = e.value

        if replace_class_refs:
            # Coerce functions may produce the parent type.
            # So what we'll do is a two pass function
            #   - one pass that just downcoerces functions that are the
            #     final parent type
            #   - second pass after the original coerce that *will* produce the
            #     parent type.
            parent_type_path, parent_type_coerce_function = transform_typing_to_coerce(
                original_definition, dict(replace_class_refs)
            )
            new_coerce_definition = create_union_coerce_function(
                parent_type_path,
                parent_type_coerce_function,
                current_coerce[0] if current_coerce else None,
                current_coerce[1] if current_coerce else None,
            )
        return ModifiedSkipTypes(
            current_definition,
            new_coerce_definition or current_coerce,
            frozenset(replace_class_refs),
        )
    else:
        return None, None, EMPTY_FROZEN_SET


def list_callables(cls):
    for key in dir(cls):
        value = getattr(cls, key)
        if isinstance(value, type):
            continue
        elif not callable(value):
            continue
        yield key, value


def find_users_of(mutant_class_parent_names, in_cls):
    ignore_functions = frozenset()
    for parent_cls in in_cls.__bases__:
        ignore_functions |= frozenset(
            value
            for key, value in list_callables(parent_cls)
            if not (key.startswith("__") and key.endswith("__"))
        )
    functions_to_scan = (
        (key, value) for key, value in list_callables(in_cls) if not key.startswith("__")
    )
    for key, value in functions_to_scan:
        external_names = frozenset(value.__code__.co_names) | frozenset(value.__code__.co_freevars)
        matches = external_names & mutant_class_parent_names
        if matches:
            yield (key, value), matches


def is_defined_coerce(cls, key):
    for cls_item in inspect.getmro(cls):
        coerce_mappings = getattr(cls_item, "__coerce__", None)
        if coerce_mappings is not None:
            if key in coerce_mappings:
                return coerce_mappings[key]
    return None


class Atomic(type):
    __slots__ = ()
    REGISTRY = ReadOnly(set())
    MIXINS = ReadOnly({})
    SKIPPED_FIELDS: Mapping[FrozenSet[str], Atomic] = WeakValueDictionary()

    if TYPE_CHECKING:
        _data_class: Atomic
        _columns: Mapping[str, Any]
        _column_types: Mapping[str, Union[Type, Tuple[Type, ...]]]
        _all_coercions: Mapping[str, Tuple[Union[Type, Tuple[Type, ...]], Callable]]
        _support_columns: Tuple[str, ...]
        _properties: typing.collections.KeysView[str]
        _configuration: AttrsDict
        _all_accessible_fields: typing.collections.KeysView[str]
        # i.e. key -> List[Union[AtomicDerived, bool]] means key can hold an Atomic derived type.
        _nested_atomic_collection_keys: Mapping[str, Tuple[Atomic, ...]]

    def __public_class__(self):
        """
        Most of the time, we want to return the support class (the public facing one).

        However, there are cases where a subclass changes the response of certain functions
        and it is not desirable to return it for other code.
        """
        return getattr(self, "_parent", self)

    @classmethod
    def register_mixin(cls, name, klass):
        cls.MIXINS[name] = klass

    def __init__(self, *args, **kwargs):
        # We use kwargs to pass to __new__ and therefore we need
        # to filter it out of the `type(...)` call
        super().__init__(*args)

    def __iter__(self):
        yield from self._columns.keys()

    def __and__(
        self: Atomic,
        include_fields: Union[Set[str], List[str], Tuple[str], FrozenSet[str], str, Dict[str, Any]],
    ) -> Atomic:
        assert isinstance(include_fields, (list, frozenset, set, tuple, dict, str, FrozenMapping))
        include_fields: FrozenMapping = flatten_fields.collect(include_fields)
        include_fields -= self._skipped_fields
        if not include_fields:
            return self
        skip_fields = (
            FrozenMapping(show_all_fields(self, deep_traverse_on=include_fields)) - include_fields
        )
        return self - skip_fields

    def __sub__(self: Atomic, skip_fields: Union[Mapping[str, Any], Iterable[Any]]) -> Atomic:
        assert isinstance(skip_fields, (list, frozenset, set, tuple, dict, str, FrozenMapping))
        debug_mode = is_debug_mode("skip")

        root_class = type(self)
        cls = public_class(self)

        if not skip_fields:
            return self

        if isinstance(skip_fields, str):
            skip_fields = frozenset((skip_fields,))

        skip_fields: FrozenMapping = flatten_fields.collect(skip_fields)
        unrecognized_keys = frozenset(skip_fields) - self._columns.keys()
        skip_fields -= unrecognized_keys

        currently_skipped_fields = FrozenMapping(self._skipped_fields)
        effective_skipped_fields: FrozenMapping = skip_fields | currently_skipped_fields
        if not effective_skipped_fields:
            return self

        try:
            value = root_class.SKIPPED_FIELDS[(cls.__qualname__, effective_skipped_fields)]
        except KeyError:
            # print(f"Cache miss for {self.__qualname__}")
            pass
        else:
            # print(f"Cache hit for {self.__qualname__}")
            return value
        skip_fields = effective_skipped_fields

        redefinitions = None
        redefine_coerce = None

        skip_entire_keys = set()

        redefinitions = {}
        redefine_coerce = {}
        mutant_classes = set()
        for key, key_specific_strip_keys in skip_fields.items():
            if not key_specific_strip_keys:
                skip_entire_keys.add(key)
                continue

            if isinstance(key_specific_strip_keys, str):
                key_specific_strip_keys = frozenset((key_specific_strip_keys,))

            current_definition = self._slots[key]
            current_coerce = is_defined_coerce(self, key)
            redefined_definition, redefined_coerce_definition, new_mutants = apply_skip_keys(
                key_specific_strip_keys, current_definition, current_coerce
            )
            mutant_classes |= new_mutants

            if redefined_definition is not None:
                redefinitions[key] = redefined_definition
            if redefined_coerce_definition is not None:
                redefine_coerce[key] = redefined_coerce_definition

        mutant_class_parent_names = {
            parent.__name__: (parent, child) for parent, child in mutant_classes
        }
        if debug_mode:
            logger.debug(f"Mutants: {mutant_class_parent_names}")

        attrs = {"__slots__": ()}

        for (function_name, function_value), parents_to_replace in find_users_of(
            mutant_class_parent_names.keys(), cls
        ):
            mutated_function_value = replace_class_references(
                function_value,
                return_classmethod=True,
                *[mutant_class_parent_names[parent_name] for parent_name in parents_to_replace],
            )
            if debug_mode:
                logger.debug(f"{function_name} has {parents_to_replace}")
            attrs[function_name] = mutated_function_value

        skip_entire_keys = FrozenMapping(skip_entire_keys)

        if redefinitions:
            attrs["__slots__"] = redefinitions
            attrs["_modified_fields"] = tuple(redefinitions)
        if redefine_coerce:
            attrs["__coerce__"] = redefine_coerce

        changes = ""
        if skip_entire_keys:
            changes = "Without{}".format("And".join(key.capitalize() for key in skip_entire_keys))
        if redefinitions:
            changes = "{}ButModified{}".format(
                changes, "And".join(sorted(key.capitalize() for key in redefinitions))
            )
        if not changes:
            return self
        value = type(f"{cls.__name__}{changes}", (cls,), attrs, skip_fields=skip_entire_keys)
        root_class.SKIPPED_FIELDS[(cls.__qualname__, effective_skipped_fields)] = value
        return value

    def __new__(
        klass,
        class_name,
        bases,
        attrs,
        *,
        fast=None,
        concrete_class=False,
        skip_fields=FrozenMapping(),
        include_fields=FrozenMapping(),
        **mixins,
    ):
        if concrete_class:
            cls = super().__new__(klass, class_name, bases, attrs)
            if not getattr(cls, "__hash__", None):
                cls.__hash__ = object.__hash__
            assert cls.__hash__ is not None
            return cls
        assert isinstance(
            skip_fields, FrozenMapping
        ), f"Expect skip_fields to be a FrozenMapping, not a {type(skip_fields).__name__}"
        assert isinstance(
            include_fields, FrozenMapping
        ), f"Expect include_fields to be a FrozenMapping, not a {type(include_fields).__name__}"
        if include_fields and skip_fields:
            raise TypeError("Cannot specify both include_fields and skip_fields!")
        data_class_attrs = {}
        base_class_functions = []
        # Move overrides to the data class,
        # so we call them first, then the codegen pieces.
        # Suitable for a single level override.
        # _set_defaults, __eq__ is special as it calls up the inheritance tree
        # Others do not.
        for key in (
            "__iter__",
            "__getstate__",
            "__setstate__",
            "__eq__",
            "__getitem__",
            "__setitem__",
        ):
            if key in attrs:
                if hasattr(attrs[key], "_instruct_base_cls"):
                    base_class_functions.append(key)
                    continue
                data_class_attrs[key] = attrs.pop(key)
        base_class_functions = tuple(base_class_functions)
        support_cls_attrs = attrs
        del attrs

        if "__slots__" not in support_cls_attrs and "__annotations__" in support_cls_attrs:
            module = import_module(support_cls_attrs["__module__"])
            kwargs = {}
            if _GET_TYPEHINTS_ALLOWS_EXTRA:
                kwargs["include_extras"] = True
            hints = get_type_hints(
                SimpleNamespace(**support_cls_attrs),
                support_cls_attrs,
                # First look in the module, then failsafe to the typing to support
                # unimported 'Optional', et al
                ChainMap(module.__dict__, typing.__dict__),
                **kwargs,
            )
            support_cls_attrs["__slots__"] = hints

        if "__slots__" not in support_cls_attrs:
            # Infer a support class w/o __annotations__ or __slots__ as being an implicit
            # mixin class.
            support_cls_attrs["__slots__"] = FrozenMapping()

        coerce_mappings: Optional[CoerceMapping] = None
        if "__coerce__" in support_cls_attrs:
            if support_cls_attrs["__coerce__"] is not None:
                coerce_mappings: AbstractMapping = support_cls_attrs["__coerce__"]
                if isinstance(coerce_mappings, ReadOnly):
                    # Unwrap
                    coerce_mappings = coerce_mappings.value
        else:
            support_cls_attrs["__coerce__"] = None

        if coerce_mappings is not None:
            if not isinstance(coerce_mappings, AbstractMapping):
                raise TypeError(
                    f"{class_name} expects `__coerce__` to implement an AbstractMapping or None, "
                    f"not a {type(coerce_mappings)}"
                )
            coerce_mappings = dict(unpack_coerce_mappings(coerce_mappings))
            if not isinstance(support_cls_attrs["__coerce__"], ReadOnly):
                support_cls_attrs["__coerce__"] = ReadOnly(coerce_mappings)
        coerce_mappings = cast(CoerceMapping, coerce_mappings)

        # A support column is a __slot__ element that is unmanaged.
        support_columns = []
        if isinstance(support_cls_attrs["__slots__"], tuple):
            # Classes with tuples in them are assumed to be
            # data class definitions (i.e. supporting things like a change log)
            support_columns.extend(support_cls_attrs["__slots__"])
            support_cls_attrs["__slots__"] = FrozenMapping()

        if not isinstance(support_cls_attrs["__slots__"], (tuple, AbstractMapping)):
            raise TypeError(
                f"The __slots__ definition for {class_name} must be a mapping or empty tuple!"
            )

        if "fast" in support_cls_attrs:
            fast = support_cls_attrs.pop("fast")
        if fast is None:
            fast = not __debug__

        combined_columns = {}
        combined_slots = {}
        nested_atomic_collections: Dict[str, Atomic] = {}
        # Mapping of public name -> custom type vector for `isinstance(...)` checks!
        column_types: Dict[str, Union[Type, Tuple[Type, ...]]] = {}

        for mixin_name in mixins:
            if mixins[mixin_name]:
                mixin_cls = klass.MIXINS[mixin_name]
                if isinstance(mixins[mixin_name], type):
                    mixin_cls = mixins[mixin_name]
                bases = (mixin_cls,) + bases

        # Setup wrappers are nested
        # pieces of code that effectively surround a part that sets
        #    self._{key} -> value
        # They must be reindented properly
        setter_wrapper = []
        getter_templates = []
        setter_templates = []
        defaults_templates = []

        if "__setter_template__" in support_cls_attrs:
            setter_templates.append(support_cls_attrs["__setter_template__"])
        if "__getter_template__" in support_cls_attrs:
            getter_templates.append(support_cls_attrs["__getter_template__"])
        if "__defaults__init__template__" in support_cls_attrs:
            defaults_templates.append(support_cls_attrs["__defaults__init__template__"])

        # collection of all the known public properties for this class and it's parents:
        properties = [name for name, val in support_cls_attrs.items() if isinstance(val, property)]

        pending_extra_slots = []
        if "__extra_slots__" in support_cls_attrs:
            pending_extra_slots.extend(support_cls_attrs["__extra_slots__"])
        # Base class inherited items:
        annotated_metadata = {}
        inherited_listeners = {}
        for cls in bases:
            skipped_properties = ()
            if (
                hasattr(cls, "__slots__")
                and cls.__slots__ != ()
                and not ismetasubclass(cls, Atomic)
            ):
                # Because we cannot control the circumstances of a base class's construction
                # and it has __slots__, which will destroy our multiple inheritance support,
                # so we should just refuse to work.
                #
                # Please note that ``__slots__ = ()`` classes work perfectly and are not
                # subject to this limitation.
                raise TypeError(
                    f"Multi-slot classes (like {cls.__name__}) must be defined "
                    "with `metaclass=Atomic`. Mixins with empty __slots__ are not subject to "
                    "this restriction."
                )
            if hasattr(cls, "_listener_funcs"):
                for key, value in cls._listener_funcs.items():
                    if key in inherited_listeners:
                        inherited_listeners[key].extend(value)
                    else:
                        inherited_listeners[key] = value
            if hasattr(cls, "__extra_slots__"):
                support_columns.extend(list(cls.__extra_slots__))

            if ismetasubclass(cls, Atomic):
                # Only Atomic Descendants will merge in the helpers of
                # _columns: Dict[str, Type]
                if cls._annotated_metadata:
                    annotated_metadata.update(cls._annotated_metadata)
                if cls._column_types:
                    column_types.update(cls._column_types)
                if cls._nested_atomic_collection_keys:
                    for key, value in cls._nested_atomic_collection_keys.items():
                        # Override of this collection definition, so don't inherit!
                        if key in combined_columns:
                            continue
                        nested_atomic_collections[key] = value

                if cls._columns:
                    combined_columns.update(cls._columns)
                if cls._slots:
                    combined_slots.update(cls._slots)
                if cls._support_columns:
                    support_columns.extend(cls._support_columns)
                skipped_properties = cls._no_op_properties

                if hasattr(cls, "setter_wrapper"):
                    setter_wrapper.append(cls.setter_wrapper)
                if hasattr(cls, "__getter_template__"):
                    getter_templates.append(cls.__getter_template__)
                if hasattr(cls, "__setter_template__"):
                    setter_templates.append(cls.__setter_template__)
                if hasattr(cls, "__defaults__init__template__"):
                    defaults_templates.append(cls.__defaults__init__template__)
            # Collect all publicly accessible properties:
            for key in dir(cls):
                value = getattr(cls, key)
                if isinstance(value, property):
                    if key in skipped_properties:
                        continue
                    if (
                        key.startswith("_")
                        and key.endswith("_")
                        and key[1:-1] in skipped_properties
                    ):
                        continue
                    properties.append(key)

        # Okay, now parse the current class types and then merge with
        # the overall combined blob!
        derived_classes = {}
        current_class_columns = {}
        current_class_slots = {}
        for key, value in support_cls_attrs["__slots__"].items():
            if isinstance(value, dict):
                value = type("{}".format(key.capitalize()), bases, {"__slots__": value})
                derived_classes[key] = value
            if not ismetasubclass(value, Atomic):
                nested_atomics = tuple(find_class_in_definition(value, Atomic, metaclass=True))
                if nested_atomics:
                    nested_atomic_collections[key] = nested_atomics
                del nested_atomics
            current_class_slots[key] = combined_slots[key] = value
            current_class_columns[key] = combined_columns[key] = parse_typedef(value)

        no_op_skip_keys = []
        if skip_fields:
            for key in tuple(combined_columns.keys()):
                if key not in skip_fields:
                    continue
                no_op_skip_keys.append(key)
                del combined_columns[key]
                del combined_slots[key]
                if key in annotated_metadata:
                    del annotated_metadata[key]

            for key in tuple(current_class_columns.keys()):
                if key not in skip_fields:
                    continue
                no_op_skip_keys.append(key)
                del current_class_slots[key]
                del current_class_columns[key]
        elif include_fields:
            for key in tuple(combined_columns.keys()):
                if key in include_fields:
                    continue
                no_op_skip_keys.append(key)
                del combined_columns[key]
                del combined_slots[key]
                if key in annotated_metadata:
                    del annotated_metadata[key]

            for key in tuple(current_class_columns.keys()):
                if key in include_fields:
                    continue
                no_op_skip_keys.append(key)
                del current_class_slots[key]
                del current_class_columns[key]

        # Gather listeners:
        listeners, post_coerce_failure_handlers = gather_listeners(
            class_name,
            support_cls_attrs,
            current_class_columns,
            combined_columns,
            inherited_listeners,
        )

        if combined_columns:
            try:
                defaults_var_template = defaults_templates[0]
            except IndexError:
                raise MissingGetterSetterTemplateError(
                    "You must define __defaults__init__template__!"
                )
            try:
                setter_var_template = setter_templates[0]
                getter_var_template = getter_templates[0]
            except IndexError:
                raise MissingGetterSetterTemplateError(
                    "You must define both __getter_template__ and __setter_template__"
                )
            else:
                local_setter_var_template = setter_var_template.format(key="{{field_name}}")
                local_getter_var_template = getter_var_template.format(key="{{field_name}}")
                del setter_var_template
                del getter_var_template
            for index, template_name in enumerate(setter_wrapper):
                template = env.get_template(template_name)
                local_setter_var_template = template.render(
                    field_name="{{field_name}}", setter_variable_template=local_setter_var_template
                )
            local_setter_var_template = local_setter_var_template.replace(
                "{{field_name}}", "%(key)s"
            )
            local_getter_var_template = local_getter_var_template.replace(
                "{{field_name}}", "%(key)s"
            )
        current_class_fields = []
        all_coercions = {}
        # the `__class__` field of the generated functions will be incomplete,
        # so track them so we can replace them with a derived type made ``__class__``
        class_cell_fixups = []
        for key, raw_typedef in tuple(current_class_slots.items()):
            disabled_derived = None
            if raw_typedef in klass.REGISTRY:
                disabled_derived = False
                derived_classes[key] = raw_typedef
            current_class_fields.append(key)
            coerce_types, coerce_func = None, None
            if coerce_mappings and key in coerce_mappings:
                coerce_types, coerce_func = coerce_mappings[key]
                if (
                    isinstance(coerce_types, type)
                    and coerce_types is dict
                    or isinstance(coerce_types, tuple)
                    and dict in coerce_types
                ):
                    disabled_derived = True
                coerce_types = parse_typedef(coerce_types)
                all_coercions[key] = (coerce_types, coerce_func)
            derived_class = derived_classes.get(key)
            if disabled_derived and derived_class is not None:
                if is_debug_mode("derived"):
                    logger.debug(
                        f"Disabling derived for {key} on {class_name}, failsafe to __coerce__[{coerce_types}]"
                    )
                derived_class = None
            if get_origin(raw_typedef) is Annotated:
                _, *metadata = get_args(raw_typedef)
                annotated_metadata[key] = tuple(metadata)
            new_property, isinstance_compatible_types = create_proxy_property(
                env,
                class_name,
                key,
                raw_typedef,
                coerce_types,
                coerce_func,
                derived_class,
                listeners.get(key),
                post_coerce_failure_handlers.get(key),
                local_getter_var_template,
                local_setter_var_template,
                fast=fast,
            )
            column_types[key] = isinstance_compatible_types
            if key in properties and key in support_cls_attrs:
                current_prop = support_cls_attrs[key]
                if current_prop.fget is not None:
                    new_property = new_property.getter(current_prop.fget)
                if current_prop.fset is not None:
                    new_property = new_property.setter(current_prop.fset)
                if current_prop.fdel is not None:
                    new_property = new_property.deleter(current_prop.fdel)
            support_cls_attrs[key] = new_property
            class_cell_fixups.append((key, new_property))

        # Support columns are left as-is for slots
        support_columns = tuple(_dedupe(support_columns))

        ns_globals = {"NoneType": NoneType, "Flags": Flags, "typing": typing}
        ns_globals[class_name] = ReadOnly(None)

        if combined_columns:
            exec(
                compile(
                    make_fast_dumps(combined_columns, class_name), "<make_fast_dumps>", mode="exec"
                ),
                ns_globals,
                ns_globals,
            )
            class_cell_fixups.append(("_asdict", cast(FunctionType, ns_globals["_asdict"])))
            class_cell_fixups.append(("_astuple", cast(FunctionType, ns_globals["_astuple"])))
            class_cell_fixups.append(("_aslist", cast(FunctionType, ns_globals["_aslist"])))
            exec(
                compile(make_fast_eq(combined_columns), "<make_fast_eq>", mode="exec"),
                ns_globals,
                ns_globals,
            )
            exec(
                compile(
                    make_fast_clear(combined_columns, local_setter_var_template, class_name),
                    "<make_fast_clear>",
                    mode="exec",
                ),
                ns_globals,
                ns_globals,
            )
            class_cell_fixups.append(("clear", cast(FunctionType, ns_globals["_clear"])))
            exec(
                compile(
                    make_fast_getset_item(
                        combined_columns,
                        properties,
                        class_name,
                        local_getter_var_template,
                        local_setter_var_template,
                    ),
                    "<make_fast_getset_item>",
                    mode="exec",
                ),
                ns_globals,
                ns_globals,
            )
            iter_fields = []
            for field in combined_columns:
                if field in annotated_metadata and NoIterable in annotated_metadata[field]:
                    continue
                iter_fields.append(field)
            exec(
                compile(make_fast_iter(iter_fields), "<make_fast_iter>", mode="exec"),
                ns_globals,
                ns_globals,
            )
            del iter_fields
            pickle_fields = []
            for field in combined_columns:
                if field in annotated_metadata and NoPickle in annotated_metadata[field]:
                    continue
                pickle_fields.append(field)
            exec(
                compile(make_set_get_states(pickle_fields), "<make_set_get_states>", mode="exec"),
                ns_globals,
                ns_globals,
            )
            exec(
                compile(
                    make_defaults(tuple(combined_columns), defaults_var_template),
                    "<make_defaults>",
                    mode="exec",
                ),
                ns_globals,
                ns_globals,
            )
            class_cell_fixups.append(
                ("_set_defaults", cast(FunctionType, ns_globals["_set_defaults"]))
            )

        for key in (
            "__iter__",
            "__getstate__",
            "__setstate__",
            "__eq__",
            "_clear",
            "__getitem__",
            "__setitem__",
            "_asdict",
            "_astuple",
            "_aslist",
        ):
            # Move the autogenerated functions into the support class
            # Any overrides that *may* call them will be assigned
            # to the concrete class instead
            if key in ns_globals:
                if key in base_class_functions:
                    continue
                logger.debug(f"Copying {key} into {class_name} attributes")
                support_cls_attrs[key] = ns_globals.pop(key)
        if "_set_defaults" in ns_globals:
            data_class_attrs["_set_defaults"] = ns_globals.pop("_set_defaults")

        # Any keys subtracted must have no-nop setters in order to
        # allow for subtype relationship will behaving as if those keys are fundamentally
        # not there.
        for key in no_op_skip_keys:
            support_cls_attrs[key] = support_cls_attrs[f"_{key}_"] = property(
                __no_op_skip_get__, __no_op_skip_set__
            )

        if ns_globals:
            logger.debug(
                f"Did not add the following to {class_name} attributes: {tuple(ns_globals.keys())}"
            )

        support_cls_attrs["_columns"] = ReadOnly(FrozenMapping(combined_columns))
        support_cls_attrs["_no_op_properties"] = tuple(no_op_skip_keys)
        # The original typing.py mappings here:
        support_cls_attrs["_slots"] = ReadOnly(FrozenMapping(combined_slots))

        support_cls_attrs["_column_types"] = ReadOnly(FrozenMapping(column_types))
        support_cls_attrs["_all_coercions"] = ReadOnly(FrozenMapping(all_coercions))
        support_cls_attrs["_support_columns"] = tuple(support_columns)
        support_cls_attrs["_annotated_metadata"] = ReadOnly(FrozenMapping(annotated_metadata))
        support_cls_attrs["_nested_atomic_collection_keys"] = FrozenMapping(
            nested_atomic_collections
        )
        support_cls_attrs["_skipped_fields"] = skip_fields
        if "_modified_fields" not in support_cls_attrs:
            support_cls_attrs["_modified_fields"] = ()
        conf = AttrsDict(**mixins)
        conf["fast"] = fast
        extra_slots = tuple(_dedupe(pending_extra_slots))
        support_cls_attrs["__extra_slots__"] = ReadOnly(extra_slots)
        support_cls_attrs["_properties"] = properties = KeysView(properties)
        # create a constant ordered keys view representing the columns and the properties
        support_cls_attrs["_all_accessible_fields"] = ReadOnly(
            KeysView(tuple(field for field in chain(combined_columns, properties)))
        )
        support_cls_attrs["_configuration"] = ReadOnly(conf)

        support_cls_attrs["_listener_funcs"] = ReadOnly(listeners)
        # Ensure public class has zero slots!
        support_cls_attrs["__slots__"] = ()

        support_cls_attrs["_data_class"] = support_cls_attrs[f"_{class_name}"] = dc = ReadOnly(None)
        support_cls_attrs["_parent"] = parent_cell = ReadOnly(None)
        support_cls = super().__new__(klass, class_name, bases, support_cls_attrs)

        for prop_name, value in support_cls_attrs.items():
            if isinstance(value, property):
                value = property(
                    insert_class_closure(support_cls, value.fget),
                    insert_class_closure(support_cls, value.fset),
                )
            elif isinstance(value, FunctionType):
                value = insert_class_closure(support_cls, value)
            else:
                continue
            setattr(support_cls, prop_name, value)

        ns_globals["klass"] = support_cls
        dataclass_slots = (
            tuple("_{}_".format(key) for key in combined_columns) + support_columns + extra_slots
        )
        dataclass_template = env.get_template("data_class.jinja").render(
            class_name=class_name,
            slots=repr(dataclass_slots),
            data_class_attrs=data_class_attrs,
            class_slots=current_class_slots,
        )
        ns_globals["_dataclass_attrs"] = data_class_attrs
        exec(compile(dataclass_template, "<dcs>", mode="exec"), ns_globals, ns_globals)
        dc.value = data_class = ns_globals[f"_{class_name}"]
        data_class.__module__ = support_cls.__module__
        for key, value in data_class_attrs.items():
            if callable(value):
                setattr(data_class, key, insert_class_closure(data_class, value))
        data_class.__qualname__ = f"{support_cls.__qualname__}.{data_class.__name__}"
        parent_cell.value = support_cls
        klass.REGISTRY.add(support_cls)
        return support_cls

    def from_json(cls: Type[T], data: Dict[str, Any]) -> T:
        return cls(**data)

    def from_many_json(cls: Type[T], iterable: Iterable[Dict[str, Any]]) -> Tuple[T, ...]:
        return tuple(cls(**item) for item in iterable)

    def to_json(*instances):
        """
        Returns a dictionary compatible with json.dumps(...)
        """
        if isinstance(instances[0], type):
            instances = instances[1:]
        jsons = []
        cached_class_binary_encoders = {}
        types = {type(item) for item in instances}
        cached_class_binary_encoders = {
            instance_type: getattr(instance_type, "BINARY_JSON_ENCODERS", EMPTY_MAPPING)
            for instance_type in types
        }
        for instance in instances:
            instance_type = type(instance)
            annotated_metadata = instance_type._annotated_metadata
            skip_fields = set()
            for key in annotated_metadata:
                if NoJSON in annotated_metadata[key]:
                    skip_fields.add(key)
            result = {}
            special_binary_encoders = cached_class_binary_encoders[instance_type]
            for key, value in instance._asdict().items():
                if key in skip_fields:
                    continue
                # Support nested daos
                if hasattr(value, "to_json"):
                    value = value.to_json()
                # Date/datetimes
                elif hasattr(value, "isoformat"):
                    value = value.isoformat()
                elif isinstance(value, (bytearray, bytes)):
                    if key in special_binary_encoders:
                        value = special_binary_encoders[key](value)
                    else:
                        value = urlsafe_b64encode(value).decode()
                elif not isinstance(value, (str,)) and isinstance(
                    value, (AbstractMapping, Sequence)
                ):
                    value = _encode_simple_nested_base(value, immutable=True)
                result[key] = value
            jsons.append(result)
        return tuple(jsons)


class Delta(NamedTuple):
    state: str
    old: Any
    new: Any
    index: int


class LoggedDelta(NamedTuple):
    timestamp: float
    key: str
    delta: Delta


class Undefined(object):
    SINGLETON = None

    def __new__(cls):
        if Undefined.SINGLETON is not None:
            return Undefined.SINGLETON
        Undefined.SINGLETON = super().__new__(cls)
        return Undefined.SINGLETON

    def __repr__(self):
        return "Undefined"


UNDEFINED = Undefined()


class History(metaclass=Atomic):
    __slots__ = ("_changes", "_changed_keys", "_changed_index", "_suppress_history")
    setter_wrapper = "history-setter-wrapper.jinja"

    if TYPE_CHECKING:
        _columns: FrozenSet[str]

    def __init__(self, **kwargs):
        t_s = time.time()
        self._suppress_history = frozenset(
            field for field, metadata in self._annotated_metadata.items() if NoHistory in metadata
        )
        self._changes = {
            key: [Delta("default", UNDEFINED, value, 0)]
            for key, value in self._asdict().items()
            if key not in self._suppress_history
        }
        self._changed_keys = [
            (key, t_s) for key in self._columns if key not in self._suppress_history
        ]
        self._changed_index = len(self._changed_keys)

        super().__init__(**kwargs)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if self._flags & Flags.IN_CONSTRUCTOR and key in self._columns:
            # Always normalize the changed index to be after the constructor
            # is done.
            self._changed_index = len(self._changed_keys)

    def _record_change(self, key, old_value, new_value):
        if old_value == new_value:
            return
        if self._flags & Flags.DISABLE_HISTORY:
            return
        if key in self._suppress_history:
            return
        msg = "update"
        if self._flags & 2 == 2:
            msg = "initialized"
        else:
            old_msg, old_val_prior, _, index = self._changes[key][-1]
            if new_value == old_val_prior and old_msg == msg:
                self._changes[key].pop()
                del self._changed_keys[index]
                return

        index = len(self._changed_keys)
        self._changed_keys.append((key, time.time()))
        self._changes[key].append(Delta(msg, old_value, new_value, index))

    @property
    def is_dirty(self):
        return len(self._changed_keys[self._changed_index :]) > 0

    def reset_changes(self, *keys):
        if not keys:
            keys = self._columns.keys()
        self._flags |= Flags.DISABLE_HISTORY
        for key in keys:
            first_changes = self._changes[key][:2]
            self._changes[key][:2] = first_changes

            val = first_changes[0].new  # Constructor default, defaults to None
            if len(first_changes) == 2:
                assert first_changes[1].state == "initialized"
                val = first_changes[1].new  # Use the initialized default
            if getattr(self, key) != val:
                setattr(self, key, val)
        self._flags &= self._flags ^ Flags.DISABLE_HISTORY

    def list_changes(self):
        key_counter = {}
        for key, delta_time in self._changed_keys:
            if key not in key_counter:
                key_counter[key] = 0
            index = key_counter[key]
            delta = self._changes[key][index]

            yield LoggedDelta(delta_time, key, delta)
            key_counter[key] += 1


Atomic.register_mixin("history", History)


DEFAULTS = """{%- for field in fields %}
result._{{field}}_ = None
{%- endfor %}
"""


class IMapping(metaclass=Atomic):
    """
    Allow an instruct class instance to have the `keys()` function which is
    mandatory to support **item unpacking.

    This will collide with any property that's already named keys.
    """

    __slots__ = ()

    @ClassOrInstanceFuncsDescriptor
    def keys(cls, instance=None, *, all=False) -> Set[str]:
        if instance is not None:
            return keys(instance, all=all)
        return keys(cls, all=all)

    @keys.instance_function
    def keys(self, *, all=False) -> Set[str]:
        return keys(self, all=all)

    @ClassOrInstanceFuncsDescriptor
    def values(cls, item):
        return values(item)

    @values.instance_function
    def values(self):
        return values(self)

    @ClassOrInstanceFuncsDescriptor
    def items(cls, item):
        return items(item)

    @items.instance_function
    def items(self):
        return items(self)

    @ClassOrInstanceFuncsDescriptor
    def get(cls, instance, key, default=None):
        return get(instance, key, default)

    @get.instance_function
    def get(self, key, default=None):
        return get(self, key, default)


Atomic.register_mixin("mapping", IMapping)


def add_event_listener(*fields):
    def wrapper(func):
        func._event_listener_funcs = getattr(func, "_event_listener_funcs", ()) + fields
        return func

    return wrapper


def handle_type_error(*fields):
    def wrapper(func):
        func._post_coerce_failure_funcs = getattr(func, "_post_coerce_failure_funcs", ()) + fields
        return func

    return wrapper


def load_cls(cls, args, kwargs, skip_fields: Optional[FrozenMapping] = None):
    if skip_fields:
        cls = cls - skip_fields
    return cls(*args, **kwargs)


def _encode_simple_nested_base(iterable, *, immutable=None):
    """
    Handle an List[Base], Tuple[Base], Mapping[Any, Base]
    and coerce to json. Does not deeply traverse by design.
    """

    # Empty items short circuit:
    if not iterable:
        return iterable
    if isinstance(iterable, AbstractMapping):
        destination = iterable
        if immutable:
            if hasattr(iterable, "copy"):
                destination = iterable.copy()
            else:
                # initialize an empty form of an AbstractMapping:
                destination = type(iterable)()
        for key in iterable:
            value = iterable[key]
            if hasattr(value, "to_json"):
                destination[key] = value.to_json()
            else:
                destination[key] = value
        return iterable
    elif isinstance(iterable, Sequence):
        if immutable is None and isinstance(iterable, (tuple, frozenset)):
            immutable = True
        elif immutable is None and isinstance(iterable, (list, set)):
            immutable = False
        if immutable is None:
            try:
                iterable[0] = iterable[0]
            except Exception:
                immutable = True
            else:
                immutable = False
        if immutable:
            # Convert to a mutable list and replace items
            iterable = list(iterable)
        for index, item in enumerate(iterable):
            if hasattr(item, "to_json"):
                iterable[index] = item.to_json()
        return iterable
    return iterable


class JSONSerializable(metaclass=Atomic):
    __slots__ = ()

    def to_json(self) -> Dict[str, Any]:
        return Atomic.to_json(self)[0]

    def __json__(self) -> Dict[str, Any]:
        return self.to_json()

    @classmethod
    def from_json(cls: Type[T], data: Dict[str, Any]) -> T:
        return cls(**data)

    @classmethod
    def from_many_json(cls: Type[T], iterable: Iterable[Dict[str, Any]]) -> Tuple[T, ...]:
        return tuple(cls.from_json(item) for item in iterable)


def mark(**kwargs):
    def wrapper(func):
        for key, value in kwargs.items():
            setattr(func, f"_instruct_{key}", value)
        return func

    return wrapper


Atomic.register_mixin("json", JSONSerializable)


class SimpleBase(metaclass=Atomic):
    __slots__ = ("_flags",)
    __setter_template__ = ReadOnly("self._{key}_ = val")
    __getter_template__ = ReadOnly("return self._{key}_")
    __defaults__init__template__ = ReadOnly(DEFAULTS)

    @mark(base_cls=True)
    def __new__(cls, *args, **kwargs):
        # Get the edge class that has all the __slots__ defined
        cls = cls._data_class
        result = super().__new__(cls)
        result._flags = Flags.UNCONSTRUCTED
        result._set_defaults()
        assert "__dict__" not in dir(
            result
        ), "Violation - there should never be __dict__ on a slotted class"
        return result

    def __len__(self):
        cls = public_class(self, preserve_subtraction=True)
        return len(keys(cls))

    def __contains__(self, item):
        cls = public_class(self, preserve_subtraction=True)
        if item in cls._skipped_fields:
            return False
        return item in cls._all_accessible_fields

    def __reduce__(self):
        # Create an empty class then let __setstate__ in the autogen
        # code to handle passing raw values.

        # Get the public, unmessed with class:
        cls = public_class(self)
        skipped_fields = _dump_skipped_fields(type(self))
        return load_cls, (cls, (), {}, skipped_fields), self.__getstate__()

    @classmethod
    def _create_invalid_type(cls, field_name, val, val_type, types_required):
        if len(types_required) > 1:
            if len(types_required) == 2:
                expects = "either an {.__name__} or {.__name__}".format(*types_required)
            else:
                expects = (
                    f'either an {", ".join(x.__name__ for x in types_required[:-1])} '
                    f"or a {types_required[-1].__name__}"
                )
        else:
            expects = f"a {types_required[0].__name__}"
        return TypeError(
            f"Unable to set {field_name} to {val!r} ({val_type.__name__}). {field_name} expects "
            f"{expects}"
        )

    @classmethod
    def _create_invalid_value(cls, message, *args, **kwargs):
        return ValueError(message, *args, **kwargs)

    def _handle_init_errors(self, errors, errored_keys, unrecognized_keys):
        if unrecognized_keys:
            fields = ", ".join(unrecognized_keys)
            errors.append(self._create_invalid_value(f"Unrecognized fields {fields}"))
        if errors:
            typename = inflection.titleize(type(self).__name__[1:])
            if len(errors) == 1:
                raise ClassCreationFailed(
                    f"Unable to construct {typename}, encountered {len(errors)} "
                    f'error{"s" if len(errors) > 1 else ""}',
                    *errors,
                ) from errors[0]
            raise ClassCreationFailed(
                f"Unable to construct {typename}, encountered {len(errors)} "
                f'error{"s" if len(errors) > 1 else ""}',
                *errors,
            )

    def __init__(self, *args, **kwargs):
        self._flags |= Flags.IN_CONSTRUCTOR
        self._flags |= Flags.DEFAULTS_SET
        errors = []
        errored_keys = []
        class_keys = keys(self.__class__)
        if len(args) > len(class_keys):
            raise TypeError(
                f"__init__() takes {len(class_keys)} positional arguments but {len(args)} were given"
            )
        # Set by argument position
        for key, value in zip(class_keys, args):
            try:
                setattr(self, key, value)
            except Exception as e:
                errors.append(e)
                errored_keys.append(key)
        class_keys = self._all_accessible_fields
        # Set by keywords
        for key in class_keys & kwargs.keys():
            value = kwargs[key]
            try:
                setattr(self, key, value)
            except Exception as e:
                errors.append(e)
                errored_keys.append(key)
        unrecognized_keys = ()
        if kwargs.keys() - class_keys:
            unrecognized_keys = kwargs.keys() - class_keys
        self._handle_init_errors(errors, errored_keys, unrecognized_keys)
        self._flags = Flags.INITIALIZED

    @mark(base_cls=True)
    def _clear(self, fields: Iterable[str] = None):
        pass

    @mark(base_cls=True)
    def _asdict(self) -> Dict[str, Any]:
        return {}

    @mark(base_cls=True)
    def _astuple(self) -> Tuple[Any, ...]:
        return ()

    @mark(base_cls=True)
    def _aslist(self) -> List[Any]:
        return []

    @mark(base_cls=True)
    def _set_defaults(self):
        # ARJ: Override to set defaults instead of inside the `__init__` function
        # Note: Always call ``super()._set_defaults()`` FIRST as if you
        # call it afterwards, the inheritance tree will zero initialize it first
        return self

    @mark(base_cls=True)
    def __iter__(self):
        """
        Dummy iter.
        """
        if False:
            yield


class Base(SimpleBase, mapping=True, json=True):
    __slots__ = ()


AbstractMapping.register(Base)  # pytype: disable=attribute-error

__all__ = [
    # Instruct utilities:
    "public_class",
    "keys",
    "values",
    "items",
    "get",
    "clear",
    "reset_to_defaults",
    "asdict",
    "astuple",
    "aslist",
    "show_all_fields",
    # default end-user base classes
    "SimpleBase",
    "Base",
    # class event listeners:
    "add_event_listener",
    "handle_type_error",
    # class instantiation status:
    "Flags",
    # metaclass
    "Atomic",
    # history
    "History",
    "Delta",
    "LoggedDelta",
    # mapping support
    "IMapping",
    # json support
    "JSONSerializable",
    # misc
    "UNDEFINED",
    "NoJSON",
    "NoPickle",
    "NoIterable",
    "NoHistory",
    "Range",
    "RangeError",
    "RangeFlags",
]  # noqa
