#!/usr/bin/env python3
"""Negative tests only: original immutable NASA template was not locally available."""
import tempfile
import unittest
from pathlib import Path
from assemble import ROOT, assemble, blob, EXPECTED

class AssembleTests(unittest.TestCase):
 def test_new_source_git_blobs(self):
  for name in ['assets/chronology.css','assets/research-desk-r407.js']:
   self.assertEqual(blob((ROOT/name).read_bytes()),EXPECTED[name])
 def test_missing_original_sources_never_emits(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);out=p/'candidate'
   with self.assertRaisesRegex(ValueError,'missing dependency'):
    assemble(p/'pr158',p/'r404',out)
   self.assertFalse(out.exists())
 def test_modified_original_sources_never_emits(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);pr=p/'pr158';(pr/'templates').mkdir(parents=True)
   (pr/'templates/ledger.html').write_text('<p>fabricated text</p>')
   out=p/'candidate'
   with self.assertRaisesRegex(ValueError,'Git blob mismatch'):
    assemble(pr,p/'r404',out)
   self.assertFalse(out.exists())

if __name__=='__main__':unittest.main(verbosity=2)
