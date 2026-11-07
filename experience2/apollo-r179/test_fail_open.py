"""R179 source/behavior checks. Run: python -m unittest -v test_fail_open.py.
Controlled fixtures; never label as installed WordPress, axe, CDN or checkout QA.
"""
import hashlib
from pathlib import Path
import re
import unittest
HERE=Path(__file__).parent
REPLACEMENT=HERE/'source-ledger-semantic-fail-open.js'
ORIGINAL=HERE/'R177-source-ledger-semantic-search.js'
ORIGINAL_GIT_BLOB='d3475008e3da09e9d8a2b156dbe6fffeee53e4a8'

def git_blob(b):return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
class Tests(unittest.TestCase):
 def test_original_r177_witness_exists(self):
  self.assertTrue(ORIGINAL.is_file())
  self.assertIn(b'card.textContent',ORIGINAL.read_bytes())
  self.assertEqual(git_blob(ORIGINAL.read_bytes()),ORIGINAL_GIT_BLOB)
 def test_replacement_unchanged_evidence(self):
  s=REPLACEMENT.read_text()
  for word in ('cards.length!==6','card.textContent','card.hidden=false','failed-open',"search.removeEventListener('input',onInput)",'status.textContent','tools.hidden=true'):
   self.assertIn(word,s)
  self.assertNotIn('innerHTML=',s)
  for forbidden in ('fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage', 'document.cookie', 'navigator.sendBeacon', 'new Image(', 'window.location='):
   self.assertNotIn(forbidden,s)
 def test_fallback_cannot_hide_records(self):
  s=REPLACEMENT.read_text()
  recovery=s.split('const failOpen=()=>{',1)[1].split('};',1)[0]
  self.assertIn('card.hidden=false',recovery)
  self.assertIn('tools.hidden=true',recovery)
  self.assertIn("root.dataset.fvxInitialized='failed-open'",recovery)
 def test_error_guard_after_event(self):
  s=REPLACEMENT.read_text()
  self.assertRegex(s,re.compile(r'onInput=\(\)=>\{[\s\S]+?catch\(_\)\{failOpen\(\);\}'))
 if __name__=='__main__':unittest.main()
