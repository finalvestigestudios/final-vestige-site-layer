"""R233 offline negative controls: changed + newly present hub inputs.

These exercise the independent frozen-input gate, not full native 35-article
validation or the WordPress output build. All cases use temporary directories.
"""
import hashlib
import importlib.util
import pathlib
import tempfile
import unittest
from unittest.mock import patch

MODULE = pathlib.Path(__file__).resolve().parents[1] / 'tools' / 'r233_hub_input_custody_hold.py'
SPEC = importlib.util.spec_from_file_location('r233_hub_input_custody_hold', MODULE)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def digest(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


class HubSourceCustodyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='fv-r233-hub-')
        self.root = pathlib.Path(self.tmp.name) / 'preparedness'
        self.hubs = self.root / 'content' / 'hubs'
        self.hubs.mkdir(parents=True)
        self.original = b'<h2>Source-backed household readiness</h2>\n'
        (self.hubs / 'start-here.body.html').write_bytes(self.original)
        self.expected = {'start-here.body.html': digest(self.original)}

    def tearDown(self):
        self.tmp.cleanup()

    def check(self):
        return gate._verify(self.root, self.expected)

    def test_baseline_hold_does_not_claim_safety(self):
        status = self.check()
        self.assertEqual(status['state'], 'DRAFT_HARD_HOLD')
        self.assertEqual(status['hub_input_files_verified'], 1)
        for key in ('release_authorized', 'independent_qd_pass',
                    'source_or_medical_safety_approved', 'commercial_approval'):
            self.assertIs(status[key], False)

    def test_git_blob_uses_git_header(self):
        self.assertEqual(gate._git_blob(self.original), self.expected['start-here.body.html'])

    def test_frozen_production_pin_matches_R232_base(self):
        self.assertEqual(gate.FROZEN_HUB_INPUTS,
                         {'start-here.body.html': 'e1e749169a58e35a32c1d48ee8c46c209630965b'})

    def test_production_wrapper_never_uses_forged_expected(self):
        with self.assertRaisesRegex(ValueError, 'byte identity drift'):
            gate.verify_hub_inputs(self.root)

    def test_genuine_change_fails_even_when_matching_export_is_regenerated(self):
        file = self.hubs / 'start-here.body.html'
        output = self.root / 'build' / 'wp' / 'hub-start-here.html'
        output.parent.mkdir(parents=True)
        output.write_bytes(b'WP:' + file.read_bytes())
        file.write_bytes(self.original + b'<p>unreviewed product CTA</p>')
        output.write_bytes(b'WP:' + file.read_bytes())
        self.assertEqual(output.read_bytes(), b'WP:' + file.read_bytes())
        with self.assertRaisesRegex(ValueError, 'byte identity drift'):
            self.check()

    def test_new_hub_even_when_matching_export_is_regenerated(self):
        extra = self.hubs / 'food.body.html'
        extra.write_text('<p>unreviewed editorial guidance</p>')
        output = self.root / 'build' / 'preview' / 'hub-food.html'
        output.parent.mkdir(parents=True)
        output.write_text('<main>' + extra.read_text() + '</main>')
        self.assertIn(extra.read_text(), output.read_text())
        with self.assertRaisesRegex(ValueError, 'membership drift'):
            self.check()

    def test_missing_frozen_source(self):
        (self.hubs / 'start-here.body.html').unlink()
        with self.assertRaisesRegex(ValueError, 'membership drift'):
            self.check()

    def test_symlink_hub_root(self):
        elsewhere = self.root / 'backed-up'
        self.hubs.rename(elsewhere)
        self.hubs.symlink_to(elsewhere, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'missing/symlinked hub directory'):
            self.check()

    def test_symlink_hub_file(self):
        p = self.hubs / 'start-here.body.html'
        backup = self.root / 'original.html'
        p.rename(backup)
        p.symlink_to(backup)
        with self.assertRaisesRegex(ValueError, 'unsafe hub input member'):
            self.check()

    def test_symlink_content_parent(self):
        parent = self.root / 'content'
        backup = self.root / 'content-backup'
        parent.rename(backup)
        parent.symlink_to(backup, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'missing/symlinked hub directory'):
            self.check()

    def test_symlink_preparedness_root(self):
        alias = pathlib.Path(self.tmp.name) / 'alias'
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'missing/symlinked hub directory'):
            gate._verify(alias, self.expected)

    def test_directory_replaced_by_file(self):
        path = self.hubs / 'start-here.body.html'
        path.unlink()
        self.hubs.rmdir()
        self.hubs.write_bytes(b'not a directory')
        with self.assertRaisesRegex(ValueError, 'missing/symlinked hub directory'):
            self.check()

    def test_extra_directory_rejected(self):
        (self.hubs / 'extra-dir').mkdir()
        with self.assertRaisesRegex(ValueError, 'membership drift'):
            self.check()

    def test_empty_expected_manifest_fails(self):
        with self.assertRaisesRegex(ValueError, 'invalid frozen hub manifest'):
            gate._verify(self.root, {})

    def test_invalid_root_type_fails(self):
        with self.assertRaisesRegex(ValueError, 'invalid Preparedness root'):
            gate._verify(str(self.root), self.expected)

    def test_bad_expected_name_fails(self):
        with self.assertRaisesRegex(ValueError, 'malformed hub source identity'):
            gate._verify(self.root, {'../start-here.body.html': digest(self.original)})

    def test_bad_expected_blob_fails(self):
        with self.assertRaisesRegex(ValueError, 'malformed hub source identity'):
            gate._verify(self.root, {'start-here.body.html': '0000'})


def mutation_for(suffix, value):
    def test(self):
        p = self.hubs / 'start-here.body.html'
        p.write_bytes(value + suffix)
        with self.assertRaisesRegex(ValueError, 'byte identity drift'):
            self.check()
    return test


def extra_for(name):
    def test(self):
        (self.hubs / name).write_bytes(b'new section editorial input')
        with self.assertRaisesRegex(ValueError, 'membership drift'):
            self.check()
    return test


# 32 source mutation negatives, all independently exercised on disk.
for i in range(32):
    payload = ('<span data-drift="%02d">unreviewed</span>' % i).encode()
    setattr(HubSourceCustodyTests, f'test_source_mutation_{i:02d}_fails',
            mutation_for(bytes([i]), payload))

# 18 membership negatives, including orphaned and unexpected section inputs.
for i in range(18):
    setattr(HubSourceCustodyTests, f'test_extra_hub_{i:02d}_fails',
            extra_for(f'unapproved-{i:02d}.body.html'))

if __name__ == '__main__':
    unittest.main()
