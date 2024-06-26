import json
import os
import shutil
import types
import base64
import builtins
import io
import sys
import tempfile
import tarfile
import zipfile
from contextlib import suppress, contextmanager, closing
from pathlib import Path
from typing import Type, Union, Dict, Tuple, Iterable, TypeVar, List, Optional

if sys.version_info[:2] >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


from invoke.context import Context
from tasksupport import task

_ = types.SimpleNamespace()
this = sys.modules[__name__]

DEFAULT_FORMAT = "lines"


T = TypeVar("T")
U = TypeVar("U")


def perror(*args, file=None, **kwargs):
    if file is None:
        file = sys.stderr
    return print(*args, file=file, **kwargs)


@contextmanager
def cd(path: Union[str, Path]):
    if not isinstance(path, Path):
        path = Path(path)
    new_cwd = path.resolve()
    prior_cwd = Path(os.getcwd()).resolve()
    try:
        os.chdir(new_cwd)
        yield prior_cwd
    finally:
        os.chdir(prior_cwd)


class Branch(str):
    __slots__ = ()

    def __repr__(self):
        return f'{type(self).__name__}("{self!s}")'


class Tag(str):
    __slots__ = ()

    def __repr__(self):
        return f'{type(self).__name__}("{self!s}")'


@task
def branch_name(context: Context) -> Union[Branch, Tag]:
    with suppress(KeyError):
        ref = os.environ["GITHUB_REF"]
        if ref.startswith("refs/heads/"):
            return Branch(ref.removeprefix("refs/heads/"))
        if ref.startswith("refs/tags/"):
            return Tag(ref.removeprefix("refs/tags/"))
        if ref.startswith("refs/pull/"):
            return Branch(os.environ["GITHUB_HEAD_REF"])
    here = this._.project_root(Path, silent=True)
    if (here / ".git").is_dir():
        with suppress(FileNotFoundError):
            result = context.run(f"git -C {here!s} branch --show-current", hide="both")
            assert result is not None
            branch = result.stdout.strip()
            if branch:
                return Branch(branch)
            result = context.run(
                f"git -C {here!s} describe --all --contains --abbrev=4 HEAD", hide="both"
            )
            assert result is not None
            if result.stdout.startswith("tags/"):
                return Tag(result.stdout.strip().removeprefix("tags/"))
        with open(here / ".git" / "HEAD") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("ref:"):
                    _, line = (x.strip() for x in line.split(":", 1))
                    if line.startswith("refs/heads/"):
                        return Branch(line.removeprefix("refs/heads/"))
                    elif line.startswith("refs/tags/"):
                        return Tag(line.removeprefix("refs/tags/"))
                    else:
                        raise ValueError(f"Unknown ref type: {line}")
                # okay! detached HEAD!~
                for tag in sorted(
                    (here / ".git" / "refs" / "tags").iterdir(),
                    key=lambda o: o.stat().st_mtime,
                    reverse=True,
                ):
                    if tag.is_file() and tag.read_text().strip():
                        return Tag(tag.name)
                all_branch_heads = here / ".git" / "refs" / "heads"
                for root, dirs, files in (here / ".git" / "refs" / "heads").walk():
                    for file in files:
                        if file.read_text().strip() == line:
                            return Branch(str(file).removeprefix(str(all_branch_heads)))
    raise ValueError("Unable to determine branch name!")


def window(
    iterable: Iterable[T], *, terminus: Optional[U] = None
) -> Iterable[Tuple[T, Union[T, Optional[U]]]]:
    g = iter(iterable)
    item = next(g)
    for next_item in g:
        yield item, next_item
        item = next_item
    yield item, terminus


@task
def update_changes(context: Context, version: str = ""):
    python_bin = _.python_path(str, silent=True)
    extra = ""
    if version:
        extra = f"-B {version}"
    result = context.run(f"{python_bin} -m git_changelog {extra}", warn=True)
    assert result is not None
    if "already in changelog" in result.stderr:
        perror("No new changes to create changelog with")
        return
    with open(_.project_root(Path, silent=True) / "CHANGES.rst", "r+") as fh:
        body = fh.read()
        index = body.index(".. |Changes|")
        index += body[index:].index("\n") + 1
        with suppress(ValueError):
            index += body[index:].index(".. |Changes|")
            index += body[index:].index("\n") + 1
        in_between = body[index : index + 2]
        deleted_newline_count = 0
        while in_between[-1] == "\n":
            body = body[:index] + body[index + 1 :]
            in_between = body[index : index + 2]
            deleted_newline_count += 1
        if deleted_newline_count:
            perror(f"deleted {deleted_newline_count} extra newlines")
            fh.seek(0)
            fh.write(body)


