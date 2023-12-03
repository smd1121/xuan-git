import sys
from pathlib import Path

import typer

from xgit.constants import GIT_DIR


def find_repo() -> Path:
    """
    从当前目录开始，逐级向上查找 git 仓库。

    如果找到，则返回仓库的目录；否则报错退出。
    """
    path = Path.cwd().absolute()
    while path.parent != path:
        if (path / GIT_DIR).is_dir():
            return path
        path = path.parent
    typer.echo("fatal: not a git repository (or any of the parent directories)", err=True)
    sys.exit(128)


def get_file_path(obj: str):
    repo_dir = find_repo()
    return repo_dir / GIT_DIR / "objects" / obj[:2] / obj[2:]


def check_exist(obj: str) -> bool:
    object_file = get_file_path(obj)
    return object_file.exists()
