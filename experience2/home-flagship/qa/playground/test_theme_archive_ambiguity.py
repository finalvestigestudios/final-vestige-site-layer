"""Theme ZIP ambiguity regressions: synthetic bytes, NOT the official Assembler ZIP.

Run: python -m unittest -v test_theme_archive_ambiguity.py
"""
import hashlib
import io
import unittest
import warnings
import zipfile
from make_offline_private_bundle import validate_theme

STYLE=b'/*\nTheme Name: Assembler\n*/\n'
BASE=[
    ('assembler/style.css', STYLE),
    ('assembler/theme.json', b'{"version": 2}'),
    ('assembler/templates/index.html', b'<!-- wp:group /-->'),
    ('assembler/functions.php', b'UNIQUE_PHP_PAYLOAD_123'),
]

def archive(entries=BASE, compression=zipfile.ZIP_STORED):
    stream=io.BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        with zipfile.ZipFile(stream,'w',compression=compression) as z:
            for name,content in entries:
                z.writestr(name,content)
    return stream.getvalue()

def admit(data):
    return validate_theme(data, hashlib.sha256(data).hexdigest())

class ThemeArchiveAmbiguityTests(unittest.TestCase):
    def test_valid_base(self):
        self.assertTrue(admit(archive())['all_member_crcs_verified'])

    def test_valid_deflated(self):
        self.assertTrue(admit(archive(compression=zipfile.ZIP_DEFLATED))['names_unique_casefold'])

    def test_duplicate_member_rejected_even_when_archive_rehashed(self):
        with self.assertRaisesRegex(Exception, 'duplicate'):
            admit(archive(BASE+[('assembler/style.css',STYLE)]))

    def test_case_colliding_member_rejected_even_when_archive_rehashed(self):
        with self.assertRaisesRegex(Exception, 'case-colliding'):
            admit(archive(BASE+[('assembler/STYLE.CSS',STYLE)]))

    def test_backslash_alias_rejected_even_when_archive_rehashed(self):
        with self.assertRaisesRegex(Exception, 'ambiguous'):
            admit(archive(BASE+[('assembler/..\\bad.php',b'do not install')]))

    def test_dot_path_rejected_even_when_archive_rehashed(self):
        with self.assertRaisesRegex(Exception, 'noncanonical'):
            admit(archive(BASE+[('assembler/./extra.css',b'x')]))

    def test_doubled_slash_rejected_even_when_archive_rehashed(self):
        with self.assertRaisesRegex(Exception, 'noncanonical'):
            admit(archive(BASE+[('assembler//extra.css',b'x')]))

    def test_colon_path_rejected_even_when_archive_rehashed(self):
        with self.assertRaisesRegex(Exception, 'ambiguous'):
            admit(archive(BASE+[('assembler/C:foo.php',b'x')]))

    def test_parent_traversal_rejected_even_when_archive_rehashed(self):
        with self.assertRaisesRegex(Exception, 'noncanonical'):
            admit(archive(BASE+[('assembler/../outside.php',b'x')]))

    def test_corrupt_php_member_rejected_even_when_archive_rehashed(self):
        data=archive()
        assert data.count(b'UNIQUE_PHP_PAYLOAD_123')==1
        changed=data.replace(b'UNIQUE_PHP_PAYLOAD_123',b'UNIQUE_PHP_PAYLOAD_456',1)
        with self.assertRaises((zipfile.BadZipFile, RuntimeError)):
            admit(changed)

    def test_missing_required_theme_file_rejected(self):
        with self.assertRaisesRegex(Exception, 'required Assembler'):
            admit(archive(BASE[1:]))

    def test_mismatched_archive_digest_rejected(self):
        with self.assertRaisesRegex(Exception, 'SHA-256 mismatch'):
            validate_theme(archive(),'0'*64)

    def test_directory_entry_supported(self):
        self.assertTrue(admit(archive([('assembler/', b''), ('assembler/templates/',b'')]+BASE))['all_member_crcs_verified'])

if __name__ == '__main__':
    unittest.main()
