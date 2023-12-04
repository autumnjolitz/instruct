from __future__ import annotations
import collections.abc
from collections.abc import Mapping as AbstractMapping
from typing import Union, Any, AnyStr, List, Tuple, cast, Optional, Callable, Type

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from typing_extensions import get_origin

try:
    from typing import get_args
except ImportError:
    from typing_extensions import get_args
from .utils import flatten_restrict as flatten
from .typing import ICustomTypeCheck
from .constants import Range
from .exceptions import RangeError

get_args


def make_custom_typecheck(func) -> Type[ICustomTypeCheck]:
    """Create a custom type that will turn `isinstance(item, klass)` into `func(item)`
    """
    typename = "WrappedType<{}>"

    class WrappedType(type):
        __slots__ = ()

        def __instancecheck__(self, instance):
            return func(instance)

        def __repr__(self):
            return typename.format(super().__repr__())

    class _WrappedType(metaclass=WrappedType):
        __slots__ = ()

        @staticmethod
        def set_name(name):
            nonlocal typename
            typename = name
            _WrappedType.__name__ = name
            _WrappedType._name__ = name
            return name

    return cast(Type[ICustomTypeCheck], _WrappedType)


def ismetasubclass(cls, metacls):
    return issubclass(type(cls), metacls)


def issubormetasubclass(type_cls, cls, metaclass=False):
    if metaclass is True:
        type_cls = type(type_cls)
    return issubclass(type_cls, cls)


def has_collect_class(
    type_hints: Union[Type, Tuple[Type, ...], List[Type]],
    root_cls: Type,
    *,
    _recursing=False,
    metaclass=False,
):
    if not isinstance(type_hints, (tuple, list)):
        type_hints = (type_hints,)
    for type_cls in type_hints:
        module = getattr(type_cls, "__module__", None)
        if module != "typing":
            continue
        if hasattr(type_cls, "_name") and type_cls._name is None and type_cls.__origin__ is Union:
            if _recursing:
                for child in type_cls.__args__:
                    if isinstance(child, type) and issubormetasubclass(
                        child, root_cls, metaclass=metaclass
                    ):
                        return True
                    if has_collect_class(child, root_cls, _recursing=True, metaclass=metaclass):
                        return True
            continue
        elif isinstance(getattr(type_cls, "__origin__", None), type) and (
            issubclass(type_cls.__origin__, collections.abc.Iterable)
            and issubclass(type_cls.__origin__, collections.abc.Container)
        ):
            if issubclass(type_cls.__origin__, collections.abc.Mapping):
                key_type, value_type = type_cls.__args__
                if has_collect_class(value_type, root_cls, _recursing=True, metaclass=metaclass):
                    return True
            else:
                for child in type_cls.__args__:
                    if isinstance(child, type) and issubormetasubclass(
                        child, root_cls, metaclass=metaclass
                    ):
                        return True
                    elif has_collect_class(child, root_cls, _recursing=True, metaclass=metaclass):
                        return True
    return False


