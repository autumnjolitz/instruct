import os
import time
import tempfile
import logging
from collections import namedtuple, UserDict
from collections.abc import Mapping, Sequence, ValuesView, KeysView, ItemsView as _ItemsView
import typing
import types
from enum import IntEnum
from importlib import import_module


import inflection
from jinja2 import Environment, PackageLoader

from .about import __version__
from .typedef import parse_typedef
__version__  # Silence unused import warning.

NoneType = type(None)

logger = logging.getLogger(__name__)
env = Environment(loader=PackageLoader(__name__, 'templates'))
env.globals['tuple'] = tuple
env.globals['repr'] = repr


class ItemsView(_ItemsView):
    __slots__ = ()

    def __iter__(self):
        yield from self._mapping


def _convert_exception_to_json(item):
    assert isinstance(item, Exception), \
        f'item {item!r} ({type(item)}) is not an exception!'
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

    def keys(self):
        return frozenset(self._value.keys())

    def __init__(self, value):
        self._value = value

    def __getitem__(self, key):
        return self._value[key]

    def __len__(self):
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


def make_fast_getitem(fields, class_name, get_variable_template, set_variable_template):
    code_template = env.get_template('fast_getitem.jinja').render(
        fields=fields, class_name=class_name, get_variable_template=get_variable_template,
        set_variable_template=set_variable_template)
    return code_template


def make_fast_eq(fields):
    code_template = env.get_template('fast_eq.jinja').render(fields=fields)
    return code_template


def make_fast_iter(fields):
    code_template = env.get_template('fast_iter.jinja').render(fields=fields)
    return code_template


def make_set_get_states(fields):
    code_template = env.get_template('raw_get_set_state.jinja').render(fields=fields)
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


def insert_class_closure(klass, function, *, memory=None):
    Derived = None
    if memory is not None:
        try:
            Derived = memory[klass]
        except KeyError:
            Derived = None

    code = function.__code__
    code = types.CodeType(
        code.co_argcount, code.co_kwonlyargcount, code.co_nlocals,
        code.co_stacksize, code.co_flags, code.co_code, code.co_consts, code.co_names,
        code.co_varnames, code.co_filename, code.co_name, code.co_firstlineno,
        code.co_lnotab, code.co_freevars + ('__class__',), code.co_cellvars)

    if Derived is None:
        class Derived(klass):
            __slots__ = ()

            def dummy(self):
                return __class__  # noqa

        if memory is not None:
            memory[klass] = Derived

    class_cell = Derived.dummy.__closure__[0]
    class_cell.cell_contents = klass
    current_closure = function.__closure__
    if current_closure is None:
        current_closure = ()
    new_globals = globals()
    if function.__module__ and function.__module__ != '__main__':
        module = import_module(function.__module__)
        new_globals = {**globals(), **vars(module)}
    return types.FunctionType(
        code, new_globals, function.__name__,
        function.__defaults__, current_closure + (class_cell,))


