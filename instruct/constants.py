"""
Constants for Annotated signaling to Instruct.
"""

from __future__ import annotations
from enum import IntEnum


class _NoPickle(object):
    """
    Used to signal via an ``Annotated[type_cls, NoPickle]`` on an
    instruct class to tell it to skip pickling this field
    """

    def __new__(cls):
        return NoPickle

    def __reduce__(self):
        return (_NoPickle, ())

    def __copy__(self) -> _NoPickle:
        return NoPickle

    def __deepcopy__(self, memo) -> _NoPickle:
        return NoPickle

    def __call__(self, default):
        pass

    def __repr__(self):
        return type(self).__name__[1:]

    def __str__(self):
        return str(self.__class__.__name__[1:])


class _NoJSON(object):
    def __new__(cls):
        return NoPickle

    def __reduce__(self):
        return (_NoJSON, ())

    def __copy__(self) -> _NoJSON:
        return NoJSON

    def __deepcopy__(self, memo) -> _NoJSON:
        return NoJSON

    def __call__(self, default):
        pass

    def __repr__(self):
        return type(self).__name__[1:]

    def __str__(self):
        return str(self.__class__.__name__[1:])


class _NoIterable(object):
    def __new__(cls):
        return NoIterable

    def __reduce__(self):
        return (_NoIterable, ())

    def __copy__(self) -> _NoIterable:
        return NoIterable

    def __deepcopy__(self, memo) -> _NoIterable:
        return NoIterable

    def __call__(self, default):
        pass

    def __repr__(self):
        return type(self).__name__[1:]

    def __str__(self):
        return str(self.__class__.__name__[1:])


class _NoHistory(object):
    def __new__(cls):
        return NoHistory

    def __reduce__(self):
        return (_NoHistory, ())

    def __copy__(self) -> _NoHistory:
        return NoHistory

    def __deepcopy__(self, memo) -> _NoHistory:
        return NoHistory

    def __call__(self, default):
        pass

    def __repr__(self):
        return type(self).__name__[1:]

    def __str__(self):
        return str(self.__class__.__name__[1:])


class _Undefined(object):
    def __new__(cls):
        return Undefined

    def __reduce__(self):
        return (_Undefined, ())

    def __copy__(self) -> _Undefined:
        return Undefined

    def __deepcopy__(self, memo) -> _Undefined:
        return Undefined

    def __call__(self, default):
        pass

    def __repr__(self):
        return type(self).__name__[1:]

    def __str__(self):
        return str(self.__class__.__name__[1:])


try:
    NoPickle  # type: ignore
except NameError:
    NoPickle = object.__new__(_NoPickle)

try:
    NoJSON  # type: ignore
except NameError:
    NoJSON = object.__new__(_NoJSON)

try:
    NoIterable  # type: ignore
except NameError:
    NoIterable = object.__new__(_NoIterable)

try:
    NoHistory  # type: ignore
except NameError:
    NoHistory = object.__new__(_NoHistory)

try:
    Undefined  # type: ignore
except NameError:
    Undefined = object.__new__(_Undefined)


class RangeFlags(IntEnum):
    """
    Interval ranges allowed.

    See https://en.wikipedia.org/wiki/Interval_(mathematics)
    """

    OPEN_OPEN = 1
    CLOSED_CLOSED = 2
    CLOSED_OPEN = 4
    OPEN_CLOSED = 8


class Range:
    """
    Useful for something like ``Annotated[int, Range(0, 256, RangeFlags.CLOSED_OPEN)]`` to indicate
    an integer should be between 0 and 255.

    If a value does not satisfy the interval, it will be rejected.
    """

    __slots__ = ("_lower", "_upper", "_flags", "_type_restrictions", "_type_restrictions_orig")

    def __init__(
        self, lower, upper, flags: RangeFlags = RangeFlags.CLOSED_OPEN, *, type_restrictions=()
    ):
        from .typedef import parse_typedef

        if upper < lower:
            raise ValueError("upper must be >= lower")
        if not isinstance(type_restrictions, type) and not (
            isinstance(type_restrictions, tuple)
            and all(isinstance(x, type) for x in type_restrictions)
        ):
            raise TypeError("type_restrictions must be a tuple of types!")

        self._lower = lower
        self._upper = upper
        self._flags = flags
        if isinstance(type_restrictions, type):
            type_restrictions = (type_restrictions,)
        if type_restrictions:
            self._type_restrictions_orig = type_restrictions
            self._type_restrictions = parse_typedef(type_restrictions)
        else:
            self._type_restrictions = self._type_restrictions_orig = ()

    def applies(self, value):
        """
        Given a value of type T, check if the Range is constrained to those types.

        Return True if type restrictions are not set.
        """
        if self._type_restrictions:
            if not isinstance(value, self._type_restrictions):
                return False
        return True

    def copy(self):
        """
        Makes a copy of the Range
        """
        return self.__class__(
            self._lower, self._upper, self._flags, type_restrictions=self._type_restrictions_orig
        )

    def __contains__(self, value):
        """
        Check if value fits within the range.
        """
        if not self.applies(value):
            return False
        if self._flags is RangeFlags.OPEN_OPEN:
            return self._lower < value < self._upper
        elif self._flags is RangeFlags.CLOSED_CLOSED:
            return self._lower <= value <= self._upper
        elif self._flags is RangeFlags.CLOSED_OPEN:
            return self._lower <= value < self._upper
        elif self._flags is RangeFlags.OPEN_CLOSED:
            return self._lower < value <= self._upper
        raise NotImplementedError

    def __repr__(self):
        return (
            f"{self.__class__.__qualname__}({self._lower!r}, {self._upper!r}, "
            f"flags={self._flags.name}, type_restrictions={self._type_restrictions_orig!r})"
        )

    def __str__(self):
        if self._flags is RangeFlags.OPEN_OPEN:
            range_repr = f"({self._lower!r}, {self._upper!r})"
        elif self._flags is RangeFlags.CLOSED_CLOSED:
            range_repr = f"[{self._lower!r}, {self._upper!r}]"
        elif self._flags is RangeFlags.CLOSED_OPEN:
            range_repr = f"[{self._lower!r}, {self._upper!r})"
        elif self._flags is RangeFlags.OPEN_CLOSED:
            range_repr = f"({self._lower!r}, {self._upper!r}]"
        else:
            raise NotImplementedError
        if self._type_restrictions_orig:
            if len(self._type_restrictions_orig) == 1:
                return f"{self._type_restrictions_orig[0].__name__}{range_repr}"
            return (
                "({})".format(", ".join(type.__name__ for type in self._type_restrictions_orig))
                + range_repr
            )
        return range_repr