@task
def test(context: Context):
    python_bin = _.python_path(str)
    context.run(f"{python_bin} -m pytest")


@task
def setup_metadata(file: Optional[str] = None) -> Dict[str, Union[str, Tuple[str, ...]]]:
    in_metadata = False
    sep = "="
    if file is None:
        fh = open(_.project_root(Path, silent=True) / "setup.cfg")
    else:
        if file.endswith(".whl"):
            with zipfile.ZipFile(file, "r") as wheel:
                for metadata in wheel.infolist():
                    if metadata.filename.endswith(".dist-info/METADATA"):
                        fh = io.StringIO(wheel.read(metadata).decode())
                        in_metadata = True
                        sep = ":"
                        break
        elif file.endswith(".tar.gz"):
            with tarfile.open(file) as sdist:
                for metadata in sdist:
                    filename = Path(metadata.name)
                    if filename.name == "setup.cfg":
                        fh = io.StringIO(sdist.extractfile(metadata).read().decode())
                        break
    with closing(fh):
        in_multiline = False
        values: Optional[Union[str, List[str]]] = None
        key = None
        mapping: Dict[str, Union[str, Tuple[str, ...]]] = {}
        for line in fh:
            if line.startswith("[metadata]"):
                in_metadata = True
                continue
            if line.startswith("[") and in_metadata:
                in_metadata = False
            if in_metadata:
                if sep in line and in_multiline:
                    in_multiline = False
                    assert key is not None
                    assert isinstance(values, list)
                    mapping[key] = tuple(values)
                    values = None
                if in_multiline:
                    assert isinstance(values, list)
                    values.append(line.strip())
                    continue
                if not line.strip():
                    break

                else:
                    key, value = [x.strip() for x in line.split(sep, 1)]
                    key = key.lower()
                    if not value:
                        in_multiline = True
                        values = []
                        continue
                    if key in mapping:
                        if isinstance(mapping[key], str):
                            mapping[key] = (mapping[key], value.strip())
                        else:
                            mapping[key] = (*mapping[key], value.strip())
                    else:
                        mapping[key] = value.strip()
    return mapping


@task
def project_name(context: Context) -> str:
    return _.setup_metadata(silent=True)["name"]


@task
def b64encode(value: str, silent: bool = True) -> str:
    return base64.urlsafe_b64encode(value.encode()).decode().strip()


@task
def b64decode(value: str, silent: bool = True) -> str:
    remainder = len(value) % 8
    if remainder:
        value += "=" * remainder
    return base64.urlsafe_b64decode(value).decode().strip()


def get_topmost_directory(p: Path) -> Path:
    while p.parent.name:
        p = p.parent
    return p


