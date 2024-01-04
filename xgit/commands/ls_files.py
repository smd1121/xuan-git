from pathlib import Path

import typer
from typer import Option
from typing_extensions import Annotated

from xgit.types.index import get_index
from xgit.utils.utils import find_repo


def ls_files(
    full_name: Annotated[bool, Option("--full-name", help="输出相对于项目根目录，而非当前目录")] = False,
):
    """
    输出 index 中在当前目录下的所有文件
    """
    index = get_index()
    for entry in index.entries:
        f = find_repo() / entry.file_name
        cwd = Path.cwd()

        if f.is_relative_to(cwd):
            if full_name:
                typer.echo(entry.file_name)
            else:
                typer.echo(f.relative_to(cwd))
