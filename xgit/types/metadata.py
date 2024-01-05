from pathlib import Path


class Metadata:
    _path: Path

    ctime_s: int
    ctime_ns: int
    mtime_s: int
    mtime_ns: int
    dev: int
    inode: int
    mode: int
    uid: int
    gid: int
    file_size: int

    def __init__(
        self,
        path: Path,
        ctime_s: int,
        ctime_ns: int,
        mtime_s: int,
        mtime_ns: int,
        dev: int,
        inode: int,
        mode: int,
        uid: int,
        gid: int,
        file_size: int,
    ):
        self._path = path
        self.ctime_s = ctime_s
        self.ctime_ns = ctime_ns
        self.mtime_s = mtime_s
        self.mtime_ns = mtime_ns
        self.dev = dev
        self.inode = inode
        self.mode = mode
        self.uid = uid
        self.gid = gid
        self.file_size = file_size

    def __rich_repr__(self):
        yield "ctime_s", self.ctime_s
        yield "ctime_ns", self.ctime_ns
        yield "mtime_s", self.mtime_s
        yield "mtime_ns", self.mtime_ns
        yield "dev", self.dev
        yield "inode", self.inode
        yield "mode", self.mode
        yield "uid", self.uid
        yield "gid", self.gid
        yield "file_size", self.file_size
