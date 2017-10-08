from collections import Mapping, namedtuple
from typing import Union
import time
from enum import IntEnum
import textwrap

from .about import __version__
__version__  # Silence unused import warning.

NoneType = type(None)
SETTER_BLOCK = 'self._{key} = val'
GETTER_BLOCK = 'return self._{key}'


GETTER_TEMPLATE = '''
def make_getter(type_def):
    def {key}(self) -> type_def:
        {getter_block}
    return {key}
'''

SETTER_TEMPLATE = '''
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
            {setter_block}
    else:
        def {key}(self, val: type_def) -> NoneType:
            {setter_block}
    return {key}
'''
C_DATA_SETTER_TEMPLATE = '''
def make_setter(type_def, fast):
    if True:
        def {key}(self, val: type_def) -> NoneType:
            {setter_block}
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


class ReadonlyClassVariable:
    __slots__ = ('value',)

    def __init__(self, value):
        self.value = value

    def __get__(self, obj, obj_type=None):
        return self.value


class ColumnDefinition:
    def __init__(self, columns):
        self.columns = columns

    def __get__(self, obj, objtype=None):
        return self.columns

    def __set__(self, obj, val):
        raise NotImplementedError


class Config:
    def __init__(self, value):
        self.value = value

    def __getattr__(self, key):
        try:
            return self.value[key]
        except KeyError:
            return None


class ConfigDefinition:
    def __init__(self, **kwargs):
        self.config = Config(kwargs)

    def __get__(self, obj, objtype=None):
        return self.config

    def __set__(self, obj, val):
        raise NotImplementedError


class Atomic(type):
    mixins = {}

    @classmethod
    def register_class_mixin(cls, name, klass_mixin, **overrides):
        cls.mixins[name] = (klass_mixin, overrides)

    def __new__(klass, class_name, bases, attrs, fast=None, **kwargs):
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
        slot_ordering = None
        if '__slot_order__' in attrs:
            if not isinstance(attrs['__slot_order__'], ReadonlyClassVariable):
                attrs['__slot_order__'] = ReadonlyClassVariable(attrs['__slot_order__'])
            slot_ordering = attrs['__slot_order__'].value

        # Python 3.6+ dicts are ordered by insertion
        # so this means the MRO defines the ordering of keys
        # in an inheritance chain
        columns = {
            key: attrs['__slots__'][key] for key in (slot_ordering or attrs['__slots__'])
        }
        for cls in bases:
            if hasattr(cls, '_columns'):
                cols = cls._columns
                if isinstance(cols, ReadonlyClassVariable):
                    cols = cols.value
                for key in cols:
                    columns[key] = cols[key]

        setter_template = SETTER_TEMPLATE
        getter_template = GETTER_TEMPLATE
        config = {}
        field_setters = []
        field_getters = []

        for key, value in tuple(kwargs.items()):
            if key in cls.mixins and (value is True or isinstance(value, type)):
                mixin_cls, overrides = cls.mixins[key]
                if overrides.get('promoted'):
                    bases = (mixin_cls,) + bases
                else:
                    bases += (mixin_cls,)
                if overrides:
                    if 'setter_template' in overrides:
                        setter_template = overrides['setter_template']
                    if 'getter_template' in overrides:
                        getter_template = overrides['getter_template']
                del kwargs[key]
                config[key] = value
                if hasattr(mixin_cls, 'preprocess'):
                    mixin_cls.preprocess(class_name, columns, attrs)
                if hasattr(mixin_cls, 'FIELD_SETTER_WRAPPER'):
                    setter_template = setter_template.replace(
                        '{setter_block}',
                        textwrap.indent(mixin_cls.FIELD_SETTER_WRAPPER, ' ' * 12).lstrip())
                if hasattr(mixin_cls, 'FIELD_SETTER'):
                    field_setters.append(mixin_cls.FIELD_SETTER)
                if hasattr(mixin_cls, 'FIELD_GETTER'):
                    field_getters.append(mixin_cls.FIELD_GETTER)
        if len(field_setters) > 1:
            raise ValueError('Only one field setter macro allowed at any time')
        if field_setters:
            setter_template = setter_template.replace('{setter_block}', field_setters[0])
        else:
            setter_template = setter_template.replace('{setter_block}', SETTER_BLOCK)
        if len(field_getters) > 1:
            raise ValueError('Only one field setter macro allowed at any time')
        if field_getters:
            getter_template = getter_template.replace('{getter_block}', field_getters[0])
        else:
            getter_template = getter_template.replace('{getter_block}', GETTER_BLOCK)

        if kwargs:
            raise ValueError('Unknown kwargs {}'.format(kwargs))

        attrs['_columns'] = ReadonlyClassVariable(columns)
        attrs['_configuration'] = ConfigDefinition(**config)
        ns_globals = {'Union': Union, 'NoneType': type(None)}
        for key, value in attrs['__slots__'].items():
            if key[0] == '_':
                continue
            attrs['__slots__'][f'_{key}'] = value
            del attrs['__slots__'][key]
            ns = {}
            exec(getter_template.format(key=key), ns_globals, ns)
            exec(setter_template.format(key=key), ns_globals, ns)
            attrs[key] = property(ns['make_getter'](value), ns['make_setter'](value, fast))
        return super().__new__(klass, class_name, bases, attrs)


Delta = namedtuple('Delta', ['state', 'old', 'new', 'index'])
LoggedDelta = namedtuple('LoggedDelta', ['timestamp', 'key', 'delta'])


class History(object):
    __slots__ = ()
    FIELD_SETTER_WRAPPER = ReadonlyClassVariable('''
