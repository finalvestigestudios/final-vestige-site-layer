"""Defensive structural inspection of a Windows AMD64 application image.

This is a *format sanity check*, not malware scanning, Authenticode verification,
or proof that the program will run. Real-machine smoke and independent release
approval remain separate gates. No binary content is executed here.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
import stat
import struct
from pathlib import Path

from pe_digest_custody_r493 import verify_pe_digest_stream
from pe_directory_guard_r494 import PEDataDirectoryError, validate_pe_directories


class PEFormatError(ValueError):
    """The candidate does not meet the desktop suite PE32+ shape contract."""


@contextmanager
def _private_pe_stream(stream):
    """Preserve stream ownership and cleanup across inspection failures.

    The caller sanitizes unexpected errors *outside* an active exception
    handler: a generator-based context manager cannot reliably clear private
    exception chains from faults thrown into its suspended ``yield``.
    If __enter__ fails, explicitly close the unowned stream; after a successful
    enter, the stream context owns cleanup. Never swallow interrupts.
    """
    entered = False
    try:
        with stream:
            entered = True
            yield stream
    finally:
        if not entered:
            try:
                stream.close()
            except Exception:
                # A broken close cannot be reported with client-derived text.
                # The original failure already rejects this candidate.
                pass


def _u16(raw: bytes, at: int) -> int:
    return struct.unpack_from("<H", raw, at)[0]


def _u32(raw: bytes, at: int) -> int:
    return struct.unpack_from("<I", raw, at)[0]


def _read_at(stream, start: int, count: int, length: int) -> bytes:
    if start < 0 or count < 0 or start + count > length:
        raise PEFormatError("PE header or section extends beyond file")
    stream.seek(start)
    data = stream.read(count)
    if len(data) != count:
        raise PEFormatError("PE file changed or was truncated during inspection")
    return data


def _power_of_two(value: int) -> bool:
    return value > 0 and value & (value - 1) == 0


def verify_amd64_pe(path: str | Path, *, expected_sha256: str | None = None) -> None:
    """Reject truncated, non-AMD64, DLL/driver and malformed executable images.

    Deliberately restrict the expected PyInstaller --windowed output to normal
    GUI/console PE32+ files with a bounded section table and executable section.
    Do not treat a structurally valid PE as safe or signed.
    """
    filename = Path(path)
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = None
    try:
        fd = os.open(filename, flags)
    except OSError:
        # OS exception messages can contain private candidate directories.
        pass
    if fd is None:
        raise PEFormatError("Cannot open candidate without following file symlinks")
    prestream_fault = False
    try:
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode):
            raise PEFormatError("Candidate is not a regular file")
        # Ownership moves to the stream only AFTER fdopen succeeds.
        stream = os.fdopen(fd, "rb")
    except BaseException as exc:
        # fstat/fdopen can fail or be interrupted before ownership transfer.
        # Never abandon the raw candidate descriptor on any of those paths.
        try:
            os.close(fd)
        except OSError:
            pass
        if isinstance(exc, Exception) and not isinstance(exc, PEFormatError):
            prestream_fault = True
        else:
            raise
    if prestream_fault:
        raise PEFormatError("Cannot inspect candidate file")
    stream_fault = False
    try:
        with _private_pe_stream(stream):
            length = metadata.st_size
            if length < 512:
                raise PEFormatError("Truncated Windows image")
            dos = _read_at(stream, 0, 64, length)
            if dos[:2] != b"MZ":
                raise PEFormatError("Missing DOS MZ signature")
            pe_offset = _u32(dos, 0x3C)
            if not 64 <= pe_offset <= 65536:
                raise PEFormatError("Unsafe PE header offset")
            nt = _read_at(stream, pe_offset, 24, length)
            if nt[:4] != b"PE\x00\x00":
                raise PEFormatError("Missing NT PE signature")
            machine = _u16(nt, 4)
            section_count = _u16(nt, 6)
            optional_bytes = _u16(nt, 20)
            characteristics = _u16(nt, 22)
            if machine != 0x8664:
                raise PEFormatError("Expected Windows AMD64 executable")
            if not 1 <= section_count <= 96:
                raise PEFormatError("Invalid PE section count")
            if not 112 <= optional_bytes <= 4096:
                raise PEFormatError("Invalid PE32+ optional-header size")
            if not characteristics & 0x0002 or characteristics & (0x2000 | 0x1000):
                raise PEFormatError("PE is not a user-mode executable image")
            optional_start = pe_offset + 24
            section_start = optional_start + optional_bytes
            section_table_bytes = section_count * 40
            sections_end = section_start + section_table_bytes
            if sections_end > length:
                raise PEFormatError("PE section table is truncated")
            optional = _read_at(stream, optional_start, optional_bytes, length)
            if _u16(optional, 0) != 0x20B:
                raise PEFormatError("Expected PE32+, not PE32")
            entry_rva = _u32(optional, 16)
            if entry_rva == 0:
                raise PEFormatError("Executable has no entry point")
            section_align = _u32(optional, 32)
            file_align = _u32(optional, 36)
            if (not _power_of_two(file_align) or not _power_of_two(section_align)
                    or section_align < file_align):
                raise PEFormatError("Invalid PE image/file alignments")
            image_size = _u32(optional, 56)
            headers_size = _u32(optional, 60)
            if not sections_end <= headers_size <= length or image_size < headers_size:
                raise PEFormatError("Invalid PE image/header extent")
            if _u16(optional, 68) not in (2, 3):
                raise PEFormatError("Expected user-mode GUI or console subsystem")
            if (headers_size % file_align or image_size % section_align
                    or entry_rva >= image_size):
                raise PEFormatError("Misaligned image extents or entry point outside image")
            table = _read_at(stream, section_start, section_table_bytes, length)
            virtual_ranges: list[tuple[int, int]] = []
            file_ranges: list[tuple[int, int]] = []
            backed_virtual_ranges: list[tuple[int, int]] = []
            backed_entry = False
            for offset in range(0, len(table), 40):
                virtual_bytes = _u32(table, offset + 8)
                virtual_rva = _u32(table, offset + 12)
                raw_bytes = _u32(table, offset + 16)
                raw_offset = _u32(table, offset + 20)
                section_flags = _u32(table, offset + 36)
                # R370: release candidates must never request pages that are both
                # writable and executable. Check EVERY mapped section, including
                # non-entry and zero-filled sections; a valid entry point alone
                # does not make an unsafe PE suitable for review/distribution.
                # This is a conservative format policy, not an AV or signing check.
                if section_flags & 0xA0000000 == 0xA0000000:
                    raise PEFormatError("PE section requests writable executable memory")
                mapped_bytes = max(virtual_bytes, raw_bytes)
                if (not mapped_bytes or virtual_rva < headers_size
                        or virtual_rva % section_align
                        or virtual_rva + mapped_bytes > image_size):
                    raise PEFormatError("Invalid mapped PE section extent")
                virtual_ranges.append((virtual_rva, virtual_rva + mapped_bytes))
                if raw_bytes:
                    if (raw_offset < headers_size or raw_offset % file_align
                            or raw_bytes % file_align
                            or raw_offset + raw_bytes > length):
                        raise PEFormatError("PE section bytes unaligned or outside image")
                    file_ranges.append((raw_offset, raw_offset + raw_bytes))
                    # An entry in executable zero-fill or file padding is not
                    # backed by actual code. Never accept another section's flags.
                    code_end = virtual_rva + min(raw_bytes, virtual_bytes or raw_bytes)
                    backed_virtual_ranges.append((virtual_rva, code_end))
                    if (section_flags & 0x20000000
                            and virtual_rva <= entry_rva < code_end):
                        backed_entry = True
            for ranges in (virtual_ranges, file_ranges):
                ranges.sort()
                if any(prev[1] > current[0]
                       for prev, current in zip(ranges, ranges[1:])):
                    raise PEFormatError("Overlapping PE section extents")
            if not backed_entry:
                raise PEFormatError("Entry point is not backed by executable section bytes")
            try:
                # PE security directory is a raw file offset, not an RVA.
                # Other table entries must live in mapped PE image regions.
                validate_pe_directories(
                    optional, header_size=headers_size, image_size=image_size,
                    file_size=length, virtual_ranges=virtual_ranges,
                    file_ranges=file_ranges,
                    backed_virtual_ranges=backed_virtual_ranges,
                )
            except PEDataDirectoryError:
                raise PEFormatError("PE data directory rejected") from None
            if expected_sha256 is not None:
                # Bind the structural PE verdict to the EXACT manifest bytes on
                # this same already-open descriptor; a pathname can be replaced
                # between independent format and checksum passes.
                verify_pe_digest_stream(stream, metadata, expected_sha256)
    except PEFormatError:
        raise
    except Exception:
        # Private read/seek, context-enter/exit, parse and I/O faults must
        # not survive via the exception-chain object graph. The handler ends
        # before we construct the redacted public exception.
        stream_fault = True
    if stream_fault:
        raise PEFormatError("Cannot inspect candidate file")
