import os
import time
import tempfile
import logging
from collections import namedtuple, UserDict
from collections.abc import Mapping
import typing
from enum import IntEnum


import inflection
from jinja2 import Environment, PackageLoader

from .about import __version__
from .typedef import parse_typedef
__version__  # Silence unused import warning.

NoneType = type(None)

logger = logging.getLogger(__name__)
env = Environment(loader=PackageLoader(__name__, 'templates'))


def _convert_exception_to_json(item: Exception):
    assert isinstance(item, Exception)
    if hasattr(item, 'to_json'):
        return item.to_json()
    return {
        'type': inflection.titleize(type(item).__name__),
        'message': str(item)
    }


class ClassCreationFailed(ValueError, TypeError):
    def __init__(self, message, *errors):
        assert len(errors) > 0, 'Must have varargs of errors!'
        self.errors = errors
        self.message = message
        super().__init__(message, *errors)

    def to_json(self):
        stack = list(self.errors)
        results = []
        while stack:
            item = stack.pop(0)
            if hasattr(item, 'errors'):
                stack.extend(item.to_json())
                continue
            item = _convert_exception_to_json(item)
            item['parent_message'] = self.message
            item['parent_type'] = inflection.titleize(type(self).__name__)
            results.append(item)
        return tuple(results)


class AttrsDict(UserDict):
    def __getattr__(self, key):
        try:
            return self.data[key]
        except KeyError:
            self.data[key] = None
            return None


class FrozenMapping:
    __slots__ = ('_value',)

    def __init__(self, value):
        self._value = value

    def __getitem__(self, key):
        return self._value[key]

    def __len__(self, key):
        return len(self._value)

    def __contains__(self, key):
        return key in self._value


class ReadOnly:
    __slots__ = ('value',)

    def __init__(self, value):
        self.value = value

    def __get__(self, obj, objtype=None):
        return self.value


def make_fast_clear(fields, set_block, class_name):
    set_block = set_block.format(key='%(key)s')
    code_template = env.get_template('fast_clear.jinja').render(
        fields=fields, setter_variable_template=set_block, class_name=class_name)
    return code_template


