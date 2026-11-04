#!/usr/bin/env python3
"""R107 independent hostile artifact and private-progress regression tests."""
import hashlib
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from qa_artifacts_r107 import ArtifactInvalid, check_pdf, check_png
from qa_receipt_r105 import EvidenceJournal, FILENAME


def chunk(tag, data):
    return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)


def png(width=390, height=900, *, broken=False, pixels=True):
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    scanline = b'\x00' + bytes(width * 3)
    raw = scanline * height if pixels else b''
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))


def pdf():
    return (b'%PDF-1.7\n1 0 obj\n<< /Type /Catalog >>\nendobj\n'
            b'xref\n0 1\n0000000000 65535 f \ntrailer\n<< /Size 1 /Root 1 0 R >>\n'
            b'startxref\n42\n%%EOF\n')


class R107ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.image = self.root / 'R104_REAL_WP_SELECTED_390.png'
        self.image.write_bytes(png())
        self.document = self.root / 'R104_REAL_WP_PRINT.pdf'
        self.document.write_bytes(pdf())

    def assert_invalid(self, content, reason):
        self.image.write_bytes(content)
        with self.assertRaisesRegex(ArtifactInvalid, reason):
            check_png(self.image, 390)

    def test_valid_png(self):
        self.assertEqual(check_png(self.image, 390), (390, 900))

    def test_valid_pdf(self):
        self.assertEqual(check_pdf(self.document), len(pdf()))

    def test_short_magic_only_png(self):
        self.assert_invalid(b'\x89PNG\r\n\x1a\n', 'INVALID_PNG_BYTES')

    def test_screenshot_viewport_mismatch(self):
        self.assert_invalid(png(320), 'PNG_UNEXPECTED_DIMENSIONS')

    def test_truncated_chunk(self):
        self.assert_invalid(png()[:-4], 'TRUNCATED_PNG_CHUNK')

    def test_mismatched_crc(self):
        damaged = bytearray(png()); damaged[40] ^= 1
        self.assert_invalid(bytes(damaged), 'PNG_CRC_MISMATCH')

    def test_valid_stream_without_pixels(self):
        self.assert_invalid(png(pixels=False), 'PNG_PIXEL_DATA_MISMATCH')

    def test_missing_iend(self):
        self.assert_invalid(png()[:-12], 'PNG_INCOMPLETE_IMAGE')

    def test_extra_trailer(self):
        self.assert_invalid(png() + b'token-after-IEND', 'PNG_INVALID_IEND')

    def test_large_image_dimensions(self):
        self.assert_invalid(png(390, 90000, pixels=False), 'PNG_UNEXPECTED_DIMENSIONS')

    def test_fake_pdf_header_without_xref(self):
        self.document.write_bytes(b'%PDF-1.7\n' + b'a' * 100)
        with self.assertRaisesRegex(ArtifactInvalid, 'PDF_TRUNCATED'):
            check_pdf(self.document)

    def test_pdf_truncated_eof(self):
        self.document.write_bytes(pdf()[:-5])
        with self.assertRaisesRegex(ArtifactInvalid, 'PDF_TRUNCATED'):
            check_pdf(self.document)

    def test_progress_never_serializes_token_or_nonfinite_lab_value(self):
        j = EvidenceJournal(self.root)
        j.checkpoint({'performance_lab_samples': [
            {'width': 'https://private/?token=S3CRET', 'trial': 1,
             'lcp_ms': 'Bearer S3CRET', 'cls': float('nan')},
            'cookie: S3CRET',
        ]}, 'browser:390:js1')
        text = (self.root / FILENAME).read_text()
        self.assertNotIn('S3CRET', text)
        self.assertNotIn('NaN', text)
        self.assertEqual(json.loads(text)['lab_observations'][0]['lcp_ms'], None)


if __name__ == '__main__':
    unittest.main()
