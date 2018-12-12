import json
from typing import Union, List
import datetime
import pickle

import pytest

from instruct import Base, add_event_listener, ClassCreationFailed


class Data(Base, history=True):
    __slots__ = {
        'field': Union[str, int],
        'other': str,
    }

    def __init__(self, **kwargs):
        self.field = 0
        super().__init__(**kwargs)


class NestedData(Base):
    '''
    And embedded dict should mean a class will be spawned and stored at the value
    location
    '''
    __slots__ = {
        'id': int,
        'nested': {
            'field': str,
        }
    }


class Field(Base):
    __slots__ = {
        'field': str
    }


class NestedDataAlt(Base):
    __slots__ = {
        'id': int,
        'nested': Field,
    }


class LinkedFields(Base):
    __slots__ = {
        'id': int,
        'name': str,
    }

    __coerce__ = {
        'id': (str, lambda obj: int(obj, 10))
    }

    def __init__(self, **kwargs):
        self.id = 0
        self.name = ''
        super().__init__(**kwargs)

    @add_event_listener('id')
    def _on_id_change(self, old, new):
        if new == -1:
            self.name = 'invalid'


def test_pickle():
    l = LinkedFields(id=2, name='Ben')
    data = pickle.dumps(l)
    l2 = pickle.loads(data)
    assert l == l2


def test_json():
    l = LinkedFields(id=2, name='Ben')
    data = json.dumps(l.to_json())
    l2 = LinkedFields(**json.loads(data))
    assert l == l2


def test_coercion():
    l = LinkedFields(id='2', name='Ben')
    assert l.id == 2
    l.id = '5'
    assert l.id == 5


def test_event_listener():
    l = LinkedFields(id=2, name='Ben')
    l.id = -1
    assert l.name == 'invalid'


def test_derived_klass():
    assert isinstance(NestedData._columns['nested'], type)
    item = NestedData(id=1, nested={'field': 'ben'})
    assert item.nested.field == 'ben'
    with pytest.raises(TypeError):
        item.nested.field = 1


def test_derived_equivalence():
    item = NestedData(id=1, nested={'field': 'ben'})
    item_alt = NestedDataAlt(id=1, nested={'field': 'ben'})
    assert item == item_alt


def test_valid_types():
    t = Data(field=1)
    assert '__dict__' not in dir(t)
    assert t.field == 1
    t.field = 't'
    assert t.field == 't'


def test_invalid_types():
    with pytest.raises(TypeError):
        Data(field=None)


def test_history():
    t = Data(field='ben')
    t.field = 'not ben'
    for change in t.list_changes():
        print(change)
        print('[{0.timestamp}] [{0.delta.state}] {0.key} -> {0.delta.old} -> {0.delta.new}'.format(change))


def test_history_autoprune():
    '''
    A historical object should be smart enough to recognize when it's not really changed
    '''
    t = Data(field='ben')
    t.field = 'not ben'
    t.field = 'ben'
    changes = tuple(t.list_changes())
    for change in changes:
        print('[{0.timestamp}] [{0.delta.state}] {0.key} -> {0.delta.old} -> {0.delta.new}'.format(change))
    assert len(changes) == 3
    assert not t.is_dirty, 'object was cleanly initialized and not effectively changed'


def test_changed():
    t = Data()
    t.field = 'Ben'
    assert t.is_dirty, 'Item should be dirty - we added a property!'
    t.field = 0
    assert not t.is_dirty, 'Item is now reset'


def test_reset():
    t = Data(field='Ben')
    t.reset_changes()
    assert t.field == 'Ben'
    assert not t.is_dirty


def test_fast_setter():
    class FastData(Base, fast=True):
        __slots__ = {
            'a': int,
            'bar': str
        }

        @add_event_listener('a')
        def on_a_set(self, old, new):
            self.bar = str(new)

    f = FastData(a=1)
    assert f.bar == '1'


def test_getitem():
    class Foo(Base):
        __slots__ = {
            'a': int,
            'b': str
        }

        def some_func():
            return 1

    f = Foo(a=1, b='s')
    assert f['a'] == 1
    assert f['b'] == 's'

    assert {**f} == {'a': 1, 'b': 's'}


def test_readme():

    class Member(Base):
        __slots__ = {
            'first_name': str,
            'last_name': str,
            'id': int,
        }

        def __init__(self, **kwargs):
            self.first_name = self.last_name = ''
            self.id = -1
            super().__init__(**kwargs)

    class Organization(Base, history=True):
        __slots__ = {
            'name': str,
            'id': int,
            'members': List[Member],
            'created_date': datetime.datetime,
        }

        __coerce__ = {
            'created_date': (str, lambda obj: datetime.datetime.strptime('%Y-%m-%d', obj)),
            'members': (list, lambda val: [Member(**item) for item in val])
        }

        def __init__(self, **kwargs):
            self.name = ''
            self.id = -1
            self.members = []
            self.created_date = datetime.datetime.utcnow()
            super().__init__(**kwargs)

    data = {
        "name": "An Org",
        "id": 123,
        "members": [
            {
                "id": 551,
                "first_name": "Jinja",
                "last_name": "Ninja",
            }
        ]
    }
    org = Organization(**data)
    assert org.members[0].first_name == 'Jinja'
    org.name = "New Name"
    print(tuple(org.list_changes()))


def test_invalid_kwargs():

    class Test(Base):
        __slots__ = {
            'foo': str,
            'bar': float,
            'blech': int,
        }

    with pytest.raises(ClassCreationFailed) as e:
        Test(foo=1.2, bar=1, blech='2')
    assert len(e.value.errors) == 3
    print(e.value.to_json())


def test_properties():
    class Test(Base):
        __slots__ = {
            'foo': str,
            'bar': float,
            'blech': int,
        }

        @property
        def yoo(self):
            return self.foo

        @yoo.setter
        def yoo(self, val):
            self.foo = val
    assert Test._properties | Test._columns.keys() == frozenset(['foo', 'bar', 'blech', 'yoo'])

    t = Test(yoo='New foo')
    assert t.foo == 'New foo'
