"""R148 native Python test suite, no WordPress/network mutation."""
import unittest
from pathlib import Path
from r148_acceptance_gate import sha,validate_snapshot,review_browser,PINNED_REVIEW_SHA

FIXTURE=Path(__file__).parent/'r146_synthetic_fixture.html'
HTML=FIXTURE.read_text(encoding='utf8')
RECEIPT={
  'release':'STAGING_HOLD','approved_to_publish':False,
  'status':'SOURCE_SNAPSHOT_MATCH_OFFLINE_QA_PENDING',
  'review_sha256':sha(HTML.encode()),'review_characters':len(HTML),
  'source_scope':'RAW_GUTENBERG_CONTENT_NOT_RENDERED_WORDPRESS_THEME',
  'network':'NOT_USED','browser':'NOT_EXECUTED',
  'wordpress':{'id':2017,'link':'https://finalvestige.com/apollo-1-evidence-atlas/'}}

class SnapshotGate(unittest.TestCase):
 def test_fixture_allowed_only_under_explicit_test_mode(self):
  self.assertEqual([],validate_snapshot(HTML,RECEIPT,True))
  self.assertIn('PINNED_WP_EXPORT_NOT_MATCHED',validate_snapshot(HTML,RECEIPT))
 def test_real_source_sha_is_pinned(self):
  self.assertEqual(len(PINNED_REVIEW_SHA),64)
  self.assertNotEqual(sha(HTML.encode()),PINNED_REVIEW_SHA)
 def test_no_metadata(self):
  self.assertIn('R147_RECEIPT_ABSENT',validate_snapshot(HTML,None,True))
 def test_bogus_release(self):
  self.assertIn('UNAUTHORIZED_RELEASE_RECEIPT',validate_snapshot(HTML,{**RECEIPT,'release':'LIVE'},True))
 def test_bogus_approval(self):
  self.assertIn('UNAUTHORIZED_RELEASE_RECEIPT',validate_snapshot(HTML,{**RECEIPT,'approved_to_publish':True},True))
 def test_unpassed_r147(self):
  self.assertIn('R147_SOURCE_GATE_NOT_PASSED',validate_snapshot(HTML,{**RECEIPT,'status':'SOURCE_HOLD'},True))
 def test_same_length_changed_html(self):
  self.assertEqual(len(HTML.replace('Evidence Atlas','Evidence atLas')),len(HTML))
  self.assertIn('REVIEW_EXPORT_HASH_MISMATCH',validate_snapshot(HTML.replace('Evidence Atlas','Evidence atLas'),RECEIPT,True))
 def test_characters_mismatch(self):
  self.assertIn('REVIEW_EXPORT_LENGTH_MISMATCH',validate_snapshot(HTML,{**RECEIPT,'review_characters':1},True))
 def test_faked_source_scope(self):
  self.assertIn('WP_SOURCE_SCOPE_MISMATCH',validate_snapshot(HTML,{**RECEIPT,'source_scope':'LIVE_WORDPRESS'},True))
 def test_spoofed_network(self):
  self.assertIn('SPOOFED_EXECUTION_RECEIPT',validate_snapshot(HTML,{**RECEIPT,'network':'USED'},True))
 def test_spoofed_browser(self):
  self.assertIn('SPOOFED_EXECUTION_RECEIPT',validate_snapshot(HTML,{**RECEIPT,'browser':'PASS'},True))
 def test_wp_destination(self):
  self.assertIn('WP_RECORD_NOT_MATCHED',validate_snapshot(HTML,{**RECEIPT,'wordpress':{'id':2017,'link':'https://example.com'}},False))

if __name__=='__main__':unittest.main()
