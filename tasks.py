import json
import os
import shutil
import types
import base64
import builtins
import sys
from contextlib import suppress, contextmanager
from pathlib import Path
from typing import Type, Union, Dict, Tuple, Iterable, TypeVar

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


from invoke.context import Context
from tasksupport import task, first, InvertedMapping, trim, truncate

_ = types.SimpleNamespace()
this = sys.modules[__name__]

DEFAULT_FORMAT = "lines"


def perror(*args, file=None, **kwargs):
    if file is None:
        file = sys.stderr
    return print(*args, file=file, **kwargs)


@contextmanager
def create_environment(*, copy_os_environ: bool = False, **kwargs: str) -> Dict[str, str]:
    """
    Returns some common values for Docker builds
    """
    environment = {
        **(os.environ if copy_os_environ else {}),
        "NO_COLOR": "1",
        "COMPOSE_DOCKER_CLI_BUILD": "1",
        "BUILDX_EXPERIMENTAL": "1",
        "BUILDX_GIT_LABELS": "full",
        "BUILDKIT_PROGRESS": "plain",
        "DOCKER_BUILDKIT": "1",
        "COMPOSE_PROJECT_NAME": _.project_name(silent=True),
        **kwargs,
    }
    return environment


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


@task
def branch_name(context: Context) -> str:
    with suppress(KeyError):
        return os.environ["GITHUB_REF_NAME"]
    here = this._.project_root(Path, silent=True)
    if (here / ".git").is_dir():
        with suppress(FileNotFoundError):
            return context.run(f"git -C {here!s} branch --show-current", hide="both").stdout.strip()
        with open(here / ".git" / "HEAD") as fh:
            for line in fh:
                if line.startswith("ref:"):
                    _, line = (x.strip() for x in line.split(":", 1))
                if line.startswith("refs/heads/"):
                    return line.removeprefix("refs/heads/")
    raise ValueError("Unable to determine branch name!")


T = TypeVar("T")


def window(iterable: Iterable[T]) -> Iterable[Tuple[T, T]]:
    g = iter(iterable)
    item = next(g)
    for next_item in g:
        yield item, next_item
        next_item = item


@task
def update_changes(context: Context):
    context.run(
        r"git-changelog -I CHANGES.rst  -g '^Version (?P<version>[\d\.]+)' -m '.. |Changes|' -t path:CHANGES.rst.template -F '82c264ca9a125317945e4aa3f581f009b49014ad...' -i -o CHANGES.rst"
    )


@task
def setup_metadata() -> Dict[str, str]:
    with open(_.project_root(Path, silent=True) / "setup.cfg") as fh:
        in_multiline = False
        in_metadata = False
        values = None
        key = None
        mapping = {}
        for line in fh:
            if line.startswith("[metadata]"):
                in_metadata = True
                continue
            if line.startswith("[") and in_metadata:
                in_metadata = False
            if in_metadata:
                if "=" in line and in_multiline:
                    in_multiline = False
                    mapping[key] = values
                    values = None
                if in_multiline:
                    values.append(line.strip())
                    continue
                key, value = [x.strip() for x in line.split("=", 1)]
                if not value:
                    in_multiline = True
                    values = []
                    continue
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


@task
def build(context: Context) -> Tuple[Path, ...]:
    python_bin = _.python_path(str)
    context.run(f"{python_bin} -m build")
    return tuple(Path("dist").iterdir())


# @task
# def get_tags_from(context: Context, image_name: str) -> Iterable[str]:
#     """
#     Given an image url, return the repo tags
#     """
#     try:
#         result = context.run(f"docker inspect {image_name}", hide="both")
#     except UnexpectedExit as e:
#         if "Error: No such object:" in e.result.stderr:
#             context.run(f"docker pull {image_name}", env=compose_environ())
#             result = context.run(f"docker inspect {image_name}", hide="both")
#         else:
#             raise
#     image = json.loads(result.stdout)
#     results = []
#     for match in image:
#         results.extend(match["RepoTags"])
#     return results


@task
def project_root(
    type: Union[Type[str], Type[Path], Literal["str", "Path"]] = "str"
) -> Union[str, Path]:
    """
    Get the absolute path of the project root assuming tasks.py is in the repo root.
    """
    if isinstance(type, builtins.type):
        type = type.__name__
    assert type in ("str", "Path"), f"{type} may be str or Path"
    root = Path(__file__).resolve().parent
    if type == "str":
        return str(root)
    return root


@task
def python_path(
    type_name: Literal["str", "Path", str, Path] = "str",
    *,
    skip_venv: bool = False,
) -> Union[str, Path]:
    """
    Return the best python to use
    """
    if isinstance(type_name, type):
        type_name = type_name.__name__
    assert type_name in ("Path", "str")
    root = Path(__file__).resolve().parent
    python = root / "python" / "bin" / "python"
    if not python.exists():
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
    swap_venv_stage: str = None,
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
