import json
import os
import shutil
import types
import base64
import builtins
import io
import hashlib
import sys
import tempfile
import tarfile
import typing
import zipfile
from contextlib import suppress, contextmanager, closing
from pathlib import Path
from typing import (
    Type,
    Union,
    Dict,
    Tuple,
    Iterable,
    TypeVar,
    List,
    Optional,
    NamedTuple,
)

if sys.version_info[:2] >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info[:2] >= (3, 10):
    from typing import TypeGuard, TypeAlias
else:
    from typing_extensions import TypeGuard, TypeAlias
if sys.version_info[:2] >= (3, 11):
    from typing import Never, assert_never
else:
    from typing_extensions import Never, assert_never

if typing.TYPE_CHECKING:
    from packaging.version import Version
    from packaging.version import parse as parse_version

    has_packaging = True

else:
    try:
        import packaging.version
    except ImportError:
        has_packaging = False
    else:
        packaging.version
        has_packaging = True

    if has_packaging:
        from packaging.version import Version
        from packaging.version import parse as parse_version
    else:
        Version: TypeAlias = Never

        def parse_version(v: str) -> Version:
            raise ImportError("packaging not found!")


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
                f"git -C {here!s} describe --all --contains --abbrev=4 HEAD",
                hide="both",
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
def last_logged_changes(context: Context) -> str:
    """
    Return the latest entry in CHANGES.rst.
    """
    python_bin = _.python_path(str, silent=True)
    cli = f"{python_bin} -m git_changelog"
    result = context.run(f"{cli} -R", warn=True, hide="both")
    assert result is not None
    if result:
        return result.stdout
    perror(f"Unable to emit last release changes due to:\n{result.stderr}")
    raise SystemExit(result.return_code)


@task(
    help={
        "with_unreleased": "Add unreleased section if missing and populate",
        "version": "override version",
    }
)
def update_changelog(
    context: Context,
    version: str = "",
    output: Optional[str] = None,
    with_unreleased: bool = False,
):
    """
    Update the change log (output defaults to CHANGES.rst)
    """
    python_bin = _.python_path(str, silent=True)
    root = _.project_root(Path, silent=True)
    default_changelog = root / "CHANGES.rst"
    extra = f"-i -o {default_changelog!s}"
    if output is not None:
        output_file = Path(output).resolve()
    else:
        output_file = default_changelog
    if output in ("-", "/dev/stdout"):
        output = "-"
        extra = ""
    elif output_file != default_changelog:
        extra = f"-o {output_file!s}"
    if version:
        extra = f"{extra} -B {version}"
    if with_unreleased:
        extra = f"{extra} -j emit_unreleased=true"
    cli = f"{python_bin} -m git_changelog"
    result = context.run(f"{cli} {extra}", warn=True, hide="both")
    assert result is not None
    if not result:
        if "already in changelog" in result.stderr:
            perror("No new changes to create changelog with")
            return
        perror(f"Unable to run {cli!r} due to:\n{result.stderr}")
        raise SystemExit(result.return_code)
    if output == "-":
        return result.stdout
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
        while body[-2:] in ("\n", "\n"):
            body = body[:-1]
            deleted_newline_count += 1
        if deleted_newline_count:
            perror(f"deleted {deleted_newline_count} extra newlines")
            fh.seek(0)
            fh.truncate(0)
            fh.write(body)
    return


def walk_path(p: Path, *args, **kwargs):
    if callable(getattr(p, "walk", None)):
        return p.walk(*args, **kwargs)
    return _walk_path(p)


def _walk_path(p: Path, *args, **kwargs):
    for dirpath, dirnames, filenames in os.walk(f"{p!s}", *args, **kwargs):
        yield p / dirpath, dirnames, filenames


@task
def lint(context: Context):
    root = _.project_root(Path, silent=True)
    python_bin = _.python_path(str, silent=True)
    print("Flake8 Issues:")
    context.run(
        f"{python_bin} -m flake8 {root / 'instruct'!s} "
        "--select=E9,F63,F7,F82 --show-source --statistics"
    )
    print("Flake8 Warnings:")
    context.run(
        f"{python_bin} -m flake8 {root / 'instruct'!s} "
        "--ignore=E203,W503,E704 --count --exit-zero "
        "--max-complexity=103 --max-line-length=127 --statistics"
    )


