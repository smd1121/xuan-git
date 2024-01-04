from pathlib import Path

import typer
from typer import Argument
from typing_extensions import Annotated

from xgit.utils.constants import GIT_DIR


def init(directory: Annotated[str, Argument(help="要初始化 git 仓库的目录")] = "."):
    """
    初始化一个 git 仓库。
    """
    dir_path: Path = Path(directory)
    git_dir: Path = dir_path / GIT_DIR

    git_dir.mkdir(exist_ok=True)
    (git_dir / "objects").mkdir(exist_ok=True)
    (git_dir / "refs").mkdir(exist_ok=True)
    (git_dir / "refs" / "heads").mkdir(exist_ok=True)
    (git_dir / "refs" / "tags").mkdir(exist_ok=True)

    if not (git_dir / "HEAD").exists():
        with (git_dir / "HEAD").open("w") as f:
            f.write("ref: refs/heads/master\n")

    typer.echo(f"Initialized empty Git repository in {git_dir.absolute()}")