def find_class_in_definition(
    type_hints: Union[Type, Tuple[Type, ...], List[Type]], root_cls: Type, *, metaclass=False
):
    if type_hints is Ellipsis:
        return
    assert (
        isinstance(type_hints, tuple)
        or is_typing_definition(type_hints)
        or isinstance(type_hints, type)
    ), f"{type_hints} is a {type(type_hints)}"

    if is_typing_definition(type_hints):
        type_cls: Type = cast(Type, type_hints)
        type_cls_copied: bool = False
        if hasattr(type_cls, "_name") and type_cls._name is None and type_cls.__origin__ is Union:
            args = type_cls.__args__[:]
            for index, child in enumerate(args):
                if isinstance(child, type) and issubormetasubclass(
                    child, root_cls, metaclass=metaclass
                ):
                    replacement = yield child
                else:
                    replacement = yield from find_class_in_definition(
                        child, root_cls, metaclass=metaclass
                    )
                if replacement is not None:
                    args = args[:index] + (replacement,) + args[index + 1 :]
            if args != type_cls.__args__:
                type_cls = type_cls.copy_with(args)
                type_cls_copied = True

        elif isinstance(getattr(type_cls, "__origin__", None), type) and (
            issubclass(type_cls.__origin__, collections.abc.Iterable)
            and issubclass(type_cls.__origin__, collections.abc.Container)
        ):
            if issubclass(type_cls.__origin__, collections.abc.Mapping):
                key_type, value_type = args = type_cls.__args__
                if isinstance(value_type, type) and issubormetasubclass(
                    value_type, root_cls, metaclass=metaclass
                ):
                    replacement = yield value_type
                else:
                    replacement = yield from find_class_in_definition(
                        value_type, root_cls, metaclass=metaclass
                    )
                if replacement is not None:
                    args = (key_type, replacement)
                if args != type_cls.__args__:
                    type_cls = type_cls.copy_with(args)
                    type_cls_copied = True
            else:
                args = type_cls.__args__[:]
                for index, child in enumerate(args):
                    if isinstance(child, type) and issubormetasubclass(
                        child, root_cls, metaclass=metaclass
                    ):
                        replacement = yield child
                    else:
                        replacement = yield from find_class_in_definition(
                            child, root_cls, metaclass=metaclass
                        )
                    if replacement is not None:
                        args = args[:index] + (replacement,) + args[index + 1 :]
                if args != type_cls.__args__:
                    type_cls = type_cls.copy_with(args)
                    type_cls_copied = True
        if type_cls_copied:
            return type_cls
        return None

    if isinstance(type_hints, type):
        if issubormetasubclass(type_hints, root_cls, metaclass=metaclass):
            replacement = yield type_hints
            if replacement is not None:
                return replacement
        return None

    for index, type_cls in enumerate(type_hints[:]):
        if isinstance(type_cls, type) and issubormetasubclass(
            type_cls, root_cls, metaclass=metaclass
        ):
            replacement = yield type_cls
        else:
            replacement = yield from find_class_in_definition(
                type_cls, root_cls, metaclass=metaclass
            )
        if replacement is not None:
            type_hints = type_hints[:index] + (replacement,) + type_hints[index + 1 :]
    return type_hints


def create_custom_type(container_type, *args, check_ranges=()):
    if is_typing_definition(container_type):
        if hasattr(container_type, "_name") and container_type._name is None:
            if container_type.__origin__ is Union:
                types = flatten(
                    (create_custom_type(arg) for arg in container_type.__args__), eager=True
                )
                if check_ranges:

                    def test_func(value) -> bool:
                        if not isinstance(value, types):
                            return False
                        failed_ranges = []
                        for rng in check_ranges:
                            if rng.applies(value):
                                try:
                                    in_range = value in rng
                                except TypeError:
                                    continue
                                else:
                                    if in_range:
                                        return True
                                    else:
                                        failed_ranges.append(rng)
                        if failed_ranges:
                            raise RangeError(value, failed_ranges)
                        return False

                else:

                    def test_func(value) -> bool:
                        """
                        Check if the value is of the type set
                        """
                        return isinstance(value, types)

            elif container_type.__origin__ is Literal:
                from . import Atomic, public_class

                def test_func(value) -> bool:
                    """
                    Operate on a Literal type
                    """
                    for arg in args:
                        if arg is value:
                            # Exact match on ``is``, useful for enums
                            return True
                        elif arg == value:
                            # Equality by value. This may be part of an
                            # overridden __eq__, so check the types too!
                            if isinstance(arg, type):
                                arg_type = arg
                            else:
                                arg_type = type(arg)
                            if isinstance(arg_type, Atomic):
                                arg_type = public_class(arg_type, preserve_subtraction=True)
                            if isinstance(value, arg_type):
                                return True
                    return False

        elif container_type is AnyStr:
            if check_ranges:

                def test_func(value) -> bool:
                    if not isinstance(value, (str, bytes)):
                        return False
                    failed_ranges = []
                    for rng in check_ranges:
                        if rng.applies(value):
                            try:
                                in_range = value in rng
                            except TypeError:
                                continue
                            else:
                                if in_range:
                                    return True
                                else:
                                    failed_ranges.append(rng)
                    if failed_ranges:
                        raise RangeError(value, failed_ranges)
                    return False

            else:
                return (str, bytes)
        elif container_type is Any:
            return object
        elif isinstance(getattr(container_type, "__origin__", None), type) and (
            issubclass(container_type.__origin__, collections.abc.Iterable)
            and issubclass(container_type.__origin__, collections.abc.Container)
        ):
            return parse_typedef(container_type)
        else:
            raise NotImplementedError(container_type, container_type._name)
    elif isinstance(container_type, type) and (
        issubclass(container_type, collections.abc.Iterable)
        and issubclass(container_type, collections.abc.Container)
    ):
        test_func = create_typecheck_container(container_type, args)
    elif isinstance(container_type, type) and not args:
        if check_ranges:

            def test_func(value) -> bool:
                if not isinstance(value, container_type):
                    return False
                failed_ranges = []
                for rng in check_ranges:
                    if rng.applies(value):
                        try:
                            in_range = value in rng
                        except TypeError:
                            continue
                        else:
                            if in_range:
                                return True
                            else:
                                failed_ranges.append(rng)
                if failed_ranges:
                    raise RangeError(value, failed_ranges)
                return False

        else:
            return container_type
    else:
        assert isinstance(container_type, tuple), f"container_type is {container_type}"
        if check_ranges:

            def test_func(value):
                if not isinstance(value, container_type):
                    return False
                failed_ranges = []
                for rng in check_ranges:
                    if rng.applies(value):
                        try:
                            in_range = value in rng
                        except TypeError:
                            continue
                        else:
                            if in_range:
                                return True
                            else:
                                failed_ranges.append(rng)
                if failed_ranges:
                    raise RangeError(value, failed_ranges)
                return False

        else:

            def test_func(value):
                return isinstance(value, container_type)

    return make_custom_typecheck(test_func)


