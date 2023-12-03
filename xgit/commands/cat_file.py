import sys
import zlib
from typing import Optional

import typer
from typer import Option, Argument
from typing_extensions import Annotated

from xgit.types import Factory
from xgit.utils import check_exist, get_file_path


def cat_file(
    type: Annotated[Optional[str], Argument(help="要查看的对象的类型")] = None,
    obj: Annotated[Optional[str], Argument(help="要查看的对象的哈希值")] = None,
    show_size: Annotated[bool, Option("-s", help="显示对象的大小")] = False,
    show_type: Annotated[bool, Option("-t", help="显示对象的类型")] = False,
    exists: Annotated[bool, Option("-e", help="检查对象是否存在")] = False,
    pretty: Annotated[bool, Option("-p", help="按照对象的类型，显示对象的内容")] = False,
):
    """
    根据对象的哈希值，查看对象的内容。

    **Usages**:

    - xgit cat-file TYPE OBJ

    - xgit cat-file (-s | -t | -e | -p) OBJ
    """
    # 检查参数正确性
    if show_size + show_type + exists + pretty > 1:
        typer.echo("fatal: only one of the options can be used", err=True)
        sys.exit(1)

    if show_size | show_type | exists | pretty:
        # 这里一个比较特殊的地方是，我们需要同时支持两种用法。因此如果有选项，我们会把接收到的第一个参数当作 <obj>，而不是 <type>。
        type, obj = obj, type

        if obj is None:
            typer.echo("fatal: <obj> is required", err=True)
            sys.exit(1)

        if type is not None:
            typer.echo("fatal: <type> is not allowed with options", err=True)
            sys.exit(1)
    else:
        # 如果没有指定选项，那么我们就需要检查 <type> 和 <obj> 是否都存在。
        if obj is None or type is None:
            typer.echo("fatal: <type> and <obj> are both required if no option is not used", err=True)
            sys.exit(1)

    # `-e` 选项不打印内容，只返回 0 或者 1
    if exists:
        sys.exit(0 if check_exist(obj=obj) else 1)

    if not check_exist(obj=obj):
        typer.echo(f"fatal: Not a valid obj name {obj}", err=True)
        sys.exit(128)

    with get_file_path(obj=obj).open("rb") as f:
        data = zlib.decompress(f.read())

    hdr, data = data.split(b"\x00", maxsplit=1)
    type_, size = hdr.split(b" ", maxsplit=1)

    if show_size:
        typer.echo(size.decode())
        return

    if show_type:
        typer.echo(type_.decode())
        return

    if pretty:
        Factory.get_obj(data=data, obj_type=type_).print()
        return

    assert type is not None
    if type_.decode() != type:
        typer.echo(f"fatal: obj {obj} is of type {type_!r}, not {type!r}", err=True)
        sys.exit(128)
    sys.stdout.buffer.write(data)
