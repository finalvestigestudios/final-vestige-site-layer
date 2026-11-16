#!/usr/bin/env python3
import hashlib
from pathlib import Path
import tempfile
import unittest
from qa.assemble import assemble,git_blob,SOURCES,ROOT

class AssembleQA(unittest.TestCase):
    def test_pinned_exact_four_deps(self):
        self.assertEqual(len(SOURCES),4)
        js=(ROOT/'assets/research-desk-r406.js').read_bytes()
        self.assertEqual(git_blob(js),'a925ef792a4f894208f88d8edb3a7b4620b3028f')
    def test_missing_original_sources_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError): assemble(Path(d),Path(d))
    def test_tampered_original_sources_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'templates').mkdir();(root/'templates/ledger.html').write_text('FAKE NASA')
            with self.assertRaises(ValueError):assemble(root,root)
    def test_hash_is_git_object_not_plain_sha1(self):
        b=b'hello';self.assertNotEqual(git_blob(b),hashlib.sha1(b).hexdigest())

if __name__=='__main__':unittest.main()
