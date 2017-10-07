from typing import Union
from instruct import Base
import pytest


class Data(Base, history=True):
    __slots__ = {
        'name_or_id': Union[str, int],
    }

    def __init__(self, **kwargs):
        self._name_or_id = 0
        super().__init__(**kwargs)


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

