import sys
import contextlib
from pathlib import Path

import typer
from typer import Option, Argument
from typing_extensions import Optional, Annotated

from xgit.types.index import Index, get_index
from xgit.utils.utils import find_repo


def update_index(
    files: Annotated[Optional[list[str]], Argument(help="要更新的文件")] = None,
    add: Annotated[bool, Option("--add", help="如果文件在暂存区中不存在，则加入暂存区")] = False,
    remove: Annotated[bool, Option("--remove", help="如果文件在暂存区存在，但在本地不存在，则从暂存区移除")] = False,
    force_remove: Annotated[bool, Option("--force-remove", help="从暂存区移除文件，即使文件在本地存在")] = False,
    refresh: Annotated[bool, Option("--refresh", help="检查当前 index 中的文件是否需要 merge 或 update")] = False,
    verbose: Annotated[bool, Option("--verbose", help="详细输出添加和删除的文件")] = False,
    cacheinfo: Annotated[
        Optional[list[str]], Option("--cacheinfo", help="与 `--add` 一同使用，用 `<mode>,<object>,<path>` 指定一个 blob 加入暂存区")
    ] = None,
):
    """
    更新暂存区
    """
    files = files or []

    # 如果没有 git repo，会报错
    find_repo()

    # === 检查参数正确性 ===
    # add, remove, force_remove, refresh 互斥
    if add + remove + force_remove + refresh > 1:
        typer.echo("fatal: only one of the options can be used", err=True)
        sys.exit(1)

    # refresh 不能与 files 同时使用
    if refresh and files:
        typer.echo("fatal: --refresh cannot be used with files", err=True)
        sys.exit(1)

    # cacheinfo 必须与 add 同时使用
    if cacheinfo and not add:
        typer.echo("fatal: --cacheinfo can only be used with --add", err=True)
        sys.exit(1)

    # 如果有不在当前仓库中的文件，报错
    repo = find_repo().resolve()
    for f in files:
        if not Path(f).absolute().is_relative_to(repo):
            typer.echo(f"fatal: '{f}' is outside repository at '{repo}'", err=True)
            sys.exit(128)

    # files 中的目录需要被忽略
    dir_in_files = [f for f in files if Path(f).is_dir()]
    for f in dir_in_files:
        typer.echo(f"Ignoring path '{f}'", err=True)

    # 实际需要处理的 files
    files = [f for f in files if f not in dir_in_files]

    # === 执行操作 ===
    sys.exit(
        _update_index(
            files=files,
            add=add,
            remove=remove,
            force_remove=force_remove,
            refresh=refresh,
            verbose=verbose,
            cacheinfo=cacheinfo,
        )
    )


def _update_index(
    files: list[str],
    add: bool,
    remove: bool,
    force_remove: bool,
    refresh: bool,
    verbose: bool,
    cacheinfo: Optional[list[str]],
) -> int:
    with working_index() as index:
        if refresh:
            return refresh_index(index=index)

        if not (add or remove or force_remove):
            return update(index=index, files=files, add_if_absent=False, verbose=verbose)

        if add:
            exit_code = update(index=index, files=files, add_if_absent=True, verbose=verbose)
            if exit_code != 0:
                return exit_code
            return add_cacheinfo(index=index, cacheinfo=cacheinfo, verbose=verbose)

        if remove:
            return remove_files(index=index, files=files, force=False, verbose=verbose)

        if force_remove:
            return remove_files(index=index, files=files, force=True, verbose=verbose)

        assert False, "unreachable"


@contextlib.contextmanager
def working_index():
    """
    获取 index，执行完毕后写回
    xgit 预期不会抛出异常。因此如果抛出异常，不写回
    """
    index = get_index()
    yield index
    index.write()


def refresh_index(index: Index) -> int:
    """
    update-index --refresh: 刷新 index 中的 metadata，报告需要 update 的文件

    对于 index 中的每个 entry：
        检查其 metadata 是否与本地一致
        如果不一致，检查文件 sha 是否一致：如果一致，更新 metadata；否则报告 needs update

    我们暂时忽略 merge 相关的状态

    如果有 needs update 的文件，返回 1；否则返回 0
    """
    needs_update = index.refresh()
    for f in needs_update:
        typer.echo(f"{f}: needs update")
    return 0 if len(needs_update) == 0 else 1


def update(index: Index, files: list[str], add_if_absent: bool, verbose: bool) -> int:
    for f in files:
        ret_code = do_update(index=index, f=f, add_if_absent=add_if_absent)
        if ret_code != 0:
            typer.echo(f"fatal: Unable to process path {f}", err=True)
            return ret_code
        if verbose:
            typer.echo(f"add '{f}'")
    return 0


def do_update(index: Index, f: str, add_if_absent: bool = False) -> int:
    file_path = Path(f)

    if not file_path.exists():
        typer.echo(f"error: {f}: does not exist and --remove not passed", err=True)
        return 128

    if index.update(file_path, add_if_absent):
        return 0
    if not add_if_absent:
        typer.echo(f"error: {f}: cannot add to the index - missing --add option?", err=True)
        return 128

    assert False, "update-index --add should not fail here"


def add_cacheinfo(index: Index, cacheinfo: Optional[list[str]], verbose: bool) -> int:
    cacheinfo = cacheinfo or []
    for cache_info in cacheinfo:
        mode, obj, path = cache_info.split(",")
        ret_code = do_add_cacheinfo(index=index, mode=mode, obj=obj, path=path)

        if ret_code != 0:
            typer.echo(f"fatal: git update-index: --cacheinfo cannot add {path}")
            return ret_code
        if verbose:
            typer.echo(f"add '{path}'")

    return 0


def do_add_cacheinfo(index: Index, mode: str, obj: str, path: str) -> int:
    """
    update-index --add --cacheinfo <mode>,<object>,<path>

    将一个 blob 加入暂存区
    """

    def is_path_valid(path: str) -> bool:
        """
        path 不应以 / 开头或结尾，不应包含连续的 //，或者单独的 . 和 ..
        """
        parts = path.split("/")
        return not ("" in parts or "." in parts or ".." in parts)

    def find_path_conflict(path: str) -> Optional[str]:
        """
        path 不应与现有 index 产生冲突
        具体来说，如果 index 中有 a，那么 a/b 非法，因为 a 是一个已知文件，但 a/b 暗示 a 是一个目录
        """
        parts = path.split("/")

        for i in range(1, len(parts)):
            prefix = "/".join(parts[:i])
            if prefix in index.entry_paths():
                return prefix

        return None

    if not is_path_valid(path):
        typer.echo(f"error: Invalid path '{path}'", err=True)
        return 128

    conflict = find_path_conflict(path)
    if conflict is not None:
        typer.echo(f"error: '{conflict}' appears as both a file and as a directory", err=True)
        return 128

    index.add_cacheinfo(mode, obj, path)
    return 0


def remove_files(index: Index, files: list[str], force: bool, verbose: bool) -> int:
    for f in files:
        file_path = Path(f)
        if not file_path.exists() or force:
            removed = index.remove(file_path)
            if removed and verbose:
                typer.echo(f"remove '{f}'")
    return 0
