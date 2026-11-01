"""R32 synthetic-only custody tests: preserve original fragments README, reject extras.
No WordPress, publishing, network, QD or medical approval.
"""
from __future__ import annotations

from pathlib import Path
import json
import sys
import tempfile
import unittest

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(TESTS.parent / 'tools'))
import source_crosswalk_truth_gate as gate
import test_source_crosswalk_truth_gate as fixtures

README_TEXT = (
    'Each contributor session adds sources here as `<cluster>.json` with the same '
    'shape as `../register.json` (`{"sources": [...]}`). Ids must be unique '
    'across the whole register. Do not edit `../register.json`.\n'
)
UNEXPECTED_NAMES = [
    'README.txt', 'Readme.md', 'readme.md', 'README.MD',
    'README.md.bak', 'README.md.old', 'README.md.orig', 'README.md.copy',
    'README.md.tmp', 'README.md.lock', 'README.md~', 'README.html',
    'README.json', 'README.yaml', 'README.yml', 'README.rst',
    '.README.md.swp', '.DS_Store', '.gitkeep', '.gitignore',
    '_upgrade_test.json', '_upgrade_fixture.json', 'unreviewed.json',
    'malicious.json', 'source.json', 'sources.json', 'new.json',
    'food.json.bak', 'food.json.tmp', 'food.json.old', 'food-copy.json',
    'food.json.disabled', 'start.json.bak', 'start.json.tmp',
    'health2.json', 'base.json', 'register.json', 'crosswalk.json',
    'manifest.json', 'tempfile', 'collision.JSON', 'null.json',
    'staging.csv', 'raw-data.txt', 'preview.html', 'README.backup',
    'runner-output.log', 'draft-source.json'
]