class Atomic(type):
    __slots__ = ()
    REGISTRY = ReadOnly(set())
    MIXINS = ReadOnly({})

    @classmethod
    def register_mixin(cls, name, klass):
        cls.MIXINS[name] = klass

    def __init__(self, *args, **kwargs):
        # We use kwargs to pass to __new__ and therefore we need
        # to filter it out of the `type(...)` call
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
            columns[key] = parse_typedef(value)

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

        column_types = {}

        properties = [name for name, val in attrs.items() if isinstance(val, property)]

        for cls in bases:
            if hasattr(cls, '_column_types'):
                column_types.update(cls._column_types)

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
        all_coercions = {}
        attrs['_column_types'] = ReadOnly(FrozenMapping(column_types))
        attrs['_all_coercions'] = ReadOnly(FrozenMapping(all_coercions))
        attrs['_support_columns'] = tuple(support_columns)
        conf = AttrsDict(**mixins)
        conf['fast'] = fast
        attrs['_properties'] = properties = frozenset(properties)

        attrs['_configuration'] = ReadOnly(conf)
        ns_globals = {'NoneType': type(None), 'Flags': Flags, 'typing': typing}
        field_names = []
        _class_cell_fixups = []
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
            attrs['__slots__'][f'_{key}_'] = value

            del attrs['__slots__'][key]
            ns = {}
            coerce_types = coerce_func = None
            if '__coerce__' in attrs and key in attrs['__coerce__'].value:
                coerce_types, coerce_func = attrs['__coerce__'].value[key]
            coerce_types = parse_typedef(coerce_types)
            all_coercions[key] = (coerce_types, coerce_func)
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
            new_property = property(
                ns['make_getter'](value),
                ns['make_setter'](
                    value, fast, derived_classes.get(key), types_to_check,
                    coerce_types, coerce_func))

            if key in properties:
                current_prop = attrs[key]
                if not all((current_prop.fget, current_prop.fset)):
                    if not current_prop.fget:
                        new_property = current_prop.getter(new_property.fget)
                    if not current_prop.fset:
                        new_property = current_prop.setter(new_property.fset)
                else:
                    new_property = current_prop
            _class_cell_fixups.append((key, new_property))
            attrs[key] = new_property
        # Support columns are left as-is for slots
        support_columns = tuple(support_columns)
        ns_globals[class_name] = ReadOnly(None)
        exec(compile(
            make_fast_eq(columns), '<make_fast_eq>', mode='exec'), ns_globals, ns_globals)
        exec(compile(
            make_fast_clear(columns, local_setter_var_template, class_name),
            '<make_fast_clear>', mode='exec'), ns_globals, ns_globals)
        _class_cell_fixups.append(('clear', ns_globals['clear']))
        exec(compile(
            make_fast_getitem(
                columns, class_name, local_getter_var_template, local_setter_var_template),
            '<make_fast_getitem>', mode='exec'), ns_globals, ns_globals)
        exec(compile(
            make_fast_iter(columns),
            '<make_fast_iter>', mode='exec'), ns_globals, ns_globals)
        exec(compile(
            make_set_get_states(columns),
            '<make_set_get_states>', mode='exec'), ns_globals, ns_globals)
        exec(compile(
            make_defaults(tuple(columns), defaults_var_template),
            '<make_defaults>', mode='exec'), ns_globals, ns_globals)
        if '__new__' not in attrs:
            exec(compile(
                make_fast_new(field_names, defaults_var_template),
                '<make_fast_new>', mode='exec'), ns_globals, ns_globals)
            attrs['__new__'] = ns_globals['__new__']
            _class_cell_fixups.append(('__new__', ns_globals['__new__']))

        attrs['__iter__'] = ns_globals['__iter__']
        attrs['__getstate__'] = ns_globals['__getstate__']
        attrs['__setstate__'] = ns_globals['__setstate__']
        attrs['__eq__'] = ns_globals['__eq__']
        attrs['_set_defaults'] = ns_globals['_set_defaults']
        attrs['clear'] = ns_globals['clear']
        attrs['__getitem__'] = ns_globals['__getitem__']
        attrs['__setitem__'] = ns_globals['__setitem__']

        slots = attrs.pop('__slots__')

        attrs['_data_class'] = attrs[f'_{class_name}'] = dc = ReadOnly(None)
        attrs['__slots__'] = ()
        attrs['_parent'] = parent_cell = ReadOnly(None)
        support_cls = super().__new__(klass, class_name, bases, attrs)

        cache = {}
        for prop_name, value in _class_cell_fixups:
            if isinstance(value, property):
                value = property(
                    insert_class_closure(support_cls, value.fget, memory=cache),
                    insert_class_closure(support_cls, value.fset, memory=cache),
                )
            else:
                value = insert_class_closure(support_cls, value, memory=cache)
            setattr(support_cls, prop_name, value)
        del cache

        ns_globals[class_name].value = support_cls
        ns_globals[class_name] = support_cls

        dataclass_template = env.get_template('data_class.jinja').render(
            class_name=class_name,
            slots=repr(tuple('_{}_'.format(key) for key in columns) + support_columns))
        exec(compile(
            dataclass_template,
            '<dcs>', mode='exec'), ns_globals, ns_globals)
        dc.value = data_class = ns_globals[f'_{class_name}']
        data_class.__module__ = support_cls.__module__
        data_class.__qualname__ = f'{support_cls.__qualname__}.{data_class.__name__}'
        parent_cell.value = support_cls
        klass.REGISTRY.add(support_cls)
        return support_cls


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
        t_s = time.time()
        self._changes = {
            key: [Delta('default', UNDEFINED, value, 0)] for key, value in self
        }
        self._changed_keys = [(key, t_s) for key in self._columns]
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
        msg = 'update'
        if self._flags & 2 == 2:
            msg = 'initialized'
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
    UNPICKLING = 16


