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

    @staticmethod
    def from_cache_info(path, mode):
        return Metadata(
            path=path,
            mode=mode,
            ctime_s=0,
            ctime_ns=0,
            mtime_s=0,
            mtime_ns=0,
            dev=0,
            inode=0,
            uid=0,
            gid=0,
            file_size=0,
        )

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

    @staticmethod
    def get_metadata(path: Path):
        assert path.exists()
        stat = path.stat()
        return Metadata(
            path,
            int(stat.st_ctime),
            stat.st_ctime_ns % 10**9,
            int(stat.st_mtime),
            stat.st_mtime_ns % 10**9,
            stat.st_dev,
            stat.st_ino,
            stat.st_mode,
            stat.st_uid,
            stat.st_gid,
            stat.st_size,
        )

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, Metadata)
        return (
            self.ctime_s == __value.ctime_s
            and self.ctime_ns == __value.ctime_ns
            and self.mtime_s == __value.mtime_s
            and self.mtime_ns == __value.mtime_ns
        )