old_value = self.{key}
{setter_block}
self._record_change('{key}', old_value, val)
'''.strip())

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

Atomic.register_class_mixin('history', History)


class Flags(IntEnum):
    IN_CONSTRUCTOR = 1
    DEFAULTS_SET = 2
    INITIALIZED = 4


class Base(metaclass=Atomic):
    __slots__ = (
        '_changes', '_changed_keys', '_flags', '_changed_index',
        '_value', '_struct_def',)

    def __init__(self, **kwargs):
        self._flags = Flags.IN_CONSTRUCTOR
        self._changed_index = -1
        if self._configuration.history:
            self._changed_index = 0
            t_s = time.time()
            self._changes = {
                key: [Delta('default', None, getattr(self, key, None), 0)] for key in self._columns
            }
            self._changed_keys = [(key, t_s) for key in self._columns]
            self._changed_index += len(self._changed_keys)
        self._flags |= Flags.DEFAULTS_SET
        initializer_keys = self._columns.keys() & kwargs.keys()
        for key in initializer_keys:
            setattr(self, key, kwargs[key])
            self._changed_index += 1

        if kwargs.keys() - self._columns.keys():
            fields = ', '.join(kwargs.keys() - self._columns.keys())
            raise ValueError(f'Unrecognized fields {fields}')
        self._flags = Flags.INITIALIZED
        super().__init__()

import cffi

CSTRUCT_TEMPLATE = '''
struct {
%(fields)s
}
'''.strip()

UNION_TEMPLATE = '''
union {
%(value)s
} %(name)s;
'''.strip()


class CStruct:
    __slots__ = ()
    _ffi = ReadonlyClassVariable(cffi.FFI())
    FIELD_GETTER = ReadonlyClassVariable('return self._value.{key}')
    FIELD_SETTER = ReadonlyClassVariable('self._value.{key} = val')

    def __init__(self, **kwargs):
        self._value = self._ffi.new(f'py_{self.__class__.__name__.lower()}*')
        super().__init__(**kwargs)

    @classmethod
    def preprocess(cls, class_name, columns, namespace, indent=0):
        template = CSTRUCT_TEMPLATE
        fields = []
        stack = list(columns)
        while stack:
            key = stack.pop(0)
            value = columns[key]
            assert (hasattr(value, '__origin__') and
                    value.__origin__ is Union) or isinstance(value, (dict, str))
            if isinstance(value, str):
                if value.endswith(']'):
                    value, array = value.split('[', 1)
                    array = array[:-1]
                    key = f'{key}[{array}]'
                fields.append(f'{value} {key};')
            if isinstance(value, dict):
                value = cls.preprocess(None, value, {}, indent=indent+1)
                fields.append(f'{value} {key}')
            if hasattr(value, '__origin__') and value.__origin__ is Union:
                value = ['{1} {0};'.format(
                    x.__name__, x.__supertype__) for x in value._subs_tree()[1:]]
                assert value
                value = textwrap.indent('\n'.join(value), ' ' * 4 * (indent + 1))
                fields.append(
                    UNION_TEMPLATE % {
                        'value': value, 'name': key
                    })
        fields = textwrap.indent('\n'.join(fields), ' ' * (indent + 1) * 4)
        struct_def = template % {
                'fields': fields
            }
        if indent:
            struct_def = textwrap.indent(struct_def, ' ' * indent * 4)
        if not indent:
            struct_def = 'typedef {} py_{name};'.format(struct_def, name=class_name.lower())
            namespace['_struct_def'] = struct_def
            cls._ffi.cdef(struct_def)
        return struct_def

    def __bytes__(self):
        return self.to_bytes()

    def to_bytes(self):
        buf = self._ffi.buffer(self._value)
        return buf[:]

    def from_bytes(self, val):
        assert isinstance(val, bytes), 'Must be bytes!'
        assert len(val) == self._ffi.sizeof(f'py_{self.__class__.__name__.lower()}'), \
            'must have same sizeof'
        self._ffi.memmove(self._value, val, len(val))


Atomic.register_class_mixin(
    'cstruct',
    CStruct, promoted=True, setter_template=C_DATA_SETTER_TEMPLATE)
