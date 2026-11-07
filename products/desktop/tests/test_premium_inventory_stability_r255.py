"""R255: premium manifest Windows metadata compatibility and package stability.

Synthetic private-free files. Assertions exercise the real R255 verifier; this
isolated harness supplies a local hash stand-in, not the complete repo tree.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import fvs_suite.premium_manifest_completion as subject
from fvs_suite.csv_snapshot import _same_path_descriptor_signature as same

STAMP = '20261107-005400-123456'
PACK = '20261107T085400Z-' + 'a'*32
HEADER = 'SHA-256 file inventory. Hashes do not certify accuracy or compliance.\n'
REAL_FSTAT = os.fstat
SOURCES = [f'source-{i}.csv\t' + 'a'*64 + '\n' for i in range(3)]


class PremiumInventoryStabilityR255(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def create(self, app='grants', optional=False):
        prefix, stems = ('grant-evidence-', ('grant-audit-exceptions', 'grant-budget-check')) if app == 'grants' else ('procurement-evidence-', ('procurement-three-way',))
        package = self.root / (prefix + PACK)
        package.mkdir()
        reports = []
        for stem in stems:
            report = package / f'{stem}-{STAMP}.csv'
            report.write_bytes((stem+'\n').encode())
            reports.append(report)
        manifest = package / f'evidence-manifest-{STAMP}.txt'
        digest_entries = [f'{json.dumps(path.name, ensure_ascii=True)[1:-1]}\t{hashlib.sha256(path.read_bytes()).hexdigest()}\n' for path in reports]
        sources = SOURCES + (['policy.txt\t'+'b'*64+'\n'] if optional else [])
        manifest.write_text(HEADER + ''.join(sources + digest_entries), encoding='ascii')
        return tuple(reports+[manifest])

    def during_hash(self, mutation, *, trigger=0):
        original = subject._hash_regular
        calls = 0
        def wrapped(path, limit):
            nonlocal calls
            result = original(path, limit)
            if calls == trigger:
                mutation()
            calls += 1
            return result
        return patch.object(subject, '_hash_regular', side_effect=wrapped)

    def test_stable_grants_pass(self):
        subject.verify_premium_inventory(self.create(), 'grants')

    def test_stable_procurement_pass(self):
        subject.verify_premium_inventory(self.create('procurement'), 'procurement')

    def test_stable_procurement_optional_policy_pass(self):
        subject.verify_premium_inventory(self.create('procurement', optional=True), 'procurement')

    def test_stable_manifest_read_does_not_modify_files(self):
        paths = self.create()
        before = {p: p.read_bytes() for p in paths}
        subject.verify_premium_inventory(paths, 'grants')
        self.assertEqual(before, {p: p.read_bytes() for p in paths})

    def test_manifest_changed_during_first_hash_is_rejected(self):
        paths = self.create()
        manifest = paths[-1]
        def mutate():
            manifest.write_bytes(manifest.read_bytes().replace(b'source-0', b'source-Z'))
        with self.during_hash(mutate):
            with self.assertRaisesRegex(ValueError, 'changed while reports'):
                subject.verify_premium_inventory(paths, 'grants')

    def test_manifest_modified_at_same_size_is_rejected(self):
        paths = self.create('procurement')
        manifest = paths[-1]
        initial_size = manifest.stat().st_size
        def mutate():
            content = manifest.read_bytes()
            manifest.write_bytes(content.replace(b'source-0', b'source-7'))
        with self.during_hash(mutate):
            with self.assertRaises(ValueError):
                subject.verify_premium_inventory(paths, 'procurement')
        self.assertEqual(initial_size, manifest.stat().st_size)

    def test_manifest_deleted_during_hash_fails_closed(self):
        paths = self.create()
        with self.during_hash(lambda: paths[-1].unlink()):
            with self.assertRaises(ValueError):
                subject.verify_premium_inventory(paths, 'grants')

    def test_manifest_replaced_with_symlink_during_hash_fails_closed(self):
        paths = self.create('procurement')
        outside = self.root/'other.txt'
        outside.write_bytes(paths[-1].read_bytes())
        def mutate():
            paths[-1].unlink()
            paths[-1].symlink_to(outside)
        try:
            with self.during_hash(mutate):
                with self.assertRaises(ValueError):
                    subject.verify_premium_inventory(paths, 'procurement')
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f'Host cannot create symlinks: {type(exc).__name__}')

    def test_first_report_modified_during_second_hash_is_rejected(self):
        paths = self.create()
        with self.during_hash(lambda: paths[0].write_bytes(b'overwritten\n'), trigger=1):
            with self.assertRaisesRegex(ValueError, 'report changed'):
                subject.verify_premium_inventory(paths, 'grants')

    def test_report_removed_during_later_hash_fails_closed(self):
        paths = self.create()
        with self.during_hash(lambda: paths[0].unlink(), trigger=1):
            with self.assertRaises(ValueError):
                subject.verify_premium_inventory(paths, 'grants')

    def test_directory_new_file_during_hash_is_rejected(self):
        paths = self.create('procurement')
        with self.during_hash(lambda: (paths[0].parent/'new-file.txt').write_text('x')):
            with self.assertRaisesRegex(ValueError, 'package changed'):
                subject.verify_premium_inventory(paths, 'procurement')

    def test_directory_new_folder_during_hash_is_rejected(self):
        paths = self.create('procurement')
        with self.during_hash(lambda: (paths[0].parent/'extra').mkdir()):
            with self.assertRaisesRegex(ValueError, 'package changed'):
                subject.verify_premium_inventory(paths, 'procurement')

    def test_wrong_report_hash_still_rejected(self):
        paths = self.create('procurement')
        paths[0].write_text('wrong\n')
        with self.assertRaises(ValueError):
            subject.verify_premium_inventory(paths, 'procurement')

    def test_wrong_product_still_rejected(self):
        paths = self.create('procurement')
        with self.assertRaises(ValueError):
            subject.verify_premium_inventory(paths, 'grants')

    @staticmethod
    def mismatched_ctime(fd):
        original = REAL_FSTAT(fd)
        return SimpleNamespace(st_dev=original.st_dev, st_ino=original.st_ino,
                               st_size=original.st_size, st_mode=original.st_mode,
                               st_mtime_ns=original.st_mtime_ns,
                               st_ctime_ns=original.st_ctime_ns+987654321)

    def test_windows_path_descriptor_ctime_discrepancy_permitted(self):
        paths = self.create()
        self.original_fstat = os.fstat
        with (patch.object(subject.os, 'fstat', side_effect=self.mismatched_ctime),
              patch.object(subject, '_same_path_descriptor_signature',
                           side_effect=lambda a,b: same(a,b,windows=True))):
            self.assertEqual(subject._read_bounded_inventory(paths[-1]),paths[-1].read_text('ascii'))

    def test_posix_path_descriptor_ctime_discrepancy_rejected(self):
        paths = self.create()
        self.original_fstat = os.fstat
        with (patch.object(subject.os, 'fstat', side_effect=self.mismatched_ctime),
              patch.object(subject, '_same_path_descriptor_signature',
                           side_effect=lambda a,b: same(a,b,windows=False))):
            with self.assertRaises(ValueError):
                subject._read_bounded_inventory(paths[-1])


if __name__ == '__main__':
    unittest.main()