def create_typecheck_container(container_type, items: Tuple[Any]):
    test_types = []
    test_func: Optional[Callable[[Any], bool]] = None

    if issubclass(container_type, tuple):
        container_type = tuple
        # Special support: Tuple[type, ...]
        if any(item is Ellipsis for item in items):
            if len(items) != 2:
                raise TypeError("Tuple[type, ...] is allowed but it must be a two pair tuple!")
            homogenous_type_spec, ellipsis = items
            if ellipsis is not Ellipsis or homogenous_type_spec is Ellipsis:
                raise TypeError(
                    "Tuple[type, ...] is allowed but it must have ellipsis as second arg"
                )
            homogenous_type = parse_typedef(homogenous_type_spec)

            def test_func(value):
                if not isinstance(value, container_type):
                    return False
                return all(isinstance(item, homogenous_type) for item in value)

            return test_func

        else:
            for some_type in items:
                test_types.append(create_custom_type(some_type))

            def test_func(value):
                if not isinstance(value, container_type):
                    return False
                if len(value) != len(test_types):
                    raise ValueError(f"Expecting a {len(test_types)} value tuple!")
                for index, (item, item_type) in enumerate(zip(value, test_types)):
                    if not isinstance(item, item_type):
                        # raise TypeError(f"{item!r} at index {index} should be a {item_type}")
                        return False
                return True

    elif issubclass(container_type, AbstractMapping):
        if items:
            key_type_spec, value_type_spec = items
            key_type = parse_typedef(key_type_spec)
            value_type = parse_typedef(value_type_spec)

            def test_func(mapping) -> bool:
                if not isinstance(mapping, container_type):
                    return False
                for key, value in mapping.items():
                    if not all((isinstance(key, key_type), isinstance(value, value_type))):
                        return False
                return True

    if test_func is None:
        if items:
            for some_type in items:
                test_types.append(create_custom_type(some_type))
            test_types = tuple(test_types)

            def test_func(value):
                if not isinstance(value, container_type):
                    return False
                return all(isinstance(item, test_types) for item in value)

        else:

            def test_func(value):
                return isinstance(value, container_type)

    return test_func


