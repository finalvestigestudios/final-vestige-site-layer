"""Fail-closed post-link custody check for six-app verification report evidence.

This is an offline integrity witness, NOT release, entitlement or QD approval.
The publisher must preserve a suspect destination for independent review.
"""
from __future__ import annotations

import os
import stat
from pathlib import Path


class LinkWitnessError(ValueError):
    """Published report has not been shown to match the intended staged bytes."""


def _identity(info: os.stat_result) -> tuple[int, int]:
    return (info.st_dev, info.st_ino)


def verify_published_link(stage: str | Path, destination: str | Path, payload: bytes) -> None:
    """Prove the new hardlink refers to the staged ordinary file and exact bytes.

    The witness opens the final filename without following symbolic links when
    supported, reads through its own descriptor, and checks identity both
    before and after readback. A failed witness does NOT unlink either path.
    No network, execution, user data, or file modification occurs here.
    """
    if type(payload) is not bytes:
        raise LinkWitnessError("Invalid expected verification evidence")
    fd = None
    read_failed = False
    try:
        stage_info = os.stat(stage, follow_symlinks=False)
        dest_info = os.stat(destination, follow_symlinks=False)
        if not stat.S_ISREG(stage_info.st_mode) or not stat.S_ISREG(dest_info.st_mode):
            raise LinkWitnessError("Verification evidence is not an ordinary file")
        if _identity(stage_info) != _identity(dest_info) or stage_info.st_size != len(payload):
            raise LinkWitnessError("Published verification evidence identity differs")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(destination, flags)
        opened = os.fstat(fd)
        if (not stat.S_ISREG(opened.st_mode) or _identity(opened) != _identity(stage_info)
                or opened.st_size != len(payload)):
            raise LinkWitnessError("Published verification evidence changed")
        remaining = len(payload) + 1
        chunks = []
        while remaining:
            chunk = os.read(fd, min(remaining, 65536))
            if type(chunk) is not bytes:
                raise LinkWitnessError("Published verification evidence is unreadable")
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        if b"".join(chunks) != payload:
            raise LinkWitnessError("Published verification evidence bytes differ")
        after = os.fstat(fd)
        end_dest = os.stat(destination, follow_symlinks=False)
        end_stage = os.stat(stage, follow_symlinks=False)
        if (not stat.S_ISREG(end_dest.st_mode) or not stat.S_ISREG(end_stage.st_mode)
                or _identity(after) != _identity(stage_info)
                or _identity(end_dest) != _identity(stage_info)
                or _identity(end_stage) != _identity(stage_info)
                or after.st_size != len(payload) or end_dest.st_size != len(payload)):
            raise LinkWitnessError("Published verification evidence custody changed")
    except LinkWitnessError:
        raise
    except (OSError, ValueError, TypeError):
        read_failed = True
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
    if read_failed:
        raise LinkWitnessError("Could not verify published evidence safely")
