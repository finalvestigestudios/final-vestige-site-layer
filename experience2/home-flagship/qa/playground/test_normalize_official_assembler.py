#!/usr/bin/env python3
"""Adversarial pure-local checks for official Assembler archive root normalization."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import stat
import tempfile
import unittest
import zipfile

SCRIPT = Path(__file__).with_name('normalize_official_assembler.py')
spec = importlib.util.spec_from_file_location('fv_assembler_normalizer', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AssemblerNormalizationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='fv-theme-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.src = self.root / 'official.zip'
        self.out = self.root / 'assembler-canonical.zip'
        self.receipt = self.root / 'receipt.json'

    def write_zip(self, files):
        with zipfile.ZipFile(self.src, 'w') as z:
            for name, payload in files.items():
                if isinstance(payload, tuple):
                    raw, symlink = payload
                    entry = zipfile.ZipInfo(name)
                    entry.create_system = 3
                    entry.external_attr = (stat.S_IFLNK | 0o777) << 16 if symlink else (stat.S_IFREG | 0o644) << 16
                    z.writestr(entry, raw)
                else:
                    entry = zipfile.ZipInfo(name)
                    entry.create_system = 3
                    entry.external_attr = (stat.S_IFREG | 0o644) << 16
                    z.writestr(entry, payload)

    def valid(self):
        return {
            'assembler-wpcom/style.css': b'/*\nTheme Name: Assembler\nVersion: 0.0.126\n*/',
            'assembler-wpcom/templates/index.html': b'<!-- wp:post-content /-->',
            'assembler-wpcom/inc/fixture.php': b'<?php return true;'
        }

    def test_real_bytes_preserved_and_root_canonical(self):
        src = self.valid()
        self.write_zip(src)
        r = module.normalize(self.src, self.out, self.receipt)
        self.assertEqual(r['file_contents_byte_preserved'], True)
        self.assertEqual(r['release'], 'HOLD')
        self.assertEqual(r['files'], 3)
        with zipfile.ZipFile(self.out) as z:
            self.assertEqual(sorted(z.namelist()), sorted(k.replace('assembler-wpcom/', 'assembler/') for k in src))
            self.assertEqual(z.read('assembler/style.css'), src['assembler-wpcom/style.css'])
        self.assertEqual(r['derived_canonical_zip_sha256'], module.sha256(self.out))

    def test_wrong_root_rejected(self):
        d = {k.replace('assembler-wpcom/', 'fake-assembler/') : v for k,v in self.valid().items()}
        self.write_zip(d)
        with self.assertRaisesRegex(ValueError, 'unsafe theme ZIP path'):
            module.normalize(self.src, self.out, self.receipt)

    def test_wrong_version_fails_closed(self):
        d = self.valid(); d['assembler-wpcom/style.css'] = b'Theme Name: Assembler\nVersion: 0.0.127'
        self.write_zip(d)
        with self.assertRaisesRegex(ValueError, 'version parity'):
            module.normalize(self.src, self.out, self.receipt)

    def test_colliding_names_rejected(self):
        d = self.valid(); d['assembler-wpcom/INC/fixture.php'] = b'<?php exit;'
        self.write_zip(d)
        with self.assertRaisesRegex(ValueError, 'collision'):
            module.normalize(self.src, self.out, self.receipt)

    def test_zip_symlink_rejected(self):
        d = self.valid(); d['assembler-wpcom/assets/link'] = (b'../../etc/passwd', True)
        self.write_zip(d)
        with self.assertRaisesRegex(ValueError, 'file type'):
            module.normalize(self.src, self.out, self.receipt)

    def test_missing_template_rejected(self):
        d = self.valid(); del d['assembler-wpcom/templates/index.html']
        self.write_zip(d)
        with self.assertRaisesRegex(ValueError, 'index template'):
            module.normalize(self.src, self.out, self.receipt)


if __name__ == '__main__':
    unittest.main()