@task(iterable=("override_hook",))
def pre_commit(
    context: Context,
    override_hook: List[str],
    staged: bool = False,
    changed: bool = False,
):
    if isinstance(override_hook, list):
        override_hook = " ".join(override_hook)

    python_bin = _.python_path(str, silent=True)
    root = _.project_root(Path, silent=True)
    generate_version = root / "generate_version.py"
    if changed:
        extra = "--name-only"
        if staged:
            extra = f"{extra} --staged"
        iterable = context.run(f"git -C {root!s} diff {extra}", hide=True).stdout.splitlines()
    else:
        assert not staged
        iterable = context.run(f"git -C {root!s} ls-files", hide=True).stdout.splitlines()
        extra = "--all-files"

    files = []
    for filename in iterable:
        file = root / filename
        with open(file, "rb") as fh:
            h = hashlib.new("sha256")
            h.update(fh.read())
        files.append((file, h.digest()))

    if changed:
        extra = f"--files {' '.join(str(row[0].relative_to(str(root))) for row in files)}"

    context.run(f"{python_bin} -m pre_commit --version")

    with context.cd(f"{root!s}"):
        cli = f"{python_bin} -m pre_commit run {extra} {override_hook} "
        context.run(cli)
    with tempfile.NamedTemporaryFile(mode="w+") as fh:
        context.run(f"{python_bin} {generate_version!s} {fh.name}")
        with tempfile.NamedTemporaryFile(mode="w+") as new:
            new.write(fh.read())
            fh.seek(0)
        if not context.run(
            f"{python_bin} -m pre_commit run --files {new.name} {override_hook} ",
            warn=True,
        ):
            perror("generate_version returns pre-commit issues!")
            context.run(f"diff -Naur {fh.name} {new.name}")
            raise SystemExit(1)
    changed = []
    for file, old_hash in files:
        with open(file, "rb") as fh:
            h = hashlib.new("sha256")
            h.update(fh.read())
            if old_hash != h.digest():
                changed.append(str(file.relative_to(root)))
    if changed:
        raise ValueError(f"{' '.join(changed)} changed!")
    print("success")


@task
def test(
    context: Context,
    *,
    test_files: Optional[Union[str, List[str], Tuple[str, ...]]] = None,
    verbose: bool = False,
    fail_fast: bool = False,
):
    python_bin = _.python_path(str, silent=True)
    extra = ""
    if verbose:
        extra = f"{extra} -svvv"
    if fail_fast:
        extra = f"{extra} -x"
    if test_files:
        if isinstance(test_files, str):
            test_files = tuple(x.strip() for x in test_files.split(","))
        f = " ".join(test_files)
        extra = f"{extra} {f}"
    context.run(f"{python_bin} -m coverage run -m pytest {extra}")


@task
def coverage_report(context: Context):
    python_bin = _.python_path(str, silent=True)
    context.run(f"{python_bin} -m coverage report -m")


@task
def setup_metadata(
    file: Optional[str] = None,
) -> Dict[str, Union[str, Tuple[str, ...]]]:
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
    if not dist.exists():
        perror(f"Creating {dist!s}")
        dist.mkdir()
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
                    if (filename.parent.name, filename.name) == (
                        "instruct",
                        "about.py",
                    ):
                        gs = {}
                        buf = source.extractfile(metadata)
                        assert buf is not None
                        exec(buf.read(), gs)
                        buf.seek(0)
                        public_version = gs["__version_info__"].public
                    elif (filename.parent.name, filename.name) == (
                        top_most.name,
                        "setup.cfg",
                    ):
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
    as_type: Union[Type[str], Type[Path], Literal["str", "Path"]] = "str",
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
            (
                "python",
                "-m",
                "invoke",
                "setup",
                "--swap-venv-stage",
                "2-remove-tmp-venv",
            ),
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
            perror(
                "Unable to decode original _INSTRUCT_INVOKE_TASK_ORIG_ARGS!",
                file=sys.stderr,
            )
        while original_argv and original_argv[0] == "--":
            del original_argv[0]
        perror("Attempting to restore argv after setup which is", original_argv)
        if not original_argv:
            return
        os.execve(
            f"{venv!s}/bin/python",
            ("python", "-m", "invoke", *original_argv),
            os.environ,
        )
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
            perror("installing tmp venv invoke")
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


