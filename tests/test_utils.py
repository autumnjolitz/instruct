from instruct.utils import flatten


def test_flatten():
    assert flatten([['a']], eager=True) == ('a',)