def make_fast_getitem(fields, class_name):
    code_template = env.get_template('fast_getitem.jinja').render(
        fields=fields, class_name=class_name)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args)

    def __new__(klass, class_name, bases, attrs, fast=None, skip=None, **mixins):
        if '__coerce__' in attrs and not isinstance(attrs['__coerce__'], ReadOnly):
            attrs['__coerce__'] = ReadOnly(attrs['__coerce__'])

        if skip:
            attrs['_metaclass_skip'] = ReadOnly(True)
            cls = super().__new__(klass, class_name, bases, attrs)
            if not getattr(cls, '__hash__', None):
                cls.__hash__ = object.__hash__
            assert cls.__hash__ is not None
            return cls
        attrs['_metaclass_skip'] = ReadOnly(False)
        if '__slots__' not in attrs:
            raise TypeError(
                f'You must define __slots__ for {class_name} to constrain the typespace')
        if not isinstance(attrs['__slots__'], Mapping):
            if isinstance(attrs['__slots__'], tuple):
                # Classes with tuples in them are assumed to be
                # data class definitions (i.e. supporting things like a change log)
                attrs['_data_class'] = ReadOnly(None)
                slots = attrs.pop('__slots__')
                attrs['__slots__'] = ()
                attrs['_support_columns'] = ReadOnly(tuple(slots))
                new_cls = super().__new__(klass, class_name, bases, attrs)
                # import inspect
                # print(new_cls, slots, new_cls.__slots__, bases, class_name)
                # data_class_cell.value = type(
                #     f'{class_name}Support', (new_cls,), {'__slots__': slots})
                return new_cls
            raise TypeError(
                f'The __slots__ definition for {class_name} must be a mapping or empty tuple!')

        if 'fast' in attrs:
            fast = attrs.pop('fast')
        if fast is None:
            fast = not __debug__

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
        support_columns = []

        properties = [name for name, val in attrs.items() if isinstance(val, property)]

        for cls in bases:
            if hasattr(cls, '__slots__') and cls.__slots__ != () \
                    and not issubclass(type(cls), Atomic):
                # Because we cannot control the circumstances of a base class's construction
                # and it has __slots__, which will destroy our multiple inheritance support,
                # so we should just refuse to work.
                #
                # Please note that ``__slots__ = ()`` classes work perfectly and are not
                # subject to this limitation.
                raise TypeError(
                    f'Multi-slot classes (like {cls.__name__}) must be defined '
                    'with `metaclass=Atomic`. Mixins with empty __slots__ are not subject to '
                    'this restriction.')
            if not getattr(cls, '_metaclass_skip', False):
                assert getattr(cls, '__slots__', None) == (), \
                    f'You must define {cls.__name__}.__slots__ = ()'
            if hasattr(cls, '_columns'):
                for key, value in cls._columns.items():
                    columns[key] = value
            if hasattr(cls, '_support_columns'):
                support_columns.extend(cls._support_columns)
            if hasattr(cls, 'setter_wrapper'):
                setter_wrapper.append(cls.setter_wrapper)
            if hasattr(cls, '__getter_template__'):
                getter_templates.append(cls.__getter_template__)
            if hasattr(cls, '__setter_template__'):
                setter_templates.append(cls.__setter_template__)
            if hasattr(cls, '__defaults_init__'):
                defaults_templates.append(cls.__defaults_init__)
            for key in dir(cls):
                value = getattr(cls, key)
                if isinstance(value, property):
                    properties.append(key)
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
        column_types = {}
        attrs['_column_types'] = ReadOnly(FrozenMapping(column_types))
        attrs['_support_columns'] = tuple(support_columns)
        conf = AttrsDict(**mixins)
        conf['fast'] = fast
        attrs['_properties'] = frozenset(properties)

        attrs['_configuration'] = ReadOnly(conf)
        ns_globals = {'NoneType': type(None), 'Flags': Flags, 'typing': typing}
        field_names = []
        listeners = {}  # mapping of the setter -> function_name to be called with old, new vals
        for key, value in attrs.items():
            if callable(value) and hasattr(value, '_fields'):
                for field in value._fields:
                    try:
                        listeners[field].append(key)
                    except KeyError:
                        listeners[field] = [key]

        for key, value in tuple(attrs['__slots__'].items()):
            if value in klass.REGISTRY:
                derived_classes[key] = value
            if key[0] == '_':
                continue
            field_names.append(key)
            attrs['__slots__'][f'_{key}'] = value
            del attrs['__slots__'][key]
            ns = {}
            coerce_types = coerce_func = None
            if '__coerce__' in attrs and key in attrs['__coerce__'].value:
                coerce_types, coerce_func = attrs['__coerce__'].value[key]
            getter_code = getter_template.render(
                field_name=key, get_variable_template=local_getter_var_template)
            setter_code = setter_template.render(
                field_name=key, setter_variable_template=local_setter_var_template,
                on_sets=listeners.get(key), has_coercion=coerce_types is not None)
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

            types_to_check = parse_typedef(value)
            column_types[key] = types_to_check
            attrs[key] = property(
                ns['make_getter'](value),
                ns['make_setter'](
                    value, fast, derived_classes.get(key), types_to_check,
                    coerce_types, coerce_func))
        # Support columns are left as-is for slots
        support_columns = tuple(support_columns)
        ns_globals[class_name] = ReadOnly(None)
        exec(compile(
            make_fast_eq(columns), '<make_fast_eq>', mode='exec'), ns_globals, ns_globals)
        exec(compile(
            make_fast_clear(columns, local_setter_var_template, class_name),
            '<make_fast_clear>', mode='exec'), ns_globals, ns_globals)
        exec(compile(
            make_fast_getitem(columns, class_name),
            '<make_fast_getitem>', mode='exec'), ns_globals, ns_globals)
        exec(compile(
            make_fast_iter(columns),
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
        attrs['__getitem__'] = ns_globals['__getitem__']

        slots = attrs.pop('__slots__')

        attrs['_data_class'] = dc = ReadOnly(None)
        attrs['__slots__'] = ()
        attrs['_parent'] = parent_cell = ReadOnly(None)
        new_cls = super().__new__(klass, class_name, bases, attrs)
        ns_globals[class_name].value = new_cls
        ns_globals[class_name] = new_cls
        dataclass_template = env.get_template('data_class.jinja').render(
            class_name=class_name,
            slots=repr(tuple('_{}'.format(key) for key in columns) + support_columns))
        exec(compile(
            dataclass_template,
            '<dcs>', mode='exec'), ns_globals, ns_globals)
        dc.value = ns_globals[f'_{class_name}']
        parent_cell.value = new_cls
        klass.REGISTRY.add(new_cls)
        return new_cls


Delta = namedtuple('Delta', ['state', 'old', 'new', 'index'])
LoggedDelta = namedtuple('LoggedDelta', ['timestamp', 'key', 'delta'])


class Undefined(object):
    SINGLETON = None

    def __new__(cls):
        if Undefined.SINGLETON is not None:
            return Undefined.SINGLETON
        Undefined.SINGLETON = super().__new__(cls)
        return Undefined.SINGLETON

    def __repr__(self):
        return 'Undefined'


UNDEFINED = Undefined()


class History(metaclass=Atomic):
    __slots__ = ('_changes', '_changed_keys', '_changed_index',)
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


def add_event_listener(*fields):
    def wrapper(func):
        func._fields = \
            getattr(func, '_fields', ()) + fields
        return func
    return wrapper


def load_cls(cls, args, kwargs):
    return cls(*args, **kwargs)


class Base(metaclass=Atomic, skip=True):
    __slots__ = ('_flags',)
    __setter_template__ = ReadOnly('self._{key} = val')
    __getter_template__ = ReadOnly('return self._{key}')
    __defaults_init__ = ReadOnly(DEFAULTS)

    @classmethod
    def _create_invalid_type(cls, field_name, val, val_type, types_required):
        if len(types_required) > 1:
            if len(types_required) == 2:
                expects = 'either an {.__name__} or {.__name__}'.format(val_type)
            else:
                expects = f'either an {"".join(x.__name__) for x in types_required[:-1]} '\
                          f'or a {types_required[-1].__name__}'
        else:
            expects = f'a {val_type.__name__}'
        return TypeError(
            f'Unable to set {field_name} to {val!r} ({val_type.__name__}). {field_name} expects '
            f'{expects}'
        )

    def keys(self):
        return self._columns.keys()

    def __new__(cls, *args, **kwargs):
        # Get the edge class that has all the __slots__ defined
        cls = cls._data_class
        result = super().__new__(cls)
        result._flags = 0
        assert '__dict__' not in dir(result)
        return result

    def to_json(self) -> dict:
        '''
        Returns a dictionary compatible with json.dumps(...)
        '''
        result = {}
        for key, value in self:
            # Support nested daos
            if hasattr(value, 'to_json'):
                value = value.to_json()
            # Date/datetimes
            if hasattr(value, 'isoformat'):
                value = value.isoformat()
            result[key] = value
        return result

    def __reduce__(self):
        values = dict(self)
        this_cls, support_cls, *_ = self.__class__.__mro__
        return load_cls, (support_cls, (), values)

    def __init__(self, **kwargs):
        self._flags |= Flags.IN_CONSTRUCTOR
        self._flags |= Flags.DEFAULTS_SET
        errors = []
        for key in self._columns.keys() & kwargs.keys():
            value = kwargs[key]
            try:
                setattr(self, key, value)
            except Exception as e:
                errors.append(e)
        for key in self._properties & kwargs.keys():
            value = kwargs[key]
            try:
                setattr(self, key, value)
            except Exception as e:
                errors.append(e)
        if kwargs.keys() - (self._columns.keys() | self._properties):
            fields = ', '.join(kwargs.keys() - self._columns.keys())
            errors.append(ValueError(f'Unrecognized fields {fields}'))
        if errors:
            raise ClassCreationFailed(
                f'Unable to construct, encountered {len(errors)} '
                f'error{"s" if len(errors) > 1 else ""}', *errors)
        self._flags = Flags.INITIALIZED

    def clear(self, fields=None):
        pass