class OriginalDocumentationCustody(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory(prefix='fvs-r32-')
        self.addCleanup(td.cleanup)
        self.root = Path(td.name)
        fixtures.make_fixture(self.root)
        self.fragment_dir = self.root / 'preparedness' / 'sources' / 'fragments'
        self.doc = self.fragment_dir / 'README.md'

    def audit(self, *, expected=fixtures.EX):
        return gate.audit(self.root, expected=expected)

    def write_original_readme(self):
        self.doc.write_text(README_TEXT, encoding='utf-8')
        self.assertEqual(gate.git_blob(self.doc.read_bytes()),
                         gate.FRAGMENT_README_GIT_BLOB)

    def test_original_readme_bytes_are_independently_pinned(self):
        self.assertEqual(
            gate.git_blob(README_TEXT.encode('utf-8')),
            'cec167dd6acaf9f6e92e87a61fa9aeacdad151a5'
        )

    def test_synthetic_fixture_without_readme_retains_hold(self):
        result = self.audit()
        self.assertEqual(result['release_state'], 'HOLD')
        self.assertIs(result['may_publish'], False)
        self.assertIsNone(result['fragment_readme_git_blob_sha'])
        self.assertIs(result['human_source_reviews_complete'], False)

    def test_original_readme_is_allowed_and_fingerprinted(self):
        self.write_original_readme()
        result = self.audit()
        self.assertEqual(result['fragment_readme_git_blob_sha'],
                         gate.FRAGMENT_README_GIT_BLOB)
        self.assertIs(result['qualified_safety_clearance'], False)
        self.assertEqual(result['unresolved_shared_url_groups'], 1)

    def test_original_readme_does_not_change_source_inventory_counts(self):
        original = self.audit()
        self.write_original_readme()
        with_doc = self.audit()
        for key in ('source_row_count', 'unique_literal_urls', 'duplicate_source_id_groups',
                    'unresolved_shared_url_groups', 'unread_source_placeholders',
                    'source_group_review_queue', 'crosswalk_git_blob_sha'):
            self.assertEqual(original[key], with_doc[key], key)

    def test_original_readme_does_change_custody_fingerprint(self):
        before = self.audit()
        self.write_original_readme()
        after = self.audit()
        self.assertNotEqual(before['audit_fingerprint'], after['audit_fingerprint'])

    def test_original_readme_audit_is_repeatable(self):
        self.write_original_readme()
        self.assertEqual(self.audit(), self.audit())

    def test_original_documentation_is_not_treated_as_a_source(self):
        self.write_original_readme()
        r = self.audit()
        self.assertEqual(r['source_row_count'], fixtures.EX['source_rows'])
        self.assertEqual(r['non_author_source_head_aliases'][0]['origin'], 'food')

    def test_full_archive_demands_original_readme(self):
        with self.assertRaisesRegex(gate.CustodyError, 'README missing'):
            self.audit(expected=gate.EXPECTED)

    def test_reworded_original_readme_is_rejected(self):
        self.write_original_readme()
        self.doc.write_text(README_TEXT.replace('whole register', 'fragment'), encoding='utf-8')
        with self.assertRaisesRegex(gate.CustodyError, 'instructions drift'):
            self.audit()

    def test_readme_append_is_rejected(self):
        self.write_original_readme()
        self.doc.write_text(README_TEXT + 'Later changed.', encoding='utf-8')
        with self.assertRaisesRegex(gate.CustodyError, 'instructions drift'):
            self.audit()

    def test_readme_truncation_is_rejected(self):
        self.write_original_readme()
        self.doc.write_bytes(README_TEXT.encode('utf-8')[:-1])
        with self.assertRaisesRegex(gate.CustodyError, 'instructions drift'):
            self.audit()

    def test_empty_readme_is_rejected(self):
        self.doc.write_bytes(b'')
        with self.assertRaises(gate.CustodyError):
            self.audit()

    def test_non_utf8_readme_is_rejected(self):
        self.doc.write_bytes(b'\xff\xfe')
        with self.assertRaisesRegex(gate.CustodyError, 'instructions drift'):
            self.audit()

    def test_original_readme_is_not_rewritten_by_audit(self):
        self.write_original_readme()
        before = self.doc.read_bytes()
        self.audit()
        self.assertEqual(self.doc.read_bytes(), before)

    def test_missing_contributor_source_is_rejected_with_doc_present(self):
        self.write_original_readme()
        (self.fragment_dir / 'food.json').unlink()
        with self.assertRaises(gate.CustodyError):
            self.audit()

    def test_extraneous_directory_is_not_silently_ignored(self):
        (self.fragment_dir / 'unread-subdirectory').mkdir()
        with self.assertRaisesRegex(gate.CustodyError, 'non-file'):
            self.audit()

    def test_original_readme_symlink_is_rejected(self):
        target = self.fragment_dir / 'food.json'
        self.doc.symlink_to(target)
        with self.assertRaisesRegex(gate.CustodyError, 'linked'):
            self.audit()

    def test_extra_symlink_is_rejected(self):
        (self.fragment_dir / 'source-shadow').symlink_to(self.fragment_dir / 'food.json')
        with self.assertRaisesRegex(gate.CustodyError, 'linked'):
            self.audit()

    def test_extra_symlink_to_directory_is_rejected(self):
        (self.fragment_dir / 'linked-folder').symlink_to(self.fragment_dir, target_is_directory=True)
        with self.assertRaisesRegex(gate.CustodyError, 'linked'):
            self.audit()

    def test_missing_full_archive_readme_not_permitted_if_counts_default(self):
        # The synthetic rows are intentionally only 8. The full frozen
        # 224-row expected inventory must reject missing README *before*
        # inspecting those source rows.
        with self.assertRaisesRegex(gate.CustodyError, 'original source fragment README missing'):
            gate.audit(self.root)

    def test_source_fragment_instruction_file_does_not_approve_human_review(self):
        self.write_original_readme()
        r = self.audit()
        self.assertIs(r['human_source_reviews_complete'], False)
        self.assertIs(r['article_claim_accuracy_verified'], False)
        self.assertIs(r['qualified_safety_clearance'], False)
        self.assertIs(r['may_publish'], False)

    def test_only_original_readme_is_eligible_extra(self):
        self.write_original_readme()
        extra = self.fragment_dir / 'README-copy.md'
        extra.write_text(README_TEXT, encoding='utf-8')
        with self.assertRaises(gate.CustodyError):
            self.audit()


def _unexpected_file_case(filename):
    def test(self):
        (self.fragment_dir / filename).write_text('{}', encoding='utf-8')
        with self.assertRaises(gate.CustodyError):
            self.audit()
    return test


for index, filename in enumerate(UNEXPECTED_NAMES):
    setattr(OriginalDocumentationCustody,
            f'test_reject_unexpected_fragment_file_{index:02d}',
            _unexpected_file_case(filename))


if __name__ == '__main__':
    unittest.main()
