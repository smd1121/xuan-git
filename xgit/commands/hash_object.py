import sys
from typing import Optional

import typer
from typer import Option, Argument
from typing_extensions import Annotated

from xgit.utils.sha import hash_file, do_hash_object


def hash_object(
    files: Annotated[Optional[list[str]], Argument(help="要计算哈希值的文件")] = None,
    write: Annotated[bool, Option("-w", help="将内容写入到对象数据库中")] = False,
    stdin: Annotated[bool, Option("--stdin", help="从标准输入读取内容")] = False,
    obj_type: Annotated[str, Option("-t", help="指定要创建的对象类型")] = "blob",
):
    """
    计算对象的哈希值；如果指定了 -w，则将内容写入到对象数据库中。
    """
    if stdin:
        data = sys.stdin.read().encode()
        object_id = do_hash_object(data, obj_type, write)
        typer.echo(object_id)

    if not files:
        return

    for file in files:
        object_id = hash_file(file, write)
        typer.echo(object_id)
