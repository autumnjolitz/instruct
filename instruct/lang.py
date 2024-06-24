from functools import singledispatch
from inflection import titleize as _titleize, humanize as _humanize, pluralize as _pluralize


@singledispatch
def titleize(s):
    if isinstance(s, type):
        type_name = s.__name__
    else:
        type_name = type(s).__name__
    raise TypeError(f"Unsupported type {type_name}")


@singledispatch
def humanize(s):
    if isinstance(s, type):
        type_name = s.__name__
    else:
        type_name = type(s).__name__
    raise TypeError(f"Unsupported type {type_name}")


@singledispatch
def pluralize(s):
    if isinstance(s, type):
        type_name = s.__name__
    else:
        type_name = type(s).__name__
    raise TypeError(f"Unsupported type {type_name}")


@titleize.register
def _(s: str) -> str:
    return _titleize(s)


@humanize.register
def _(s: str) -> str:
    return _humanize(s)


@pluralize.register
def _(s: str) -> str:
    return _pluralize(s)