@task
def dirty_repo(context) -> bool:
    root = _.project_root(Path, silent=True)
    if not (root / ".git").exists():
        perror(f"{root!s} is not a git repo, assuming not dirty!")
        return False
    result = context.run("git diff-index --quiet HEAD --", warn=True)
    assert result is not None
    if not result:
        if result.return_code == 1 and not result.stderr:
            return True
        perror("git threw an error!")
        raise SystemExit(result.return_code)
    return False


@task
def remote_tag_exists(context: Context, tag: str) -> bool:
    root = _.project_root(Path, silent=True)
    result = context.run(f"git -C {root!s} ls-remote origin refs/tags/{tag!s}")
    assert result is not None
    if result.stdout.strip():
        return True
    return False


@task
def local_tag_exists(tag: str) -> bool:
    root = _.project_root(Path, silent=True)
    tag_ref = root / ".git" / "refs" / "tags" / tag
    if tag_ref.exists():
        if not tag_ref.is_file():
            raise ValueError(f"{tag!r} is not a valid tag")
        return True
    return False


@task
def prior_release_to(context: Context, version: Union[str, Version] = "") -> Optional[Version]:
    root = _.project_root(Path, silent=True)
    if isinstance(version, str):
        if version:
            version = parse_version(version)
        else:
            version = _.show_version(context, silent=True)
    elif isinstance(version, Version):
        pass
    else:
        assert_never(version)
    result = context.run(f"git -C {root!s} tag -l", hide=True)
    assert result is not None
    prior_release = None
    for line in result.stdout.splitlines():
        if not line:
            continue
        release_version = parse_version(line)
        if release_version < version:
            if prior_release is None:
                prior_release = release_version
            elif release_version > prior_release:
                prior_release = release_version
    return prior_release


@task
def create_release(
    context: Context,
    *,
    next_version: Union[str, Version] = "",
    version: Union[str, Version] = "",
) -> Version:
    assert has_packaging
    branch = _.branch_name(context)
    assert branch == "master"
    root = _.project_root(Path, silent=True)
    if _.dirty_repo(context, silent=True):
        perror(
            f"Repository {root!s} is dirty! "
            "Please commit any and all changes *before* creating a release!"
        )
        raise SystemExit(22)
    next_version = _.bump_version(
        context, next_version, from_version=version, dry_run=True, silent=True
    )
    perror(f"Next version will be {next_version!s}")
    assert isinstance(next_version, Version)
    repo_version = _.show_version(context, silent=True)
    if isinstance(version, str) and version == "":
        version = repo_version
    else:
        assert not _.remote_tag_exists(context, f"v{version!s}")
        assert not _.local_tag_exists(f"v{version!s}")
        if isinstance(version, str):
            version = parse_version(version)
    assert isinstance(version, Version)
    if version != repo_version:
        print(
            f"Discovered that CURRENT_VERSION.txt returned {repo_version}, however we require it to be {version}. Updating"
        )
        _.bump_version(context=context, to_version=version)
        print(f"Set CURRENT_VERSION.txt to {_.show_version(context, silent=True)}")

    print(f"Releasing v{version!s}, prior release was {_.prior_release_to(context, version)}")
    assert next_version > version, f"{next_version!s} must be greater than {version!s}!"
    perror(f"Checking if tag v{version!s} exists on remote!")
    if _.remote_tag_exists(context, f"v{version!s}"):
        perror(f"tag v{version!s} already exists on remote!")
        raise SystemExit(2)
    perror("Checking if tag exists locally (i.e. partial release)")
    if _.local_tag_exists(f"v{version!s}"):
        print("found local tag, Removing")
        context.run(f"git tag -d v{version!s}")
    assert not _.dirty_repo(context, silent=True), "repo dirty~?"
    perror(f"Creating a lightweight tag v{version!s} for changelog updating...")
    context.run(f"git tag v{version!s}")
    _.update_changelog(context, version=str(version))
    perror(f"deleting lightweight tag v{version!s}")
    context.run(f"git tag -d v{version!s}")
    if _.dirty_repo(context, silent=True):
        perror("changelog did change, committing it.")
        context.run(f"git -C {root!s} add {root / 'CHANGES.rst'}")
        context.run(f'git -C {root!s} commit -m "doc: update CHANGES.rst"')
        if _.dirty_repo(context, silent=True):
            perror("Repository is still dirty despite committing CHANGES.rst!")
            raise SystemExit(123)
    perror(f"Creating annotated tag v{version!s}")
    with io.StringIO() as fh:
        fh.write(_.last_logged_changes(context))
        fh.seek(0)
        context.run(f"git -C {root!s} tag -a v{version!s} -F -", in_stream=fh)
    assert not _.dirty_repo(context, silent=True)
    return _.bump_version(context, to_version=next_version, silent=True)


