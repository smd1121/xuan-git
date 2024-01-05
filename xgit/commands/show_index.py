from typing import Optional
from pathlib import Path

from typer import Option, Argument
from rich.pretty import pprint
from typing_extensions import Annotated

from xgit.types.index import get_index
from xgit.utils.utils import find_repo


def show_index(
    files: Annotated[Optional[list[str]], Argument(help="要展示的 entry，默认展示全部")] = None,
    verbose: Annotated[bool, Option("-v", "--verbose", help="以详细模式展示 entry")] = False,
):
    """
    以可读的方式输出 index。只打印当前目录和子目录下在的 index 中的 entry，不打印父目录中的其他 entry。
    这并非 git 本身支持的功能，只是为了方便调试和展示结果。
    """
    index = get_index()

    cwd = Path.cwd().resolve()
    repo = find_repo().resolve()

    # 如果指定了 files，则只打印这些文件的 entry
    if files:
        file_paths = [Path(cwd / f).resolve() for f in files]
        index.entries = [e for e in index.entries if repo / e.file_name in file_paths]

    # 只打印当前目录和子目录下在的 index 中的 entry
    index.entries = [e for e in index.entries if Path(repo / e.file_name).is_relative_to(cwd)]

    if verbose:
        for entry in index.entries:
            entry.verbose = True

    pprint(index)