@task
def build(context: Context, validate: bool = False) -> Tuple[Path, ...]:
    """
    Create special sdists that do not depend on source control and
    a bdist from said sdist.

    Because we use ``CURRENT_VERSION`` to generate ``instruct/about.py``,
    a simple sdist will unfortunately lose the information on which source
    control version it came from.

    *However* the act of generating an sdist will create the ``instruct/about.py``
    file which we can then ``exec`` and pull out the public-friendly version.

    We will basically replace the ``attr: ...`` callout in setup.cfg with the
    actual public version, thus satisfying the need to preserve a source-control'd
    about.py while being relatively repeatable.

    As a safety, we have a ``validate`` option that will try to install
    the artifacts into a venv and try to import instruct.
    """
    python_bin = _.python_path(str, silent=True)
    dist = _.project_root(Path, silent=True) / "dist"
    public_version = None
    files = []
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        del tmp
        tempdist = t / "dist"
        tempdist.mkdir()
        context.run(f"{python_bin} -m build -s -o {t!s}/sdist")
        (sdist,) = (Path(t).resolve() / "sdist").iterdir()
        with tarfile.open(sdist) as source, tarfile.open(
            f"{tempdist!s}/{sdist.name}", "w:gz"
        ) as dest:
            top_most = None
            for metadata in source:
                buf = None
                filename = Path(metadata.name)
                if top_most is None:
                    top_most = get_topmost_directory(filename)
                assert top_most is not None
                if filename.parent.name == top_most.name and filename.name in (
                    "generate_version.py",
                    "CURRENT_VERSION.txt",
                ):
                    continue
                if metadata.isfile():
                    if (filename.parent.name, filename.name) == ("instruct", "about.py"):
                        gs = {}
                        buf = source.extractfile(metadata)
                        assert buf is not None
                        exec(buf.read(), gs)
                        buf.seek(0)
                        public_version = gs["__version_info__"].public
                    elif (filename.parent.name, filename.name) == (top_most.name, "setup.cfg"):
                        buf = io.BytesIO()
                        fh = source.extractfile(metadata)
                        assert fh is not None
                        with closing(fh):
                            for line in fh:
                                if line.startswith(b"version ="):
                                    buf.write(b"version = %s\n" % (public_version.encode(),))
                                else:
                                    buf.write(line)
                        metadata.size = buf.tell()
                        buf.seek(0)
                    else:
                        buf = source.extractfile(metadata)
                        assert buf is not None
                if buf is not None:
                    with closing(buf):
                        dest.addfile(metadata, buf)
                else:
                    dest.addfile(metadata)
        context.run(f"{python_bin} -m venv {t!s}/venv")
        context.run(
            f"{t!s}/venv/bin/python -m pip wheel --no-deps file:///{dest.name!s} -w {t!s}/dist"
        )
        if validate:
            for filename in tempdist.iterdir():
                with tempfile.TemporaryDirectory() as venv:
                    context.run(f"{python_bin} -m venv {venv}")
                    context.run(f"{venv!s}/bin/python -m pip install file:///{filename!s}")
                    context.run(f"{venv!s}/bin/python -c 'import instruct'")
        for filename in tempdist.iterdir():
            files.append(filename.rename(dist / filename.name))
    return tuple(files)


@task
def project_root(
    as_type: Union[Type[str], Type[Path], Literal["str", "Path"]] = "str"
) -> Union[str, Path]:
    """
    Get the absolute path of the project root assuming tasks.py is in the repo root.
    """
    if isinstance(as_type, builtins.type):
        return_type = as_type.__name__
    else:
        return_type = as_type
    assert return_type in ("str", "Path"), f"{return_type} may be str or Path"
    root = Path(__file__).resolve().parent
    if return_type == "str":
        return str(root)
    return root


@task
def python_path(
    as_type: Union[Literal["str", "Path"], Type[Path], Type[str]] = "str",
    *,
    skip_venv: bool = False,
) -> Union[str, Path]:
    """
    Return the best python to use
    """
    if isinstance(as_type, type):
        type_name = as_type.__name__
    else:
        type_name = as_type
    assert type_name in ("Path", "str")
    root = Path(__file__).resolve().parent
    python = root / "python" / "bin" / "python"
    if not skip_venv:
        # try to see if the current venv is a repo-level venv:
        with suppress(KeyError):
            venv_python = Path(os.environ["VIRTUAL_ENV"]) / "bin" / "python"
            if venv_python.exists() and root in venv_python.parents:
                python = venv_python
    if not python.exists():
        # If  we don't have a venv, can we fallback to the $USER's venvs?
        with suppress(KeyError):
            python = Path(os.environ["VIRTUAL_ENV"]) / "bin" / "python"
    if skip_venv or not python.exists():
        failed_pythons = []
        for version in ("3.12", "3.11", "3.10", "3.9", "3.8", "3.7", "3"):
            candidate = shutil.which(f"python{version}")
            if candidate is None:
                continue
            with suppress(FileNotFoundError):
                python = Path(
                    candidate,
                    path=":".join(
                        x for x in os.environ["PATH"].split(":") if Path(x) != python.parent
                    ),
                ).resolve(True)
                break
            failed_pythons.append(candidate or f"python{version}")
        else:
            raise FileNotFoundError(
                "Unable to find a single python3 binary! Tried {}".format(", ".join(failed_pythons))
            )
    if type_name == "str":
        return str(python)
    return python


