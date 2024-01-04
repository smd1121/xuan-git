from pathlib import Path


class Metadata:
    path: Path

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
        self.path = path
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
