"""Adversarial read-only synthetic tests; no scientific or release approvals."""
from __future__ import annotations
import importlib.util
from io import BytesIO
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('r402_gate', ROOT / 'tools' / 'r402_external_editorial_custody.py')
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
HTML = b'<!doctype html><html><head><title>Private draft</title></head><body>NOT REVIEWED</body></html>'

def archive(rows=None):
    if rows is None:
        rows = [(m.ARTICLE_MEMBER, HTML)]
    buf = BytesIO()
    with ZipFile(buf, 'w', compression=ZIP_DEFLATED) as zf:
        for name, raw in rows:
            zf.writestr(name, raw)
    return buf.getvalue()

def synthetic(raw, article=HTML):
    return m.inspect(raw, expected_zip_sha=m.sha256(raw), expected_article_sha=m.sha256(article))

class CustodyTests(unittest.TestCase):
    def test_good_synthetic_receipt_not_release(self):
        r = synthetic(archive())
        self.assertEqual(r['archive_integrity'], 'PASS')
        self.assertEqual(r['release'], m.STATE)
        self.assertFalse(r['eligible'])
        self.assertEqual(r['qualified_food_safety_review'], 'NOT_GRANTED')
        self.assertEqual(r['human_content_review'], 'NOT_PERFORMED')
    def test_original_not_simulated(self):
        r = m.inspect(archive())
        self.assertIn('zip_sha256_mismatch', r['failures'])
        self.assertIn('article_sha256_mismatch', r['failures'])
    def test_wrong_package_pin(self):
        r = m.inspect(archive(), expected_zip_sha='0'*64, expected_article_sha=m.sha256(HTML))
        self.assertEqual(r['failures'], ['zip_sha256_mismatch'])
    def test_wrong_article_pin(self):
        a=archive()
        r = m.inspect(a, expected_zip_sha=m.sha256(a), expected_article_sha='0'*64)
        self.assertEqual(r['failures'], ['article_sha256_mismatch'])
    def test_missing_article(self):
        self.assertIn('article_identity_cardinality', synthetic(archive([('review.md', b'draft')]))['failures'])
    def test_casefold_duplicate(self):
        rows = [('ledger.csv', b'a'), ('LEDGER.CSV', b'b'), (m.ARTICLE_MEMBER, HTML)]
        self.assertIn('duplicate_casefold_member', synthetic(archive(rows))['failures'])
    def test_both_article_paths(self):
        rows = [(m.ARTICLE_MEMBER, HTML), ('folder/' + m.ARTICLE_MEMBER, HTML)]
        self.assertIn('article_identity_cardinality', synthetic(archive(rows))['failures'])
    def test_empty_archive(self):
        self.assertEqual(m.inspect(b'')['archive_integrity'], 'FAIL')
    def test_not_bytes(self):
        self.assertEqual(m.inspect('not bytes')['failures'], ['missing_or_oversized_zip'])
    def test_oversized_zip(self):
        self.assertIn('missing_or_oversized_zip', m.inspect(b'Z'*(m.MAX_ZIP+1))['failures'])
    def test_invalid_zip(self):
        self.assertIn('invalid_zip', synthetic(b'not a zip')['failures'])
    def test_corrupt_zip(self):
        self.assertEqual(synthetic(archive()[:-15])['archive_integrity'], 'FAIL')
    def test_bad_pin_length(self):
        self.assertEqual(m.inspect(archive(), expected_zip_sha='abc')['failures'], ['invalid_expected_sha256'])
    def test_bad_pin_case(self):
        self.assertEqual(m.inspect(archive(), expected_zip_sha='A'*64)['failures'], ['invalid_expected_sha256'])
    def test_bad_pin_type(self):
        self.assertEqual(m.inspect(archive(), expected_zip_sha=None)['failures'], ['invalid_expected_sha256'])
    def test_extra_reports_allowed_with_new_hash(self):
        a=archive([(m.ARTICLE_MEMBER, HTML), ('source-ledger.csv', b'source')])
        self.assertEqual(synthetic(a)['archive_integrity'], 'PASS')
    def test_changed_article_cannot_reuse_pin(self):
        a=archive([(m.ARTICLE_MEMBER, HTML+b' tampered')])
        r=m.inspect(a, expected_zip_sha=m.sha256(a), expected_article_sha=m.sha256(HTML))
        self.assertIn('article_sha256_mismatch', r['failures'])
    def test_nonregular_symlink(self):
        info=ZipInfo('shortcut.html')
        info.create_system=3
        info.external_attr=(stat.S_IFLNK | 0o777)<<16
        buf=BytesIO()
        with ZipFile(buf,'w') as zf:
            zf.writestr(info,'../../outside')
            zf.writestr(m.ARTICLE_MEMBER, HTML)
        self.assertIn('non_regular_member', synthetic(buf.getvalue())['failures'])
    def test_too_many_members(self):
        rows=[(f'notes/{i:03}.txt', b'x') for i in range(m.MAX_FILES)]+[(m.ARTICLE_MEMBER,HTML)]
        self.assertIn('zip_member_count', synthetic(archive(rows))['failures'])
    def test_one_member_too_big(self):
        rows=[(m.ARTICLE_MEMBER,HTML), ('extra.txt', b'A'*(m.MAX_MEMBER+1))]
        self.assertIn('unbounded_member_size', synthetic(archive(rows))['failures'])
    def test_safe_nested_record(self):
        a=archive([('evidence/record.json', b'{}'), (m.ARTICLE_MEMBER, HTML)])
        self.assertEqual(synthetic(a)['archive_integrity'], 'PASS')
    def test_reordered_package_cannot_reuse_digest(self):
        rows=[(m.ARTICLE_MEMBER,HTML), ('review.md',b'read')]
        a=archive(rows); b=archive(list(reversed(rows)))
        self.assertNotEqual(m.sha256(a),m.sha256(b))
        self.assertIn('zip_sha256_mismatch',m.inspect(b,expected_zip_sha=m.sha256(a),expected_article_sha=m.sha256(HTML))['failures'])
    def test_cli_missing_original_hard_hold(self):
        with tempfile.TemporaryDirectory() as d:
            cmd=[sys.executable,'-I',str(ROOT/'tools'/'r402_external_editorial_custody.py'),'--e395-zip',str(Path(d)/'missing.zip')]
            p=subprocess.run(cmd,capture_output=True,text=True,timeout=10)
            self.assertEqual(p.returncode,2)
            self.assertIn('missing_original_e395_zip',p.stdout)
    def test_cli_synthetic_package_hard_hold(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'fake.zip';path.write_bytes(archive())
            cmd=[sys.executable,'-I',str(ROOT/'tools'/'r402_external_editorial_custody.py'),'--e395-zip',str(path)]
            p=subprocess.run(cmd,capture_output=True,text=True,timeout=10)
            self.assertEqual(p.returncode,2)
            self.assertIn('zip_sha256_mismatch',p.stdout)

class NameRejectionTests(unittest.TestCase):
    pass

BAD_NAMES=[
 '../outside.html','a/../outside.html','/absolute.html','C:/file.html',
 'a\\b.html','a//b.html','./entry.html','a/./entry.html',
 '.hidden.html','a/.hidden.html','tool.js','tool.py','tool.exe','shell.sh',
 'note.php','note.html\x00x','a\nline.html','a\rfile.html','a\tfile.html',
 'a\x7ffile.html','a:b.html','payload.pl','file.bat','file.ps1','node.mjs',
 'dir/','','a/../../z.txt','a\\..\\x.json','a/.git/config.txt',
 'a/__MACOSX/.hidden.html'
]
for i, bad in enumerate(BAD_NAMES):
    def check(self, name=bad):
        self.assertFalse(m.safe_name(name), repr(name))
    setattr(NameRejectionTests,f'test_reject_unsafe_{i:02d}',check)

class NameAcceptanceTests(unittest.TestCase):
    pass
for i, good in enumerate(['source-ledger.csv','original.html','archive/review.md','a/b/c.json','photo.webp','figure.svg','README.txt']):
    def check(self, name=good):
        self.assertTrue(m.safe_name(name),repr(name))
    setattr(NameAcceptanceTests,f'test_accept_document_{i:02d}',check)

if __name__ == '__main__':
    unittest.main()
