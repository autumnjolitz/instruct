import sys
import builtins
import inspect
from contextlib import suppress
from pathlib import Path
from functools import wraps

import pytest

repository = Path(__file__).resolve(True).parent.parent


@wraps(builtins.print)
def print(*args, **kwargs) -> None:
    s, *rest = args
    if not isinstance(s, str):
        rest = (s, *rest)
        s = ""
    stack = inspect.stack()[1:]
    caller, *stack = stack
    module_name = caller.frame.f_globals["__name__"]
    prefix = f"[{module_name}.{caller.function}]"
    with suppress(KeyError):
        module_name = caller.frame.f_locals["__name__"]
    if s:
        s = f"{prefix} {s}"
    return builtins.print(s or prefix, *rest, **kwargs)


def pytest_ignore_collect(collection_path: Path, path, config: pytest.Config) -> bool:
    with suppress(ValueError):
        _, version = collection_path.stem.rsplit("_", 1)
        major, minor = int(version[:1], 10), int(version[1:], 10)
        if sys.version_info[:2] < (major, minor):
            print(
                f"Skipping {collection_path.relative_to(repository)!s} "
                f"(python {sys.version_info[:2]} < ({major}, {minor}))",
                file=sys.stderr,
            )
            return True
    return False
