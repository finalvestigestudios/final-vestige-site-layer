"""R211: synthetic-only source/output tamper tests. Never touch genuine sources."""
from __future__ import annotations
import importlib.util
import os
from pathlib import Path
import stat
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'tools' / 'r211_path_guard.py'
spec = importlib.util.spec_from_file_location('r211_guard', MODULE)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

# Names are only synthetic collision targets. One test per article position.
NAMES = tuple(f'preparedness/content/articles/article-{n:02d}.body.html' for n in range(1,36))

class GuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='fv-r211-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'checkout'
        self.root.mkdir()
        self.out = self.base / 'reports'
        self.out.mkdir()

    def seed(self, relative='source.txt', content=b'IMMUTABLE SOURCE'):
        p = self.root / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
        return p

    def test_reads_ordinary_files_without_change(self):
        p = self.seed()
        self.assertEqual(g.read_files(self.root,['source.txt']),{'source.txt':b'IMMUTABLE SOURCE'})
        self.assertEqual(p.read_bytes(),b'IMMUTABLE SOURCE')

    def test_writes_new_report_only_outside_checkout(self):
        p = self.out / 'first.json'
        g.write_new_report(p,self.root,'{"state":"INVALID_HARD_HOLD"}\n')
        self.assertEqual(p.read_text(),'{"state":"INVALID_HARD_HOLD"}\n')
        self.assertEqual(stat.S_IMODE(p.stat().st_mode),0o600)

    def test_rejects_existing_output_preserves_bytes(self):
        p = self.out / 'existing.json'; p.write_text('DO NOT TOUCH')
        with self.assertRaisesRegex(g.GuardViolation,'already exists'):
            g.write_new_report(p,self.root,'REPLACE')
        self.assertEqual(p.read_text(),'DO NOT TOUCH')

    def test_rejects_output_inside_checkout(self):
        p=self.root/'report.json'
        with self.assertRaisesRegex(g.GuardViolation,'protected checkout'):
            g.write_new_report(p,self.root,'WRONG')
        self.assertFalse(p.exists())

    def test_rejects_report_alias_in_symlinked_directory(self):
        (self.out/'alias').symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(g.GuardViolation):
            g.write_new_report(self.out/'alias'/'report.json',self.root,'WRONG')
        self.assertFalse((self.root/'report.json').exists())

    def test_rejects_existing_report_symlink_to_source(self):
        p=self.seed(); link=self.out/'link.json';link.symlink_to(p)
        with self.assertRaises(g.GuardViolation):
            g.write_new_report(link,self.root,'DESTROY')
        self.assertEqual(p.read_bytes(),b'IMMUTABLE SOURCE')

    def test_rejects_existing_report_hardlink_to_source(self):
        p=self.seed(); link=self.out/'linked.json';os.link(p,link)
        with self.assertRaises(g.GuardViolation):
            g.write_new_report(link,self.root,'DESTROY')
        self.assertEqual(p.read_bytes(),b'IMMUTABLE SOURCE')

    def test_rejects_checkout_root_symlink(self):
        self.seed(); alias=self.base/'alias-root';alias.symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(g.GuardViolation):g.read_files(alias,['source.txt'])

    def test_rejects_checkout_ancestor_symlink(self):
        self.seed(); alias=self.base/'alias-ancestor';alias.symlink_to(self.base,target_is_directory=True)
        with self.assertRaises(g.GuardViolation):g.read_files(alias/'checkout',['source.txt'])

    def test_rejects_source_directory_symlink(self):
        self.seed('real/source.txt')
        (self.root/'linked').symlink_to(self.root/'real',target_is_directory=True)
        with self.assertRaises(g.GuardViolation):g.read_files(self.root,['linked/source.txt'])

    def test_rejects_source_file_symlink(self):
        self.seed(); (self.root/'linked.txt').symlink_to(self.root/'source.txt')
        with self.assertRaises(g.GuardViolation):g.read_files(self.root,['linked.txt'])

    def test_rejects_fifo_without_blocking(self):
        os.mkfifo(self.root/'pipe')
        with self.assertRaisesRegex(g.GuardViolation,'non-regular'):
            g.read_files(self.root,['pipe'])

    def test_rejects_missing_source(self):
        with self.assertRaises(g.GuardViolation):g.read_files(self.root,['missing.txt'])

    def test_rejects_noncanonical_paths(self):
        for name in ('', '../source.txt', '/etc/passwd','./source.txt',
                     'sub//file.txt','sub/../source.txt','source\\bad.txt'):
            with self.subTest(name=name):
                with self.assertRaises(g.GuardViolation):g.read_files(self.root,[name])

    def test_rejects_symlinked_output_parent(self):
        alias=self.base/'output-alias';alias.symlink_to(self.out,target_is_directory=True)
        with self.assertRaises(g.GuardViolation):
            g.write_new_report(alias/'new.json',self.root,'BAD')
        self.assertFalse((self.out/'new.json').exists())

    def test_rejects_missing_output_parent(self):
        with self.assertRaises(g.GuardViolation):
            g.write_new_report(self.base/'absent'/'report.json',self.root,'BAD')

    def test_rejects_report_at_protected_checkout_root(self):
        with self.assertRaises(g.GuardViolation):
            g.write_new_report(self.root,self.root,'BAD')

    def test_rejects_report_in_missing_checkout_descendant(self):
        missing=self.base/'missing-checkout'
        with self.assertRaises(g.GuardViolation):
            g.write_new_report(missing/'new.json',missing,'BAD')

    def test_read_with_nested_dir_preserves_bytes(self):
        p=self.seed('sub/inner/item.txt',b'SOURCE VALUE')
        self.assertEqual(g.read_files(self.root,['sub/inner/item.txt'])['sub/inner/item.txt'],b'SOURCE VALUE')
        self.assertEqual(p.read_bytes(),b'SOURCE VALUE')

    def test_second_write_exclusivity(self):
        p=self.out/'once.json'
        g.write_new_report(p,self.root,'FIRST')
        with self.assertRaises(g.GuardViolation):g.write_new_report(p,self.root,'SECOND')
        self.assertEqual(p.read_text(),'FIRST')

    def test_report_root_does_not_create_parent(self):
        with self.assertRaises(g.GuardViolation):
            g.write_new_report(self.out/'newdir'/'file.json',self.root,'BAD')
        self.assertFalse((self.out/'newdir').exists())


def _protected_original(n):
    def test(self):
        name=NAMES[n-1]
        p=self.seed(name, f'AUTHENTIC-FIXTURE-{n:02d}'.encode())
        old=p.read_bytes()
        # R210's former --report path could overwrite protected input even on INVALID.
        with self.assertRaises(g.GuardViolation):
            g.write_new_report(p,self.root,'{"state":"INVALID_HARD_HOLD"}')
        self.assertEqual(p.read_bytes(),old)
    return test

for index in range(1,36):
    setattr(GuardTests,f'test_protected_article_{index:02d}_cannot_be_report',_protected_original(index))

if __name__=='__main__':unittest.main()
