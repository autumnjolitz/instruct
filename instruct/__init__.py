import os
import time
import tempfile
import logging
from collections import Mapping, namedtuple, UserDict
from typing import Union
from enum import IntEnum

from jinja2 import Environment, PackageLoader

from .about import __version__
__version__  # Silence unused import warning.

NoneType = type(None)

logger = logging.getLogger(__name__)
env = Environment(loader=PackageLoader(__name__, 'templates'))


class AttrsDict(UserDict):
    def __getattr__(self, key):
        try:
            return self.data[key]
        except KeyError:
            self.data[key] = None
            return None


class ReadOnly:
    __slots__ = ('value',)

    def __init__(self, value):
        self.value = value

    def __get__(self, obj, objtype=None):
        return self.value


def make_fast_clear(fields, set_block):
    set_block = set_block.format(key='%(key)s')
    code_template = env.get_template('fast_clear.jinja').render(
        fields=fields, setter_variable_template=set_block)
    return code_template


def make_fast_eq(fields):
    code_template = env.get_template('fast_eq.jinja').render(fields=fields)
    return code_template


def make_fast_iter(fields):
    code_template = env.get_template('fast_iter.jinja').render(fields=fields)
    return code_template


def make_fast_new(fields, defaults_var_template):
    defaults_var_template = env.from_string(defaults_var_template).render(fields=fields)
    code_template = env.get_template('fast_new.jinja').render(
        fields=fields, defaults_var_template=defaults_var_template)
    return code_template


def make_defaults(fields, defaults_var_template):
    defaults_var_template = env.from_string(defaults_var_template).render(fields=fields)
    code = env.from_string('''
def _set_defaults(self):
    result = self
    {{item|indent(4)}}
    super(self.__class__, self)._set_defaults()
    ''').render(item=defaults_var_template)
    return code


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
        defaults_templates = []

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
            if hasattr(cls, '__defaults_init__'):
                defaults_templates.append(cls.__defaults_init__)
        try:
            setter_var_template = attrs.get('__setter_template__', setter_templates[0])
            getter_var_template = attrs.get('__getter_template__', getter_templates[0])
            defaults_var_template = attrs.get('__defaults_init__', defaults_templates[0])
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
        field_names = []

        for key, value in attrs['__slots__'].items():
            if value in klass.REGISTRY:
                derived_classes[key] = value
            if key[0] == '_':
                continue
            field_names.append(key)
            attrs['__slots__'][f'_{key}'] = value
            del attrs['__slots__'][key]
            ns = {}

            getter_code = getter_template.render(
                field_name=key, get_variable_template=local_getter_var_template)
            setter_code = setter_template.render(
                field_name=key, setter_variable_template=local_setter_var_template)
            filename = '<getter-setter>'
            if os.environ.get('INSTRUCT_DEBUG_CODEGEN', '').lower().startswith(
                    ('1', 'true', 'yes', 'y')):
                with tempfile.NamedTemporaryFile(
                        delete=False, mode='w',
                        prefix=f'{class_name}-{key}', suffix='.py', encoding='utf8') as fh:
                    fh.write(getter_code)
                    fh.write('\n')
                    fh.write(setter_code)
                    filename = fh.name
                    logger.debug(f'{class_name}.{key} at {filename}')

            code = compile('{}\n{}'.format(getter_code, setter_code), filename, mode='exec')
            exec(code, ns_globals, ns)

            attrs[key] = property(
                ns['make_getter'](value),
                ns['make_setter'](value, fast, derived_classes.get(key)))
        exec(compile(
            make_fast_eq(tuple(columns)), '<make_fast_eq>', mode='exec'), ns_globals, ns_globals)
        exec(compile(
            make_fast_clear(tuple(columns), local_setter_var_template),
            '<make_fast_clear>', mode='exec'), ns_globals, ns_globals)
        exec(compile(
            make_fast_iter(tuple(columns)),
            '<make_fast_iter>', mode='exec'), ns_globals, ns_globals)
        exec(compile(
            make_defaults(tuple(columns), defaults_var_template),
            '<make_defaults>', mode='exec'), ns_globals, ns_globals)
        if '__new__' not in attrs:
            exec(compile(
                make_fast_new(field_names, defaults_var_template),
                '<make_fast_new>', mode='exec'), ns_globals, ns_globals)
            attrs['__new__'] = ns_globals['__new__']

        attrs['__iter__'] = ns_globals['__iter__']
        attrs['__eq__'] = ns_globals['__eq__']
        attrs['_set_defaults'] = ns_globals['_set_defaults']
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

    def __init__(self, **kwargs):
        self._changed_index = 0
        t_s = time.time()
        self._changes = {
            key: [Delta('default', UNDEFINED, value, 0)] for key, value in self
        }
        self._changed_keys = [(key, t_s) for key in self._columns]
        self._changed_index += len(self._changed_keys)
        super().__init__(**kwargs)

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
            if getattr(self, key) != val:
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

DEFAULTS = '''{%- for field in fields %}
result._{{field}} = None
{%- endfor %}
'''


class IBase(object):
    def clear(self, fields=None):
        pass


class Base(IBase, metaclass=Atomic):
    __slots__ = ('_changes', '_changed_keys', '_flags', '_changed_index',)
    __setter_template__ = ReadOnly('self._{key} = val')
    __getter_template__ = ReadOnly('return self._{key}')
    __defaults_init__ = ReadOnly(DEFAULTS)

    def __new__(cls, *args, **kwargs):
        result = super().__new__(cls)
        result._flags = 0
        return result

    def __init__(self, **kwargs):
        self._flags |= Flags.IN_CONSTRUCTOR
        self._flags |= Flags.DEFAULTS_SET
        for key in self._columns.keys() & kwargs.keys():
            value = kwargs[key]
            setattr(self, key, value)

        if kwargs.keys() - self._columns.keys():
            fields = ', '.join(kwargs.keys() - self._columns.keys())
            raise ValueError(f'Unrecognized fields {fields}')
        self._flags = Flags.INITIALIZED
