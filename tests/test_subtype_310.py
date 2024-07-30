from instruct.subtype import (
    wrapper_for_type,
)
from instruct import AtomicMeta


def test_union():
    wrapper_for_type(int | str, {}, AtomicMeta)