@task
def setup(
    context: Context,
    python_bin: Union[str, None] = None,
    tests: bool = False,
    devel: bool = False,
    project: bool = True,
    swap_venv_stage: Optional[str] = None,
) -> Path:
    """
    Create the venv for this project.

    This task can destroy the project's venv and recreate it from the same process id.

    swap_venv_stage: This is the internals of how a venv can replace itself while depending only
                     on the utilities within it (i.e. invoke).
    """
    root = _.project_root(Path)
    venv = root / "python"
    if python_bin is None:
        python_bin = _.python_path(str)

    requirements = ""
    if project:
        requirements = "-r setup-requirements.txt"
    if devel:
        requirements = f"{requirements} -r dev-requirements.txt"
    else:
        requirements = f"{requirements} invoke"
        if sys.version_info[:2] < (3, 11):  # 3.11 has get_overloads
            requirements = f"{requirements} typing-extensions"
    if tests:
        requirements = f"{requirements} -r test-requirements.txt"
    if project:
        requirements = f"{requirements} -e ."
        if any((devel, tests)):
            extra_addons = ",".join(
                [arg for arg, enabled in (("devel", devel), ("test", tests)) if enabled]
            )
            requirements = f"{requirements}[{extra_addons}]"

    if swap_venv_stage == "1-copy-new-venv":
        perror(f"Removing old venv at {venv}")
        shutil.rmtree(root / "python")
        context.run(f"{venv!s}_/bin/python -m venv --copies {venv!s}")
        if requirements:
            context.run(f"{venv!s}/bin/python -m pip install {requirements}")
        os.execve(
            f"{venv!s}/bin/python",
            ("python", "-m", "invoke", "setup", "--swap-venv-stage", "2-remove-tmp-venv"),
            os.environ,
        )
        assert False, "unreachable!"
    if swap_venv_stage == "2-remove-tmp-venv":
        tmp_venv = root / "python_"
        perror(f"Removing temp venv {tmp_venv}")
        shutil.rmtree(tmp_venv)
        original_argv = []
        try:
            original_argv = json.loads(os.environ["_INSTRUCT_INVOKE_TASK_ORIG_ARGS"])
        except ValueError:
            perror("Unable to decode original _INSTRUCT_INVOKE_TASK_ORIG_ARGS!", file=sys.stderr)
        while original_argv and original_argv[0] == "--":
            del original_argv[0]
        perror("Attempting to restore argv after setup which is", original_argv)
        if not original_argv:
            return
        os.execve(f"{venv!s}/bin/python", ("python", "-m", "invoke", *original_argv), os.environ)
        assert False, "unreachable!"

    current_python = Path(sys.executable)
    with suppress(FileNotFoundError):
        shutil.rmtree(f"{venv!s}_")
    if venv.exists() and str(current_python).startswith(str(venv)):
        # ARJ: Complex path: replacing a running environment.
        # Time for the os.execve hat dance!
        # make the subenvironment
        perror(f"installing tmp venv at {venv!s}_")
        context.run(f"{python_bin} -m venv {venv!s}_", hide="both")
        with Path(root / "dev-requirements.txt").open("rb") as fh:
            for line in fh:
                line_st = line.strip()
                while b"#" in line_st:
                    line_st = line[: line_st.rindex(b"#")].strip()
                if not line_st:
                    continue
                if line.startswith(b"invoke"):
                    break
            else:
                line = b"invoke"
            perror(f"installing tmp venv invoke")
            context.run(f"{venv!s}_/bin/python -m pip install {line.decode()}", hide="both")

        args = []
        skip_if_args = 0
        task_executed = True
        for arg in sys.argv:
            if task_executed and arg == "setup":
                skip_if_args += 2
                task_executed = False
                continue
            if arg == "--" or not arg.startswith("-"):
                skip_if_args = 0
                if arg == "--":
                    continue
            elif skip_if_args:
                skip_if_args -= 1
                continue
            if task_executed is False:
                args.append(arg)
        os.environ["_INSTRUCT_INVOKE_TASK_ORIG_ARGS"] = json.dumps(args)
        os.execve(
            f"{venv!s}_/bin/python",
            ("python", "-m", "invoke", "setup", "--swap-venv-stage", "1-copy-new-venv"),
            os.environ,
        )
        assert False, "unreachable"
    # Happy path:
    with suppress(FileNotFoundError):
        shutil.rmtree(root / "python")
    context.run(f"{python_bin} -m venv {venv!s}")
    if requirements:
        context.run(f"{venv!s}/bin/python -m pip install {requirements}")
    return venv
