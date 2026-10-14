"""Bounded regular-file acquisition and exclusive output in trusted directories. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: checked_path — line 39
# parameter: path — line 39
# variable: absolute — line 41
# variable: component — line 42
# definition: read_file — line 48
# parameter: maximum — line 48
# parameter: path — line 48
# variable: path — line 50
# variable: before — line 51
# variable: flags — line 54
# variable: descriptor — line 60
# variable: stream — line 61
# variable: opened — line 62
# variable: data — line 68
# variable: after — line 69
# definition: new_directory — line 81
# parameter: path — line 81
# variable: path — line 83
# definition: write_new — line 88
# parameter: data — line 88
# parameter: path — line 88
# variable: path — line 90
# variable: flags — line 91
# variable: descriptor — line 98
# variable: stream — line 99
# END CODE MAP

from __future__ import annotations

import os
import stat
from pathlib import Path

from .contracts import MAX_FILE, EvidenceError


def checked_path(path: Path) -> Path:
    """Reject existing symlink/reparse components; trusted parents remain an OS boundary."""
    absolute = path.absolute()
    for component in (absolute, *absolute.parents):
        if component.is_symlink() or component.is_junction():
            raise EvidenceError("linked_path_rejected")
    return absolute


def read_file(path: Path, maximum: int = MAX_FILE) -> bytes:
    """Read one stable regular descriptor, at most maximum bytes, never a device/FIFO/archive."""
    path = checked_path(path)
    before = path.stat()
    if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
        raise EvidenceError("file_type_or_size")
    flags = (
        os.O_RDONLY
        | getattr(os, "O_BINARY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    descriptor = os.open(path, flags)
    with os.fdopen(descriptor, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode) or (before.st_dev, before.st_ino) != (
            opened.st_dev,
            opened.st_ino,
        ):
            raise EvidenceError("source_changed")
        data = stream.read(maximum + 1)
        after = os.fstat(stream.fileno())
        if len(data) > maximum:
            raise EvidenceError("file_type_or_size")
        if (opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns) != (
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ) or len(data) != after.st_size:
            raise EvidenceError("source_changed")
    return data


def new_directory(path: Path) -> Path:
    """Create exactly one new private directory; never overwrite or recursively create parents."""
    path = checked_path(path)
    path.mkdir(mode=0o700)
    return path


def write_new(path: Path, data: bytes) -> None:
    """Write/fdatasync a new regular file, mode0600 on POSIX, preserving every existing target."""
    path = checked_path(path)
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_BINARY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(path, flags, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
