import sys
import zlib
import hashlib
from typing import Optional

import typer
from typer import Option, Argument
from typing_extensions import Annotated

from xgit.utils.utils import find_repo
from xgit.utils.constants import GIT_DIR


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
        with open(file, "rb") as f:
            data = f.read()
        object_id = do_hash_object(data, obj_type, write)
        typer.echo(object_id)


def do_hash_object(data: bytes, obj_type: str, write: bool) -> str:
    """
    计算对象的哈希值；如果 write 为 True，则将内容写入到对象数据库中。

    在 Git 中，对象的哈希值的计算依据以及存入文件的内容是这样的一个 bytes：
    一个指定对象类型的字符串 + 空格 + 对象内容的长度 + \x00 + 对象内容
    参见 https://stackoverflow.com/questions/22968856

    在存储时，会将上述内容进行 zlib 压缩，然后计算 SHA-1 哈希值，作为文件名。
    为了避免在一个目录下存储过多的文件导致性能问题，会将文件名的前两位作为目录名。
    """

    result = obj_type.encode() + b" " + str(len(data)).encode() + b"\x00" + data
    object_id = hashlib.sha1(result).hexdigest()

    if write:
        repo_dir = find_repo()
        file = repo_dir / GIT_DIR / f"objects/{object_id[:2]}/{object_id[2:]}"
        file.parent.mkdir(exist_ok=True)
        with open(file, "wb") as out:
            out.write(zlib.compress(result))

    return object_id
