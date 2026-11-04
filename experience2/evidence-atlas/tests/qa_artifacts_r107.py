#!/usr/bin/env python3
"""R107: structural receipt validation for actual Playwright PNG/PDF artifacts.

This checks format, PNG pixels/layout and the full PNG chunk CRC chain, not
historical rights, editorial validity, or WordPress publication readiness.
No image rendering/network calls; bounded decoding rejects decompression bombs.
"""
from __future__ import annotations

import re
import struct
import zlib
from pathlib import Path

PNG_SIG = b'\x89PNG\r\n\x1a\n'
MAX_FILE_BYTES = 25 * 1024 * 1024
MAX_PIXELS = 32_000_000
MAX_RAW_BYTES = 130 * 1024 * 1024


class ArtifactInvalid(ValueError):
    pass


def _die(code):
    raise ArtifactInvalid('R107_' + code)


def check_png(path: Path, expected_width: int):
    """Return (width,height) after CRC, chunk-order and scanline verification.

    Playwright's screenshot PNGs are non-interlaced 8-bit RGB/RGBA. No
    arbitrary PNG ancillary parsing is needed for this reproducible contract.
    """
    data = Path(path).read_bytes()
    if len(data) > MAX_FILE_BYTES or len(data) < 58 or not data.startswith(PNG_SIG):
        _die('INVALID_PNG_BYTES')
    pos, seen_ihdr, seen_idat, seen_iend = 8, False, False, False
    inflator = zlib.decompressobj()
    produced = 0
    width = height = channels = None
    while pos < len(data):
        if pos + 12 > len(data):
            _die('TRUNCATED_PNG_CHUNK')
        length = struct.unpack_from('>I', data, pos)[0]
        tag = data[pos + 4:pos + 8]
        end = pos + 12 + length
        if length > MAX_FILE_BYTES or end > len(data):
            _die('TRUNCATED_PNG_CHUNK')
        value = data[pos + 8:pos + 8 + length]
        crc = struct.unpack_from('>I', data, pos + 8 + length)[0]
        if zlib.crc32(tag + value) & 0xffffffff != crc:
            _die('PNG_CRC_MISMATCH')
        if not seen_ihdr:
            if tag != b'IHDR' or length != 13:
                _die('PNG_MISSING_IHDR')
            width, height, depth, color, comp, filtering, interlace = struct.unpack('>IIBBBBB', value)
            if (width != expected_width or height < 900 or width * height > MAX_PIXELS
                    or depth != 8 or color not in (2, 6) or comp or filtering or interlace):
                _die('PNG_UNEXPECTED_DIMENSIONS_OR_FORMAT')
            channels = 3 if color == 2 else 4
            seen_ihdr = True
        elif tag == b'IHDR':
            _die('PNG_DUPLICATE_IHDR')
        if tag == b'IDAT':
            if seen_iend or inflator.eof:
                _die('PNG_INVALID_IDAT_ORDER')
            seen_idat = True
            limit = MAX_RAW_BYTES - produced
            if limit <= 0:
                _die('PNG_DECOMPRESSION_LIMIT')
            try:
                raw = inflator.decompress(value, limit + 1)
            except zlib.error:
                _die('PNG_DEFLATE_INVALID')
            produced += len(raw)
            if produced > MAX_RAW_BYTES or inflator.unconsumed_tail:
                _die('PNG_DECOMPRESSION_LIMIT')
        elif tag == b'IEND':
            if length != 0 or not seen_idat or seen_iend or end != len(data):
                _die('PNG_INVALID_IEND')
            seen_iend = True
        elif tag in (b'PLTE', b'tRNS'):
            if seen_idat:
                _die('PNG_CHUNK_AFTER_IDAT')
        elif tag not in (b'IHDR', b'IDAT', b'IEND') and tag[0] & 0x20 == 0:
            # Reject unknown critical chunks; ancillary chunks are permitted.
            _die('PNG_UNKNOWN_CRITICAL_CHUNK')
        pos = end
    if not (seen_ihdr and seen_idat and seen_iend and inflator.eof and not inflator.unused_data):
        _die('PNG_INCOMPLETE_IMAGE')
    # Every unfiltered scanline must contain one filter byte and width*channels
    # pixel bytes, exactly; this detects a valid zlib stream with zero pixels.
    expected_raw = height * (width * channels + 1)
    if produced != expected_raw:
        _die('PNG_PIXEL_DATA_MISMATCH')
    return width, height


def check_pdf(path: Path):
    """Reject truncated or relabelled PDF. Full semantics remain human-reviewed."""
    data = Path(path).read_bytes()
    if not (100 <= len(data) <= MAX_FILE_BYTES and re.match(rb'%PDF-1\.[4-7]', data[:8])):
        _die('INVALID_PDF_HEADER')
    # Playwright/Chromium PDF print always includes startxref and terminal EOF.
    tail = data[-2048:].rstrip(b'\x00\t\r\n ')
    if not tail.endswith(b'%%EOF') or b'startxref' not in tail:
        _die('PDF_TRUNCATED_OR_MISSING_XREF')
    return len(data)