def is_typing_definition(item):
    module_name: str = getattr(item, "__module__", None)
    if module_name in ("typing", "typing_extensions"):
        return True
    if module_name == "builtins":
        origin = get_origin(item)
        if origin is not None:
            return is_typing_definition(origin)
    return False


def parse_typedef(
    typedef: Union[Tuple[Type, ...], List[Type]], *, check_ranges: Tuple[Range, ...] = ()
) -> Union[Type, Tuple[Type]]:
    """
    Break a type def into types suitable for doing an isinstance(item, ...) check.

    typeA -> typeA
    (typeA, typeB) -> (typeA, typeB)
    Union[typeA, typeB] -> (typeA, typeB)
    Optional[typeA] -> (NoneType, typeA)

    Support collection typelimiting like

    List[int] -> (IntList,) where IntList is a custom type with a special
    metaclass that executes an embedded function for checking if all members
    of the collection is the right type. i.e all(isintance(item, int) for item in object)
    """
    if type(typedef) is tuple or type(typedef) is list:
        return tuple(parse_typedef(x) for x in typedef)

    if not is_typing_definition(typedef):
        # ARJ: Okay, we're not a typing module descendant.
        # Are we a type itelf?
        if isinstance(typedef, type):
            if check_ranges:
                return create_custom_type(typedef, check_ranges=check_ranges)
            else:
                return typedef
        raise NotImplementedError(f"Unknown typedef definition {typedef!r} ({type(typedef)})!")

    as_origin_cls = get_origin(typedef)
    if typedef is AnyStr:
        return create_custom_type(typedef, check_ranges=check_ranges)
    elif typedef is Any:
        return object
    elif typedef is Union:
        raise TypeError("A bare union means nothing!")
    elif as_origin_cls is Annotated:
        typedef, *raw_metadata = get_args(typedef)
        # Skip to the internal type:
        # flags = []
        check_ranges = []
        for annotation in raw_metadata:
            if isinstance(annotation, Range):
                check_ranges.append(annotation)
            # elif (getattr(annotation, '__module__', '') or '').startswith('instruct.constants'):
            #     flags.append(annotation)
        check_ranges = tuple(check_ranges)
        new_type = parse_typedef(typedef, check_ranges=check_ranges)
        if check_ranges:
            if is_typing_definition(typedef):
                new_name = str(typedef)
                if new_name.startswith(("typing_extensions.")):
                    new_name = new_name[len("typing_extensions.") :]
                if new_name.startswith(("typing.")):
                    new_name = new_name[len("typing.") :]
            else:
                new_name = typedef.__name__
            new_type.set_name(new_name)
        return new_type
    elif as_origin_cls is Union:
        if check_ranges:
            return create_custom_type(typedef, check_ranges=check_ranges)
        return flatten((parse_typedef(argument) for argument in typedef.__args__), eager=True)
    elif as_origin_cls is Literal:
        if not typedef.__args__:
            raise NotImplementedError("Literals must be non-empty!")
        items = []
        for cls, arg in zip(
            (create_custom_type(typedef, arg) for arg in typedef.__args__), typedef.__args__
        ):
            if isinstance(arg, str):
                cls.set_name(f'"{arg}"')
            else:
                cls.set_name(f"{arg}")
            items.append(cls)
        return flatten(items, eager=True)
    elif as_origin_cls is not None:
        if is_typing_definition(typedef) and hasattr(typedef, "_name") and typedef._name is None:
            # special cases!
            raise NotImplementedError(
                f"The type definition for {typedef} is not supported, report as an issue."
            )
        args = get_args(typedef)
        if args:
            cls = create_custom_type(as_origin_cls, *args)
            new_name = str(typedef)
            if new_name.startswith(("typing_extensions.")):
                new_name = new_name[len("typing_extensions.") :]
            if new_name.startswith(("typing.")):
                new_name = new_name[len("typing.") :]
            cls.set_name(new_name)
            return cls
        return as_origin_cls
    raise NotImplementedError(
        f"The type definition for {typedef!r} is not supported yet, report as an issue."
    )
