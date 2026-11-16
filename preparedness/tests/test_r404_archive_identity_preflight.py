"""R404 synthetic-only adversarial ZIP identity and preflight regression suite.

The authenticated E395 original is NOT present; no test claims release/safety.
"""
from __future__ import annotations

from io import BytesIO
import importlib.util
from pathlib import Path
import stat
import unittest
from unittest import mock
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

TOOL = Path(__file__).resolve().parents[1] / 'tools' / 'r402_external_editorial_custody.py'
spec = importlib.util.spec_from_file_location('r402_for_r404', TOOL)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

ARTICLE = b'<article><h1>R404 SYNTHETIC NOT FOR PUBLICATION</h1></article>'


def make_zip(entries):
    buf = BytesIO()
    with ZipFile(buf, 'w', ZIP_DEFLATED) as z:
        for name, payload, mode in entries:
            member = ZipInfo(name)
            member.compress_type = ZIP_DEFLATED
            member.external_attr = (mode << 16) if mode is not None else 0
            z.writestr(member, payload)
    return buf.getvalue()


def article_entry(name=None):
    return (name or gate.ARTICLE_MEMBER, ARTICLE, stat.S_IFREG | 0o644)


def checked(entries, **kwargs):
    raw = make_zip(entries)
    return gate.inspect(raw, expected_zip_sha=gate.sha256(raw),
                        expected_article_sha=gate.sha256(ARTICLE), **kwargs)


class ArchivePreflight(unittest.TestCase):
    def test_one_simple_article_is_structurally_sound_not_publishable(self):
        r = checked([article_entry()])
        self.assertEqual(r['archive_integrity'], 'PASS')
        self.assertFalse(r['eligible'])
        self.assertEqual(r['release'], 'DRAFT_HARD_HOLD')
        self.assertEqual(r['qualified_food_safety_review'], 'NOT_GRANTED')

    def test_normal_directory_plus_article_accepted(self):
        r = checked([('notes/', b'', stat.S_IFDIR | 0o755), article_entry()])
        self.assertEqual(r['archive_integrity'], 'PASS')

    def test_directory_symlink_masquerade_rejected(self):
        r = checked([('notes/', b'', stat.S_IFLNK | 0o777), article_entry()])
        self.assertIn('non_directory_member', r['failures'])

    def test_directory_regular_mode_masquerade_rejected(self):
        r = checked([('notes/', b'', stat.S_IFREG | 0o644), article_entry()])
        self.assertIn('non_directory_member', r['failures'])

    def test_nonempty_directory_rejected(self):
        r = checked([('notes/', b'not a folder', stat.S_IFDIR | 0o755), article_entry()])
        self.assertIn('nonempty_directory_member', r['failures'])

    def test_duplicate_canonical_case_rejected(self):
        r = checked([article_entry(), ('Notes.txt', b'1', stat.S_IFREG),
                    ('notes.TXT', b'2', stat.S_IFREG)])
        self.assertIn('duplicate_canonical_member', r['failures'])

    def test_unicode_compatibility_alias_rejected(self):
        r = checked([article_entry(), ('1.txt', b'1', stat.S_IFREG),
                     ('①.txt', b'2', stat.S_IFREG)])
        self.assertIn('duplicate_canonical_member', r['failures'])

    def test_decomposed_unicode_rejected(self):
        r = checked([article_entry(), ('cafe\u0301.txt', b'1', stat.S_IFREG)])
        self.assertIn('unsafe_member_name', r['failures'])

    def test_file_directory_path_collision_rejected(self):
        r = checked([article_entry(), ('a.txt', b'1', stat.S_IFREG),
                     ('a.txt/sub.txt', b'2', stat.S_IFREG)])
        self.assertIn('file_directory_path_collision', r['failures'])

    def test_nested_prefix_collision_case_insensitive(self):
        r = checked([article_entry(), ('AB.txt', b'1', stat.S_IFREG),
                     ('ab.TXT/a/b.txt', b'2', stat.S_IFREG)])
        self.assertIn('file_directory_path_collision', r['failures'])

    def test_file_directory_same_identity_rejected(self):
        r = checked([article_entry(), ('base/', b'', stat.S_IFDIR),
                     ('BASE.txt', b'no collision', stat.S_IFREG),
                     ('BASE/', b'', stat.S_IFDIR)])
        self.assertIn('duplicate_canonical_member', r['failures'])

    def test_directory_file_identity_alias_rejected(self):
        # Extensionless files are disallowed, so the duplicate directory case
        # is tested by case-insensitive directory aliases.
        r = checked([article_entry(), ('Chapter/', b'', stat.S_IFDIR),
                     ('chapter/', b'', stat.S_IFDIR)])
        self.assertIn('duplicate_canonical_member', r['failures'])

    def test_over_member_limit_prevents_reads(self):
        entries = [article_entry()] + [(f'n{i:04d}.txt', b'1', stat.S_IFREG)
                                     for i in range(gate.MAX_FILES)]
        raw = make_zip(entries)
        with mock.patch.object(ZipFile, 'open', side_effect=AssertionError('decompressed before preflight')):
            r = gate.inspect(raw, expected_zip_sha=gate.sha256(raw),
                             expected_article_sha=gate.sha256(ARTICLE))
        self.assertEqual(r['failures'], ['zip_member_count'])
        self.assertFalse(r['eligible'])

    def test_max_files_boundary_allowed_if_unique(self):
        entries = [article_entry()] + [(f'{i:04d}.txt', b'z', stat.S_IFREG)
                                     for i in range(gate.MAX_FILES - 1)]
        self.assertEqual(checked(entries)['archive_integrity'], 'PASS')

    def test_hash_override_cannot_grant_safety_approval(self):
        r = checked([article_entry()])
        self.assertTrue(r['article_sha256_matched'])
        self.assertTrue(r['archive_sha256_matched'])
        self.assertFalse(r['eligible'])
        self.assertEqual(r['human_content_review'], 'NOT_PERFORMED')

    def test_no_articles_rejected(self):
        r = checked([('notes.txt', b'a', stat.S_IFREG)])
        self.assertIn('article_identity_cardinality', r['failures'])

    def test_double_articles_rejected_even_in_subfolder(self):
        r = checked([article_entry(), article_entry('nested/'+gate.ARTICLE_MEMBER)])
        self.assertIn('article_identity_cardinality', r['failures'])

    def test_bad_article_hash_rejected(self):
        raw = make_zip([article_entry()])
        r = gate.inspect(raw, expected_zip_sha=gate.sha256(raw),
                         expected_article_sha='0'*64)
        self.assertIn('article_sha256_mismatch', r['failures'])

    def test_zip_hash_mismatch_rejected(self):
        raw = make_zip([article_entry()])
        r = gate.inspect(raw, expected_zip_sha='0'*64,
                         expected_article_sha=gate.sha256(ARTICLE))
        self.assertIn('zip_sha256_mismatch', r['failures'])

    def test_unreadable_zip_rejected(self):
        r = gate.inspect(b'not a zip', expected_zip_sha=gate.sha256(b'not a zip'),
                         expected_article_sha=gate.sha256(ARTICLE))
        self.assertIn('invalid_zip', r['failures'])

    def test_sha_validation_cannot_use_uppercase(self):
        r = gate.inspect(make_zip([article_entry()]), expected_zip_sha='A'*64)
        self.assertEqual(r['failures'], ['invalid_expected_sha256'])

    def test_nonbytes_rejected(self):
        r = gate.inspect('not bytes')
        self.assertEqual(r['archive_integrity'], 'FAIL')

    def test_directory_suffix_not_allowed_in_file_name(self):
        self.assertFalse(gate.safe_name('folder/'))

    def test_file_suffix_not_allowed_for_directory(self):
        self.assertFalse(gate.safe_directory_name('folder'))

    def test_canonical_identity_normalization(self):
        self.assertEqual(gate.canonical_member('Kelvin.txt'), gate.canonical_member('Kelvin.TXT'))

    def test_canonical_directory_slash(self):
        self.assertEqual(gate.canonical_member('Folder/'), gate.canonical_member('folder'))

    def test_budget_flood_has_precise_member_count(self):
        entries = [article_entry()] + [(f'a{i:04d}.txt', b'x', stat.S_IFREG)
                                     for i in range(gate.MAX_FILES)]
        self.assertEqual(checked(entries)['archive_member_count'], gate.MAX_FILES + 1)

    def test_no_actual_article_bytes_needed_for_directory_check(self):
        r = checked([('bad/', b'', stat.S_IFLNK), article_entry()])
        self.assertTrue(r['article_sha256_matched'])
        self.assertEqual(r['archive_integrity'], 'FAIL')

    def test_unsafe_name_has_explicit_structural_failure(self):
        r = checked([article_entry(), ('CON.txt', b'bad', stat.S_IFREG)])
        self.assertIn('unsafe_member_name', r['failures'])

    def test_extra_regular_member_allowed_under_hash_override_but_no_release(self):
        r = checked([article_entry(), ('notes.md', b'private only', stat.S_IFREG)])
        self.assertEqual(r['archive_integrity'], 'PASS')
        self.assertFalse(r['eligible'])


