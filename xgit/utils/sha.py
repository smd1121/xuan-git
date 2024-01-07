import zlib
import hashlib

from xgit.utils.utils import find_repo, get_object
from xgit.utils.constants import GIT_DIR


def hash_file(file: str, write: bool = False) -> str:
    with open(file, "rb") as f:
        data = f.read()
    return do_hash_object(data, "blob", write)


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


def extract_data(object_id: str) -> bytes:
    with get_object(obj=object_id).open("rb") as f:
        return zlib.decompress(f.read())
