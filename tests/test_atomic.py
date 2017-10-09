from typing import Union
from instruct import Base
import pytest


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


def test_derived_klass():
    assert isinstance(NestedData._columns['nested'], type)
    item = NestedData(id=1, nested={'field': 'autumn'})
    assert item.nested.field == 'autumn'
    with pytest.raises(TypeError):
        item.nested.field = 1


def test_derived_equivalence():
    item = NestedData(id=1, nested={'field': 'autumn'})
    item_alt = NestedDataAlt(id=1, nested={'field': 'autumn'})
    assert item == item_alt


def test_valid_types():
    t = Data(field=1)
    assert t.field == 1
    t.field = 't'
    assert t.field == 't'


def test_invalid_types():
    with pytest.raises(TypeError):
        Data(field=None)

def test_history():
    t = Data(field='autumn')
    t.field = 'not autumn'
    for change in t.list_changes():
        print('[{0.timestamp}] [{0.delta.state}] {0.key} -> {0.delta.old} -> {0.delta.new}'.format(change))


def test_history_autoprune():
    '''
    A historical object should be smart enough to recognize when it's not really changed
    '''
    t = Data(field='autumn')
    t.field = 'not autumn'
    t.field = 'autumn'
    changes = tuple(t.list_changes())
    for change in changes:
        print('[{0.timestamp}] [{0.delta.state}] {0.key} -> {0.delta.old} -> {0.delta.new}'.format(change))
    assert len(changes) == 3
    assert not t.is_dirty, 'object was cleanly initialized and not effectively changed'


def test_changed():
    t = Data()
    t.field = 'Autumn'
    assert t.is_dirty, 'Item should be dirty - we added a property!'
    t.field = 0
    assert not t.is_dirty, 'Item is now reset'


def test_reset():
    t = Data(field='Autumn')
    t.reset_changes()
    assert t.field == 'Autumn'
    assert not t.is_dirty

