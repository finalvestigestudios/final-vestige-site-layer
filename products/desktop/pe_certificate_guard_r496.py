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


def _read_exact_at(stream, offset: int, size: int) -> bytes | None:
    """Require an exact native seek receipt before trusting certificate bytes.

    An injected stream may report success while seeking to the wrong location,
    return True (which compares equal to 1), or override comparison on an int
    subclass. Native FileIO and BytesIO return a plain integer offset. Catch
    ordinary I/O faults here so the public error raised by the caller cannot
    retain private exception context. Never swallow process interrupts.
    """
    data = None
    try:
        positioned = stream.seek(offset)
        if type(positioned) is int and positioned == offset:
            data = stream.read(size)
    except Exception:
        pass
    if type(data) is bytes and len(data) == size:
        return data
    return None


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
    R499 conservatively requires outer record alignment padding to be zero;
    it does not parse PKCS#7 or check padding *inside* the signed-data payload.
    R500 rejects non-native read receipts and sanitizes arbitrary ordinary
    stream faults without retaining their possibly private exception chains.
    R502 additionally requires an exact native seek position receipt for
    header, tail and padding reads on the held descriptor.
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
        header = _read_exact_at(stream, cursor, 8)
        if header is None:
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
        tail = _read_exact_at(stream, cursor + padded_size - 1, 1)
        if tail is None:
            raise PECertificateError("PE certificate table rejected")
        # Per PE/COFF, padding OUTSIDE dwLength is zero-filled. An otherwise
        # framed signature must not carry unaccounted bytes in this gap.
        # This reads at most seven bytes, does not parse PKCS#7 and is not
        # Microsoft's WinVerifyTrust EnableCertPaddingCheck implementation.
        padding_bytes = padded_size - record_size
        if padding_bytes:
            padding = _read_exact_at(stream, cursor + record_size, padding_bytes)
            if padding != b"\x00" * padding_bytes:
                raise PECertificateError("PE certificate table rejected")
        cursor += padded_size
        records += 1