DEFAULTS = '''{%- for field in fields %}
result._{{field}}_ = None
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


def _encode_simple_nested_base(iterable, *, immutable=None):
    '''
    Handle an List[Base], Tuple[Base], Mapping[Any, Base]
    and coerce to json. Does not deeply traverse by design.
    '''

    # Empty items short circuit:
    if not iterable:
        return iterable
    if isinstance(iterable, Mapping):
        for key in iterable:
            value = iterable[key]
            if hasattr(value, 'to_json'):
                iterable[key] = value.to_json()
        return iterable
    elif isinstance(iterable, Sequence):
        if immutable is None and isinstance(iterable, tuple):
            immutable = True
        elif immutable is None and isinstance(iterable, list):
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
            if hasattr(item, 'to_json'):
                iterable[index] = item.to_json()
        return iterable
    return iterable


class Base(metaclass=Atomic, skip=True):
    __slots__ = ('_flags',)
    __setter_template__ = ReadOnly('self._{key}_ = val')
    __getter_template__ = ReadOnly('return self._{key}_')
    __defaults_init__ = ReadOnly(DEFAULTS)

    @classmethod
    def _create_invalid_type(cls, field_name, val, val_type, types_required):
        if len(types_required) > 1:
            if len(types_required) == 2:
                expects = 'either an {.__name__} or {.__name__}'.format(*types_required)
            else:
                expects = \
                    f'either an {", ".join(x.__name__ for x in types_required[:-1])} '\
                    f'or a {types_required[-1].__name__}'
        else:
            expects = f'a {types_required[0].__name__}'
        return TypeError(
            f'Unable to set {field_name} to {val!r} ({val_type.__name__}). {field_name} expects '
            f'{expects}')

    @classmethod
    def _create_invalid_value(cls, message, *args, **kwargs):
        return ValueError(message, *args, **kwargs)

    def keys(self):
        return self._columns.keys()

    def __new__(cls, *args, **kwargs):
        # Get the edge class that has all the __slots__ defined
        cls = cls._data_class
        result = super().__new__(cls)
        result._flags = 0
        assert '__dict__' not in dir(result), \
            'Violation - there should never be __dict__ on a slotted class'
        return result

    def __len__(self):
        return len(self._column_types)

    def __contains__(self, item):
        return item in self._column_types

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    @classmethod
    def from_json(cls, data: dict):
        return cls(**data)

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
            elif hasattr(value, 'isoformat'):
                value = value.isoformat()
            elif not isinstance(value, (str, bytearray, bytes)) and \
                    isinstance(value, (Mapping, Sequence)):
                value = _encode_simple_nested_base(value, immutable=True)
            result[key] = value
        return result

    def items(self):
        return ItemsView(self)

    def values(self):
        return ValuesView(self)

    def __json__(self):
        return self.to_json()

    def __reduce__(self):
        # Create an empty class then let __setstate__ in the autogen
        # code to handle passing raw values.
        data_class, support_cls, *_ = self.__class__.__mro__
        return load_cls, (support_cls, (), {}), self.__getstate__()

    def _handle_init_errors(self, errors, errored_keys, unrecognized_keys):
        if unrecognized_keys:
            fields = ', '.join(unrecognized_keys)
            errors.append(self._create_invalid_value(f'Unrecognized fields {fields}'))
        if errors:
            typename = type(self).__name__[1:]
            raise ClassCreationFailed(
                f'Unable to construct {typename}, encountered {len(errors)} '
                f'error{"s" if len(errors) > 1 else ""}', *errors)

    def __init__(self, **kwargs):
        self._flags |= Flags.IN_CONSTRUCTOR
        self._flags |= Flags.DEFAULTS_SET
        errors = []
        errored_keys = []
        for key in self._columns.keys() & kwargs.keys():
            value = kwargs[key]
            try:
                setattr(self, key, value)
            except Exception as e:
                errors.append(e)
                errored_keys.append(key)
        for key in self._properties & kwargs.keys():
            value = kwargs[key]
            try:
                setattr(self, key, value)
            except Exception as e:
                errors.append(e)
                errored_keys.append(key)
        unrecognized_keys = ()
        if kwargs.keys() - (self._columns.keys() | self._properties):
            unrecognized_keys = kwargs.keys() - (self._columns.keys() | self._properties)
        self._handle_init_errors(errors, errored_keys, unrecognized_keys)
        self._flags = Flags.INITIALIZED

    def clear(self, fields=None):
        pass


Mapping.register(Base)
