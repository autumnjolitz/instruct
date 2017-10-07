from collections import Mapping, namedtuple
from typing import Union
import time
from enum import IntEnum

from .about import __version__
__version__  # Silence unused import warning.

NoneType = type(None)
GETTER = '''
def make_getter(type_def):
    def {key}(self) -> type_def:
        return self._{key}
    return {key}
'''

SETTER = '''
def make_setter(type_def, fast):
    type_restriction = type_def
    if hasattr(type_def, '__origin__') and type_def.__origin__ is Union:
        type_restriction = type_def._subs_tree()
        if type_restriction is Union:
            type_restriction = (object,)
        elif isinstance(type_restriction, tuple):
            # Trim off the preceding Union datatype
            type_restriction = type_restriction[1:]
    if isinstance(type_restriction, type):
        type_restriction = (type_restriction,)
    assert isinstance(type_restriction, tuple) and all(
        isinstance(cls, type) for cls in type_restriction), \\
        'Not all types {{!r}} are cls'.format(type_restriction)
    if not fast:
        def {key}(self, val: type_def) -> NoneType:
            if not isinstance(val, type_restriction):
                raise TypeError('{{!r}} must be a {{}}'.format(val, type_restriction))
            self._{key} = val
    else:
        def {key}(self, val: type_def) -> NoneType:
            self._{key} = val
    return {key}
'''

CHANGE_LOG_SETTER = '''
def make_setter(type_def, fast):
    type_restriction = type_def
    if hasattr(type_def, '__origin__') and type_def.__origin__ is Union:
        type_restriction = type_def._subs_tree()
        if type_restriction is Union:
            type_restriction = (object,)
        elif isinstance(type_restriction, tuple):
            # Trim off the preceding Union datatype
            type_restriction = type_restriction[1:]
    if isinstance(type_restriction, type):
        type_restriction = (type_restriction,)
    assert isinstance(type_restriction, tuple) and all(
        isinstance(cls, type) for cls in type_restriction), \\
        'Not all types {{!r}} are cls'.format(type_restriction)
    if not fast:
        def {key}(self, val: type_def) -> NoneType:
            old_value = self._{key}
            if not isinstance(val, type_restriction):
                raise TypeError('{{!r}} must be a {{}}'.format(val, type_restriction))
            self._{key} = val
            self._record_change('{key}', old_value, val)
    else:
        def {key}(self, val: type_def) -> NoneType:
            old_value = self._{key}
            self._{key} = val
            self._record_change('{key}', old_value, val)
    return {key}
'''


def make_redirector(variables):
    def __getattr__(self, key):
        if key in variables:
            key = f'_{key}'
        return super(self.__class__, self).__getattr__(key)

    def __setattr__(self, key, value):
        if key in variables:
            key = f'_{key}'
        return super(self.__class__, self).__setattr__(key, value)

    return __getattr__, __setattr__


class ColumnDefinition:
    def __init__(self, columns):
        self.columns = frozenset(columns)

    def __get__(self, obj, objtype=None):
        return self.columns

    def __set__(self, obj, val):
        raise NotImplementedError


class Config:
    def __init__(self, **kwargs):
        self.config = kwargs

    def __get__(self, obj, objtype=None):
        return self.config

    def __set__(self, obj, val):
        raise NotImplementedError


class Atomic(type):
    def __new__(klass, class_name, bases, attrs, fast=None, history=False):
        if fast is None:
            fast = not __debug__
        if '__slots__' not in attrs:
            raise TypeError(
                f'You must define __slots__ for {class_name} to constrain the typespace')
        if not isinstance(attrs['__slots__'], Mapping):
            if isinstance(attrs['__slots__'], tuple):
                return super().__new__(klass, class_name, bases, attrs)
            raise TypeError(
                f'The __slots__ definition for {class_name} must be a mapping or empty tuple!')

        if 'fast' in attrs:
            fast = attrs.pop('fast')
        columns = list(attrs['__slots__'])
        for cls in bases:
            if hasattr(cls, '__slots__') and isinstance(cls.__slots__, dict):
                columns.extend(cls.__slots__)
        setter_template = SETTER
        if history:
            setter_template = CHANGE_LOG_SETTER
            bases += (History,)

        attrs['_columns'] = ColumnDefinition(columns)
        attrs['_configuration'] = Config(history=history)
        ns_globals = {'Union': Union, 'NoneType': type(None)}
        for key, value in attrs['__slots__'].items():
            if key[0] == '_':
                continue
            attrs['__slots__'][f'_{key}'] = value
            del attrs['__slots__'][key]
            ns = {}
            exec(GETTER.format(key=key), ns_globals, ns)
            exec(setter_template.format(key=key), ns_globals, ns)
            attrs[key] = property(ns['make_getter'](value), ns['make_setter'](value, fast))
        return super().__new__(klass, class_name, bases, attrs)


Delta = namedtuple('Delta', ['state', 'old', 'new', 'index'])
LoggedDelta = namedtuple('LoggedDelta', ['timestamp', 'key', 'delta'])


class History(object):
    __slots__ = ()

    def _record_change(self, key, old_value, new_value):
        if old_value == new_value:
            return
        msg = 'update'
        if self._flags & 2 == 2:
            msg = 'initialized'
        else:
            _, old_val_prior, _, index = self._changes[key][-1]
            if new_value == old_val_prior:
                self._changes[key].pop()
                del self._changed_keys[index]
                return

        index = len(self._changed_keys)
        self._changed_keys.append((key, time.time()))
        self._changes[key].append(Delta(msg, old_value, new_value, index))

    @property
    def is_dirty(self):
        return len(self._changed_keys[self._changed_index:]) > 0

    def reset_changes(self, *keys):
        if not keys:
            keys = self._columns
        for key in keys:
            first_changes = self._changes[key][:2]
            val = first_changes[0][2]  # Constructor default, defaults to None
            if len(first_changes) == 2:
                assert first_changes[1][0] == 'initialized'
                val = first_changes[1][2]  # Use the initialized default
            setattr(self, f'_{key}', val)

    def list_changes(self):
        key_counter = {}
        for key, delta_time in self._changed_keys:
            if key not in key_counter:
                key_counter[key] = 0
            index = key_counter[key]
            delta = self._changes[key][index]

            yield LoggedDelta(delta_time, key, delta)
            key_counter[key] += 1


class Flags(IntEnum):
    IN_CONSTRUCTOR = 1
    DEFAULTS_SET = 2
    INITIALIZED = 4


class Base(metaclass=Atomic):
    __slots__ = ('_changes', '_changed_keys', '_flags', '_changed_index')

    def __init__(self, **kwargs):
        self._flags = Flags.IN_CONSTRUCTOR
        self._changed_index = -1
        if self._configuration['history']:
            self._changed_index = 0
            t_s = time.time()
            self._changes = {
                key: [Delta('default', None, getattr(self, key, None), 0)] for key in self._columns
            }
            self._changed_keys = [(key, t_s) for key in self._columns]
            self._changed_index += len(self._changed_keys)
        self._flags |= Flags.DEFAULTS_SET
        for key in self._columns & kwargs.keys():
            setattr(self, key, kwargs[key])
            self._changed_index += 1

        if kwargs.keys() - self._columns:
            fields = ', '.join(kwargs.keys() - self._columns)
            raise ValueError(f'Unrecognized fields {fields}')
        self._flags = Flags.INITIALIZED

