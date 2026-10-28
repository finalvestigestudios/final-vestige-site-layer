import json
import os
import tempfile
import unittest
from pathlib import Path

from packet_safety import (
    load_checklist, match_relative_path, scan_files, snapshot_digest,
    validate_checklist, write_new_report,
)


class PacketSafetyTests(unittest.TestCase):
    def test_glob_anchored_and_recursive(self):
        matrix = (
            ('application*.pdf', 'application1.pdf', True),
            ('application*.pdf', 'old/application1.pdf', False),
            ('supporting/*', 'supporting/letter.docx', True),
            ('supporting/*', 'supporting/archive/letter.docx', False),
            ('**/*.pdf', 'application.pdf', True),
            ('**/*.pdf', 'supporting/letter.pdf', True),
            ('**/*.pdf', 'a/b/c.pdf', True),
            ('budget?.csv', 'BUDGET1.CSV', True),
            ('one/**/proof*.pdf', 'one/proof.pdf', True),
            ('one/**/proof*.pdf', 'one/two/three/proof.pdf', True),
            ('one/**/proof*.pdf', 'two/one/proof.pdf', False),
            ('invoice[12].pdf', 'invoice3.pdf', False),
        )
        for pattern, name, expected in matrix:
            with self.subTest(pattern=pattern, name=name):
                self.assertIs(match_relative_path(name, pattern), expected)

    def test_bad_patterns_and_rules_rejected(self):
        base = {'name': 'Document', 'pattern': '*.pdf'}
        for pattern in ('', '../secret.pdf', '/etc/passwd', 'C:/data/*.pdf',
                        'foo//bar.pdf', 'foo/./bar.pdf', 'foo/../bar.pdf',
                        'foo\\bar.pdf', 'x:\\private', 'file\x00.pdf'):
            with self.subTest(pattern=pattern):
                with self.assertRaises(ValueError):
                    validate_checklist({'rules': [{**base, 'pattern': pattern}]})
        for rule in (
            {**base, 'allow_empty': 'false'},
            {**base, 'minimum': True},
            {**base, 'maximum': False},
            {**base, 'minimum': 2, 'maximum': 1},
            {**base, 'max_size_mb': float('inf')},
            {**base, 'max_size_mb': float('nan')},
            {**base, 'extensions': ['pdf']},
            {**base, 'extensions': ['.pdf ', '.csv']},
        ):
            with self.subTest(rule=rule):
                with self.assertRaises(ValueError):
                    validate_checklist({'rules': [rule]})

    def test_duplicate_rules_and_invalid_overall_cap(self):
        rule = {'name': 'Invoice', 'pattern': '*.pdf'}
        with self.assertRaises(ValueError):
            validate_checklist({'rules': [rule, {**rule, 'name': 'INVOICE'}]})
        for value in (-1, 0, '20', float('inf'), float('nan'), False):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_checklist({'rules': [rule], 'max_total_size_mb': value})
        with self.assertRaises(ValueError):
            validate_checklist({'rules': [rule], 'forbid_unmatched': 'yes'})

    def test_valid_limits_and_rule_globs(self):
        config = {'title': 'Submission', 'forbid_unmatched': True,
                  'max_total_size_mb': 25,
                  'rules': [{'name': 'Proof', 'pattern': '**/*.pdf',
                             'minimum': 0, 'maximum': 15, 'allow_empty': False,
                             'extensions': ['.pdf'], 'max_size_mb': 20}]}
        self.assertIs(validate_checklist(config), config)

    def test_rules_hash_and_reject_invalid_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rules = root / 'check.json'
            rules.write_text('{"rules":[{"name":"a","pattern":"*.pdf"}]}', encoding='utf-8')
            content, digest = load_checklist(rules)
            self.assertEqual(content['rules'][0]['name'], 'a')
            self.assertEqual(len(digest), 64)
            rules.write_text('"oops"', encoding='utf-8')
            with self.assertRaises(ValueError):
                load_checklist(rules)
            rules.write_bytes(b' ' * (1024 * 1024 + 1))
            with self.assertRaises(ValueError):
                load_checklist(rules)

    def test_scan_metadata_unicode_and_symlink_skip(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'A.PDF').write_bytes(b'123')
            # Case-distinct file names cannot coexist on standard Windows volumes.
            if os.name != 'nt':
                (root / 'a.pdf').write_bytes(b'456')
            (root / 'nested').mkdir()
            (root / 'nested' / 'ok.txt').write_bytes(b'')
            outside = root.parent / ('not-inside-' + root.name)
            outside.write_text('private', encoding='utf-8')
            try:
                try:
                    (root / 'alias').symlink_to(outside)
                    (root / 'linked_folder').symlink_to(root / 'nested', target_is_directory=True)
                except (OSError, NotImplementedError):
                    pass
                files, errors = scan_files(root)
                self.assertEqual(len(files), 2 if os.name == 'nt' else 3)
                self.assertTrue(all('mtime_ns' in f for f in files))
                if os.name != 'nt':
                    self.assertTrue(any('collision' in e['message'] for e in errors))
                if (root / 'alias').is_symlink():
                    self.assertTrue(any(e['file'] == 'alias' for e in errors))
                if (root / 'linked_folder').is_symlink():
                    self.assertTrue(any(e['file'] == 'linked_folder' for e in errors))
                self.assertEqual(snapshot_digest(files, errors),
                                 snapshot_digest(list(reversed(files)), list(reversed(errors))))
            finally:
                outside.unlink(missing_ok=True)

    def test_safe_export_refuses_overwrite_and_packet_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'packet'
            root.mkdir()
            input_file = root / 'source.csv'
            input_file.write_text('KEEP', encoding='utf-8')
            checklist = Path(directory) / 'rules.json'
            checklist.write_text('{}', encoding='utf-8')
            report = Path(directory) / 'report.json'
            write_new_report(report, '{"ok": true}', packet_folder=root, protected=(checklist,))
            with self.assertRaises(FileExistsError):
                write_new_report(report, '{}', packet_folder=root)
            with self.assertRaises(ValueError):
                write_new_report(input_file, '{}', packet_folder=root)
            with self.assertRaises(ValueError):
                write_new_report(checklist, '{}', packet_folder=root, protected=(checklist,))
            self.assertEqual(input_file.read_text(encoding='utf-8'), 'KEEP')
            self.assertEqual(json.loads(report.read_text(encoding='utf-8')), {'ok': True})


if __name__ == '__main__':
    unittest.main()
