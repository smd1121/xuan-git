import sys
from typing import List, Tuple

import typer


class Blob:
    data: str

    def __init__(self, data: bytes):
        self.data = data.decode()

    def __str__(self):
        return self.data

    def print(self):
        sys.stdout.buffer.write(self.data.encode())


class TreeEntry:
    filemode: str
    filename: str
    obj_type: str
    sha: str

    FILEMODE_TO_OBJ_TYPE = {
        "100644": "blob",
        "100755": "blob",
        "120000": "blob",
        "160000": "commit",
        "040000": "tree",
    }

    def __init__(self, filemode: bytes, filename: bytes, sha: bytes):
        self.filemode = filemode.decode()
        if self.filemode == "40000":
            self.filemode = "040000"
        self.filename = filename.decode()
        self.sha = sha.hex()
        self.obj_type = self.FILEMODE_TO_OBJ_TYPE[self.filemode]

    def __str__(self):
        return f"{self.filemode} {self.obj_type} {self.sha}\t{self.filename}"

    @staticmethod
    def parse(data: bytes) -> Tuple["TreeEntry", bytes]:
        filemode, data = data.split(b" ", maxsplit=1)
        filename, data = data.split(b"\x00", maxsplit=1)
        sha, data = data[:20], data[20:]
        return TreeEntry(filemode, filename, sha), data


class Tree:
    entries: List[TreeEntry]

    def __init__(self, data: bytes):
        self.entries = []
        while data:
            entry, data = TreeEntry.parse(data)
            self.entries.append(entry)

    def __str__(self):
        return "\n".join(map(str, self.entries))

    def print(self):
        return typer.echo(str(self))


class Factory:
    TYPE_TO_CLASS = {
        b"blob": Blob,
        b"tree": Tree,
    }

    @staticmethod
    def get_obj(data: bytes, obj_type: bytes):
        if obj_type not in Factory.TYPE_TO_CLASS:
            typer.echo(f"Unknown type {obj_type.decode()}", err=True)
            sys.exit(1)
        return Factory.TYPE_TO_CLASS[obj_type](data)
