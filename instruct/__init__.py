from collections import Mapping, namedtuple, UserDict
from typing import Union
import time
from enum import IntEnum
from jinja2 import Environment, PackageLoader
from .about import __version__
__version__  # Silence unused import warning.

NoneType = type(None)

env = Environment(loader=PackageLoader(__name__, 'templates'))


class AttrsDict(UserDict):
    def __getattr__(self, key):
        try:
            return self.data[key]
        except KeyError:
            self.data[key] = None
            return None


class ReadOnly:
    def __init__(self, value):
        self.value = value

    def __get__(self, obj, objtype=None):
        return self.value

    def __set__(self, obj, val):
        raise NotImplementedError


def make_fast_clear(fields, set_block):
    set_block = set_block.format(key='%(key)s')
    code_template = env.get_template('fast_clear.jinja').render(
        fields=fields, setter_variable_template=set_block)
    return code_template


def make_fast_eq(fields):
    code_template = env.get_template('fast_eq.jinja').render(fields=fields)
    return code_template


class Atomic(type):
    __slots__ = ()
    REGISTRY = ReadOnly(set())
    MIXINS = ReadOnly({})

    @classmethod
    def register_mixin(cls, name, klass):
        cls.MIXINS[name] = klass

    def __new__(klass, class_name, bases, attrs, fast=None, **mixins):
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
        columns = {}
        derived_classes = {}
        for key, value in attrs['__slots__'].items():
            if isinstance(value, dict):
                value = type('{}'.format(key.capitalize()), bases, {'__slots__': value})
                derived_classes[key] = value
                attrs['__slots__'][key] = value
            columns[key] = value

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

        for cls in bases:
            if hasattr(cls, '__slots__') and isinstance(cls.__slots__, dict):
                for key, value in cls.__slots__.items():
                    columns[key] = value
            if hasattr(cls, 'setter_wrapper'):
                setter_wrapper.append(cls.setter_wrapper)
            if hasattr(cls, '__getter_template__'):
                getter_templates.append(cls.__getter_template__)
            if hasattr(cls, '__setter_template__'):
                setter_templates.append(cls.__setter_template__)
        try:
            setter_var_template = attrs.get('__setter_template__', setter_templates[0])
            getter_var_template = attrs.get('__getter_template__', getter_templates[0])
        except IndexError:
            raise ValueError('You must define both __getter_template__ and __setter_template__')

        local_setter_var_template = setter_var_template.format(key='{{field_name}}')
        local_getter_var_template = getter_var_template.format(key='{{field_name}}')
        for index, template_name in enumerate(setter_wrapper):
            template = env.get_template(template_name)
            local_setter_var_template = template.render(
                field_name='{{field_name}}',
                setter_variable_template=local_setter_var_template)
        local_setter_var_template = local_setter_var_template.replace('{{field_name}}', '%(key)s')
        local_getter_var_template = local_getter_var_template.replace('{{field_name}}', '%(key)s')

        setter_template = env.get_template('setter.jinja')
        getter_template = env.get_template('getter.jinja')

        attrs['_columns'] = ReadOnly(columns)
        conf = AttrsDict(**mixins)
        conf['fast'] = fast

        attrs['_configuration'] = ReadOnly(conf)
        ns_globals = {'Union': Union, 'NoneType': type(None), 'Flags': Flags}
        for key, value in attrs['__slots__'].items():
            if value in klass.REGISTRY:
                derived_classes[key] = value
            if key[0] == '_':
                continue
            attrs['__slots__'][f'_{key}'] = value
            del attrs['__slots__'][key]
            ns = {}

            getter_code = getter_template.render(
                field_name=key, get_variable_template=local_getter_var_template)
            setter_code = setter_template.render(
                field_name=key, setter_variable_template=local_setter_var_template)

            exec(getter_code, ns_globals, ns)
            exec(setter_code, ns_globals, ns)
            attrs[key] = property(
                ns['make_getter'](value),
                ns['make_setter'](value, fast, derived_classes.get(key)))
        exec(make_fast_eq(tuple(columns)), ns_globals, ns_globals)
        exec(make_fast_clear(tuple(columns), local_setter_var_template), ns_globals, ns_globals)
        attrs['__eq__'] = ns_globals['__eq__']
        attrs['clear'] = ns_globals['clear']

        new_cls = super().__new__(klass, class_name, bases, attrs)
        klass.REGISTRY.add(new_cls)
        return new_cls

Delta = namedtuple('Delta', ['state', 'old', 'new', 'index'])
LoggedDelta = namedtuple('LoggedDelta', ['timestamp', 'key', 'delta'])


class Undefined(object):
    def __repr__(self):
        return 'Undefined'

UNDEFINED = Undefined()


class History(object):
    __slots__ = ()
    setter_wrapper = 'history-setter-wrapper.jinja'

    def clear(self, fields):
        self._changed_index = 0
        t_s = time.time()
        self._changes = {
            key: [Delta('default', UNDEFINED, getattr(self, key), 0)] for key in self._columns
        }
        self._changed_keys = [(key, t_s) for key in self._columns]
        self._changed_index += len(self._changed_keys)
        super().clear(fields)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if self._flags & Flags.IN_CONSTRUCTOR and key in self._columns:
            self._changed_index += 1

    def _record_change(self, key, old_value, new_value):
        if old_value == new_value:
            return
        if self._flags & Flags.DISABLE_HISTORY:
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
            keys = self._columns.keys()
        self._flags |= Flags.DISABLE_HISTORY
        for key in keys:
            first_changes = self._changes[key][:2]
            self._changes[key][:2] = first_changes

            val = first_changes[0].new  # Constructor default, defaults to None
            if len(first_changes) == 2:
                assert first_changes[1].state == 'initialized'
                val = first_changes[1].new  # Use the initialized default
            setattr(self, key, val)
        self._flags &= (self._flags ^ Flags.DISABLE_HISTORY)

    def list_changes(self):
        key_counter = {}
        for key, delta_time in self._changed_keys:
            if key not in key_counter:
                key_counter[key] = 0
            index = key_counter[key]
            delta = self._changes[key][index]

            yield LoggedDelta(delta_time, key, delta)
            key_counter[key] += 1

Atomic.register_mixin('history', History)


class Flags(IntEnum):
    IN_CONSTRUCTOR = 1
    DEFAULTS_SET = 2
    INITIALIZED = 4
    DISABLE_HISTORY = 8


class Base(metaclass=Atomic):
    __slots__ = ('_changes', '_changed_keys', '_flags', '_changed_index',)
    __setter_template__ = ReadOnly('self._{key} = val')
    __getter_template__ = ReadOnly('return self._{key}')

    def __new__(cls, *args, **kwargs):
        result = super().__new__(cls)
        result._flags = 0
        return result

    def __init__(self, **kwargs):
        self._flags |= Flags.IN_CONSTRUCTOR
        fields = []
        # about 400ms/1k
        for key in self._columns:
            if getattr(self, key, UNDEFINED) is UNDEFINED:
                fields.append(key)
        self.clear(fields)  # 400ms/1k
        self._flags |= Flags.DEFAULTS_SET
        for key in self._columns.keys() & kwargs.keys():
            value = kwargs[key]
            setattr(self, key, value)

        if kwargs.keys() - self._columns.keys():
            fields = ', '.join(kwargs.keys() - self._columns.keys())
            raise ValueError(f'Unrecognized fields {fields}')
        self._flags = Flags.INITIALIZED

    def clear(self, fields):
        pass


