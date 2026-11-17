"""Bounded WIN_CERTIFICATE table preflight for unsigned/signed PE32+ candidates.

Checks a certificate table's framing on the PE verifier's already-open stream.
This DOES NOT verify the Authenticode signature, certificate chain, trust or AV.
"""
from __future__ import annotations

import struct


class PECertificateError(ValueError):
    """The candidate's PE security directory is not a bounded certificate table."""


MAX_CERTIFICATE_TABLE_BYTES = 8 * 1024 * 1024
MAX_CERTIFICATE_RECORDS = 128


def verify_certificate_table(stream, optional: bytes, *, file_size: int) -> None:
    """Walk an optional PE security directory without executing or loading its payload.

    Security directory #4 contains FILE offsets, unlike all other RVA-based
    directories. Records are 8-byte-aligned WIN_CERTIFICATE structures with a
    DWORD length INCLUDING the eight-byte header; padding completes alignment.
    This release preflight deliberately accepts only revision 2.0 PKCS signed
    data records. Each claimed record tail must physically be readable on
    the same stream, including its alignment padding. This catches truncation
    after an earlier file-size observation; it is not a lock or signature check.
    A structurally valid record is not proof of a valid signature.
    """
    if len(optional) < 112:
        raise PECertificateError("PE certificate table rejected")
    count = struct.unpack_from("<I", optional, 108)[0]
    if count > 16 or 112 + count * 8 > len(optional):
        raise PECertificateError("PE certificate table rejected")
    if count <= 4:
        return
    start, size = struct.unpack_from("<II", optional, 112 + 4 * 8)
    if start == 0 and size == 0:
        return
    if (start == 0 or size == 0 or start % 8 or size % 8
            or size > MAX_CERTIFICATE_TABLE_BYTES or start + size > file_size):
        raise PECertificateError("PE certificate table rejected")
    cursor, end, records = start, start + size, 0
    while cursor < end:
        if records >= MAX_CERTIFICATE_RECORDS or end - cursor < 8:
            raise PECertificateError("PE certificate table rejected")
        header = None
        try:
            stream.seek(cursor)
            header = stream.read(8)
        except OSError:
            # Raise after the handler ends so no private path leaks through
            # ValueError.__context__ ("from None" only hides display).
            pass
        if header is None or len(header) != 8:
            raise PECertificateError("PE certificate table rejected")
        record_size, revision, cert_type = struct.unpack("<IHH", header)
        padded_size = (record_size + 7) & ~7
        if (record_size <= 8 or revision != 0x0200 or cert_type != 0x0002
                or padded_size > end - cursor):
            raise PECertificateError("PE certificate table rejected")
        # Headers can survive a concurrent truncation while the declared
        # fstat file length is stale. Probe the final claimed byte, including
        # alignment padding, without allocating PKCS#7 payloads in memory.
        # A complete release gate also hashes this exact descriptor.
        tail = None
        try:
            stream.seek(cursor + padded_size - 1)
            tail = stream.read(1)
        except OSError:
            pass
        if tail is None or len(tail) != 1:
            raise PECertificateError("PE certificate table rejected")
        cursor += padded_size
        records += 1