@task
def show_version(context: Context) -> Version:
    assert has_packaging
    root = _.project_root(Path, silent=True)
    with open(root / "CURRENT_VERSION.txt") as fh:
        for line in (x.strip() for x in fh):
            if line.startswith("#"):
                continue
            if "#" in line:
                line, ignore = line.split("#", 1)
            version = parse_version(line)
    return version


def _is_bump_type(
    s: str,
) -> TypeGuard[Literal["a", "b", "dev", "rc", "major", "minor", "patch", "post"]]:
    return s in ("a", "b", "dev", "rc", "major", "minor", "patch", "post")


PRE_RELEASE_TYPES = ("a", "b", "rc")


@task
def bump_version(
    context: Context,
    to_version: Union[str, Version] = "",
    dry_run: bool = False,
    *,
    from_version: Union[str, Version] = "",
) -> Version:
    assert has_packaging

    root = _.project_root(Path, silent=True)
    branch = _.branch_name(context, silent=True)
    assert branch == "master"
    root = _.project_root(Path, silent=True)
    if not dry_run and _.dirty_repo(context, silent=True):
        perror(
            f"Repository {root!s} is dirty! "
            "Please commit any and all changes *before* creating a release!"
        )
        raise SystemExit(22)

    current_version: Version = _.show_version(context, silent=True)
    if isinstance(from_version, str):
        if from_version:
            current_version = parse_version(from_version)
    elif isinstance(from_version, Version):
        current_version = from_version
    else:
        assert_never(from_version)
    del from_version

    bump_type: Literal["a", "b", "dev", "rc", "major", "minor", "patch", "post", ""] = ""
    if isinstance(to_version, str) and to_version in (
        "a",
        "alpha",
        "beta",
        "b",
        "dev",
        "rc",
        "patch",
        "minor",
        "major",
        "post",
    ):
        if to_version in ("alpha", "beta"):
            to_version = to_version[:1]
        assert _is_bump_type(to_version)
        bump_type = to_version
        to_version = ""

    action = "set"
    if not to_version:
        action = "bump"
        if not bump_type:
            if current_version.is_prerelease:
                bump_type = current_version.pre[0]
            elif current_version.is_postrelease:
                bump_type = "post"
            elif current_version.is_devrelease:
                bump_type = "dev"
            else:
                bump_type = "patch"
        if bump_type in PRE_RELEASE_TYPES:
            pre_type, pre_ord = current_version.pre
            assert PRE_RELEASE_TYPES.index(bump_type) >= PRE_RELEASE_TYPES.index(pre_type)
            if bump_type != pre_type:
                pre_ord = -1
            to_version = f"{current_version.base_version}{bump_type}{pre_ord + 1}"
        elif bump_type == "post":
            to_version = f"{current_version.base_version}post{current_version.post + 1}"
        elif bump_type == "dev":
            to_version = f"{current_version.base_version}dev{current_version.dev + 1}"
        elif bump_type == "major":
            to_version = f"{current_version.major + 1}.0.0"
        elif bump_type == "minor":
            to_version = f"{current_version.major}.{current_version.minor + 1}.0"
        elif bump_type == "patch":
            patch = current_version.micro + 1
            if current_version.is_prerelease:
                patch = current_version.micro
            to_version = f"{current_version.major}.{current_version.minor}.{patch}"
        else:
            assert False, "unreachable"

    if isinstance(to_version, str):
        next_version = parse_version(to_version)
    elif isinstance(to_version, Version):
        next_version = to_version
    else:
        assert_never(to_version)

    with open(root / "CURRENT_VERSION.txt", "r+") as fh:
        index = 0
        for line in fh:
            index += len(line)
            line_s = line.strip()
            if line_s.startswith("#"):
                continue
            if "#" in line_s:
                line_s, ignore = line_s.split("#", 1)
            parse_version(line_s)
            # version = parse_version(line_s)
            break
            # assert next_version > version
        if not dry_run:
            if index:
                fh.seek(index - len(line))
                fh.truncate(fh.tell())
                fh.write(f"{next_version!s}\n")
            else:
                perror(f"{fh.name!r} is empty?! Readding comment")
                fh.seek(0)
                fh.write("# bump the below version on release\n")
            assert _.dirty_repo(context, silent=True), (
                "Repo is not dirty despite modifying the version??"
            )
    if not dry_run:
        context.run(f"git -C {root!s} add CURRENT_VERSION.txt")
        with io.StringIO() as fh:
            fh.write(f"build(release): {action} version to {next_version!s}")
            fh.seek(0)
            context.run(f"git -C {root!s} commit -F -", in_stream=fh)
    return next_version


