import hashlib
from typing import Optional

from xgit.utils.utils import find_repo, get_repo_file, timestamp_to_str
from xgit.types.metadata import Metadata
from xgit.utils.constants import GIT_DIR


def print_bytes(data, group_size=4, group_each_line=6):
    def is_printable(byte):
        return 32 <= byte <= 126

    byte_each_line = group_size * group_each_line

    n = len(data)
    for i in range(0, n, byte_each_line):
        line = data[i : i + byte_each_line]
        for j in range(0, len(line), group_size):
            group = line[j : j + group_size]
            print("0x" + "".join(f"{byte:02x}" for byte in group).upper(), end=" ")
        print()

        for j in range(0, len(line), group_size):
            group = line[j : j + group_size]
            print("   ", end="")
            print(" ".join(chr(byte) if is_printable(byte) else "*" for byte in group), end=" ")
        print("\n")


class IndexEntry:
    class Flag:
        assume_valid: bool
        extended: bool
        stage: int
        name_length: int

        def __init__(self, assume_valid, extended, stage, name_length):
            self.assume_valid = assume_valid
            self.extended = extended
            self.stage = stage
            self.name_length = name_length

        @staticmethod
        def from_bytes(data: bytes):
            assert len(data) == 2
            flag = int.from_bytes(data, "big")
            assume_valid = flag & 0x8000 != 0
            extended = flag & 0x4000 != 0
            stage = (flag & 0x3000) >> 12
            name_length = flag & 0x0FFF
            return IndexEntry.Flag(assume_valid, extended, stage, name_length)

        def to_bytes(self) -> bytes:
            data = 0
            if self.assume_valid:
                data |= 0x8000
            if self.extended:
                data |= 0x4000
            data |= (self.stage << 12) & 0x3000
            data |= self.name_length
            return data.to_bytes(2, "big")

        def __rich_repr__(self):
            yield "assume_valid", self.assume_valid
            yield "extended", self.extended
            yield "stage", self.stage
            yield "name_length", self.name_length

    metadata: Metadata
    sha: str
    flags: Flag
    extended_flags: Optional[bytes]
    file_name: str

    def __init__(
        self,
        ctime_s,
        ctime_ns,
        mtime_s,
        mtime_ns,
        dev,
        inode,
        mode,
        uid,
        gid,
        file_size,
        sha,
        flags,
        extended_flags,
        file_name,
    ):
        self.metadata = Metadata(
            get_repo_file(file_name), ctime_s, ctime_ns, mtime_s, mtime_ns, dev, inode, mode, uid, gid, file_size
        )
        self.sha = sha
        self.flags = flags
        self.extended_flags = extended_flags
        self.file_name = file_name

    @staticmethod
    def parse(data: bytes) -> tuple["IndexEntry", bytes]:
        ctime_s = int.from_bytes(data[:4], "big")
        ctime_ns = int.from_bytes(data[4:8], "big")
        mtime_s = int.from_bytes(data[8:12], "big")
        mtime_ns = int.from_bytes(data[12:16], "big")
        dev = int.from_bytes(data[16:20], "big")
        inode = int.from_bytes(data[20:24], "big")
        mode = int.from_bytes(data[24:28], "big")
        uid = int.from_bytes(data[28:32], "big")
        gid = int.from_bytes(data[32:36], "big")
        file_size = int.from_bytes(data[36:40], "big")
        sha = data[40:60].hex()
        flags = IndexEntry.Flag.from_bytes(data[60:62])

        entry_len = 62

        # if flags.extended == True, then there is a 16-bit extended flag
        if flags.extended:
            extended_flags = data[62:64]
            entry_len += 2
        else:
            extended_flags = None

        if flags.name_length < 0xFFF:
            file_name = data[entry_len : entry_len + flags.name_length]
            assert data[entry_len + flags.name_length] == 0
            entry_len += flags.name_length + 1
        else:
            # if name_length >= 0xFFF, then find `\x00` to get the file name
            file_name, _ = data[entry_len:].split(b"\x00", maxsplit=1)
            entry_len += len(file_name) + 1

        entry_len = (entry_len + 7) // 8 * 8  # aligned to 8 bytes
        rest = data[entry_len:]  # remove padding

        return (
            IndexEntry(
                ctime_s,
                ctime_ns,
                mtime_s,
                mtime_ns,
                dev,
                inode,
                mode,
                uid,
                gid,
                file_size,
                sha,
                flags,
                extended_flags,
                file_name.decode(),
            ),
            rest,
        )

    def to_bytes(self) -> bytes:
        entry = self.metadata.ctime_s.to_bytes(4, "big")
        entry += self.metadata.ctime_ns.to_bytes(4, "big")
        entry += self.metadata.mtime_s.to_bytes(4, "big")
        entry += self.metadata.mtime_ns.to_bytes(4, "big")
        entry += self.metadata.dev.to_bytes(4, "big")
        entry += self.metadata.inode.to_bytes(4, "big")
        entry += self.metadata.mode.to_bytes(4, "big")
        entry += self.metadata.uid.to_bytes(4, "big")
        entry += self.metadata.gid.to_bytes(4, "big")
        entry += self.metadata.file_size.to_bytes(4, "big")
        entry += bytes.fromhex(self.sha)
        entry += self.flags.to_bytes()
        if self.extended_flags is not None:
            entry += self.extended_flags
        entry += self.file_name.encode()
        entry += b"\x00"

        # padding to 8 bytes
        padding = (8 - len(entry) % 8) % 8
        entry += b"\x00" * padding

        return entry

    # 以下用于 show-index 输出

    verbose: bool = False

    def __rich_repr__(self):
        if not self.verbose:
            yield "file_name", self.file_name
            yield "ctime", timestamp_to_str(self.metadata.ctime_s, self.metadata.ctime_ns)
            yield "mtime", timestamp_to_str(self.metadata.mtime_s, self.metadata.mtime_ns)
            yield "sha", self.sha
        else:
            yield "metadata", self.metadata
            yield "sha", self.sha
            yield "flags", self.flags
            yield "extended_flags", self.extended_flags
            yield "file_name", self.file_name


class Index:
    version: int
    entry_count: int
    entries: list[IndexEntry]
    extensions: bytes

    def __init__(self, data: Optional[bytes] = None):
        if data is None:
            self.version = 2
            self.entry_count = 0
            self.entries = []
            self.extensions = b""
        else:
            self.version = int.from_bytes(data[4:8], "big")
            self.entry_count = int.from_bytes(data[8:12], "big")
            self.entries = []
            data = data[12:]
            for _ in range(self.entry_count):
                entry, data = IndexEntry.parse(data)
                self.entries.append(entry)
            self.extensions = data[:-20]

    def to_bytes(self) -> bytes:
        index = b"DIRC"
        index += self.version.to_bytes(4, "big")
        index += self.entry_count.to_bytes(4, "big")
        index += b"".join(entry.to_bytes() for entry in self.entries)
        index += self.extensions
        index += hashlib.sha1(index).digest()
        return index

    def __rich_repr__(self):
        yield "version", self.version
        yield "entry_count", self.entry_count
        yield "entries", self.entries
        yield "extensions", self.extensions


def get_index() -> Index:
    """
    如果 repo 不存在，报错退出
    如果 index 不存在，返回没有 entry 的 Index 对象
    """
    index_path = find_repo() / GIT_DIR / "index"
    if not index_path.exists():
        return Index()
    with index_path.open("rb") as f:
        data = f.read()
        assert data[-20:] == hashlib.sha1(data[:-20]).digest()
        return Index(data)