UNSAFE_NAMES = [
    'CON.txt', 'NUL.md', 'PRN.html', 'AUX.json',
    'com1.csv', 'com9.md', 'lpt1.pdf', 'LPT9.PNG',
    'folder/CON.txt', 'folder/nul.txt',
    'bad<name>.txt', 'bad>name.txt', 'bad|name.txt', 'bad?name.txt',
    'bad*name.txt', 'bad"name.txt',
    'trailing. ', 'trailing.txt ', 'folder /bad.txt',
    'folder./a.txt', 'folder/../a.txt', 'folder//a.txt',
    'folder/./a.txt', 'folder/.hidden.txt',
    'bidi\u202e.html', 'zero\u200bwidth.txt', 'zwj\u200dname.txt',
    'unicode\u2066isolate.txt', 'null\x00byte.txt',
    'slash\\back.txt', 'colon:drive.txt',
    'decomposed_e\u0301.txt', 'control\x85.txt',
    '/absolute.txt', 'folder\nline.txt', 'folder\rcr.txt',
    'folder\tname.txt', 'file.txt/',
]


def _unsafe_case(name):
    def test(self):
        self.assertFalse(gate.safe_name(name), repr(name))
    return test

for i, name in enumerate(UNSAFE_NAMES):
    setattr(ArchivePreflight, f'test_unsafe_member_{i:02d}', _unsafe_case(name))


if __name__ == '__main__':
    unittest.main()