@task
def checksum(context: Context, with_header: bool = True):
    root = _.project_root(Path, silent=True)
    dist = root / "dist"
    if not dist.exists():
        return
    if with_header:
        sys.stdout.write("\nChecksums\n^^^^^^^^^^^\n::\n\n")
    for file in sorted(dist.iterdir()):
        file_hash = hashlib.sha256()
        file_hash.update(file.read_bytes())
        sys.stdout.write(f"    SHA2-256({file.name})= {file_hash.hexdigest()}\n")
    sys.stdout.write("\n")
    sys.stdout.flush()


class UnitValue(NamedTuple):
    value: Union[int, float]
    unit: str


@task
def parse_with_unit(s: str) -> Tuple[Union[int, float], str]:
    s = s.strip()
    has_dot = False
    units = []
    values = []
    has_unit = False
    has_sep = False
    for char in s:
        is_sep = not char.strip()
        if (char.isalpha() or is_sep) and not has_unit:
            has_unit = True
        if has_unit:
            if is_sep:
                if has_sep:
                    raise ValueError("Encountered extra seperator after first one!")
                has_sep = True
            units.append(char)
        else:
            if char == ".":
                if has_dot:
                    raise ValueError
                has_dot = True
            values.append(char)
    maybe_values = "".join(values).strip()
    maybe_units = "".join(units).strip()
    if not maybe_units:
        raise ValueError
    if has_dot:
        return (float(maybe_values), maybe_units)
    return (int(maybe_values, 10), maybe_units)


@task
def benchmark(
    context: Context,
    type_: Union[Type[UnitValue], Type[str], Literal["UnitValue", "str"]] = "str",
    *,
    mode: Literal["us", "ns"] = "us",
    count: Optional[int] = None,
) -> Union[UnitValue, Tuple[str, ...]]:
    if type_ == "UnitValue":
        type_ = UnitValue
    elif type_ == "str":
        type_ = str
    assert type_ in (str, UnitValue)
    python_bin = _.python_path(str, silent=True)
    fh = context.run(f"{python_bin} -m instruct benchmark {mode} {count or ''}", hide="stdout")
    assert fh is not None
    tests = []
    section = None
    for line in fh.stdout.strip().splitlines():
        with suppress(ValueError):
            name, val = (x.strip() for x in line.strip().split(":", 1))
            if val:
                if type_ is UnitValue:
                    v = UnitValue(name, _.parse_with_unit(val, silent=True))
                else:
                    v = (
                        f"{name}",
                        f"{val}",
                    )
                if section:
                    tests.append((section, *v))
                else:
                    tests.append(v)
                continue
        if line.strip().endswith(":"):
            line = line.strip()[:-1]
        section = line

    return tuple(tests)


@task
def verify_types(
    context: Context,
):
    python_bin = _.python_path(str, silent=True)
    context.run(f"{python_bin!s} -m mypy {_.project_name(context, silent=True)}")
    _.pre_commit(context, "ruff-check")


@task
def verify_style(
    context: Context,
):
    _.pre_commit(context, "ruff-format-check")
