from typing import Union, NewType
from instruct import Base
import cffi

import pytest


class Data(Base, history=True):
    __slots__ = {
        'name_or_id': Union[str, int],
    }

    def __init__(self, **kwargs):
        self._name_or_id = 0
        super().__init__(**kwargs)

# def test_nested_init():
#     n = NestedData(id=1, name='test', value={'id': 1})
#     n = NestedData(id=1, name='test', value=Node(id=1))


class CData(Base, cstruct=True, fast=True, history=True):
    '''
    One can easily define a class that will instead synthesize a
    CFFI struct instance.

    Want:
    struct {
        int id;
        char[8] name;
        union {
            int64_t as_int;
            double as_double;
        } value;
    }
    '''
    __slots__ = {
        'id': 'int',
        'name': 'char[8]',
        'value': Union[
            NewType('as_int', 'int64_t'),
            NewType('as_double', 'double')
        ],
    }


def test_cdata():
    item = CData(id=1, name=b'ben')
    item.value.as_int = 42
    data = bytes(item)
    new_item = CData()
    new_item.from_bytes(data)
    assert bytes(new_item) == bytes(item)
    assert new_item.value.as_int == 42


def test_valid_types():
    t = Data(name_or_id=1)
    assert t.name_or_id == 1
    t.name_or_id = 't'
    assert t.name_or_id == 't'


def test_invalid_types():
    with pytest.raises(TypeError):
        Data(name_or_id=None)


def test_history_autoprune():
    '''
    A historical object should be smart enough to recognize when it's not really changed
    '''
    t = Data(name_or_id='ben')
    t.name_or_id = 'not ben'
    t.name_or_id = 'ben'
    changes = tuple(t.list_changes())
    for change in changes:
        print('[{0.timestamp}] [{0.delta.state}] {0.key} -> {0.delta.old} -> {0.delta.new}'.format(change))
    assert len(changes) == 2
    assert not t.is_dirty, 'object was cleanly initialized and not effectively changed'


def test_changed():
    t = Data()
    t.name_or_id = 'Ben'
    assert t.is_dirty, 'Item should be dirty - we added a property!'
    t.name_or_id = 0
    assert not t.is_dirty, 'Item is now reset'


def test_reset():
    t = Data(name_or_id='Ben')
    t.reset_changes()
    assert t.name_or_id == 'Ben'
    assert not t.is_dirty

def test_columns():
    print(Data._columns)