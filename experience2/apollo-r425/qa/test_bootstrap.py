#!/usr/bin/env python3
"""Offline adversarial tests of the exact-Git-object source checkout contract."""
import pathlib, tempfile, unittest
import bootstrap_exact_sources as s

class SourceBootstrapTests(unittest.TestCase):
 def test_authentic_reviewed_contract_six_sources(self):
  self.assertEqual(len(s.BLOBS),6)
  self.assertEqual(s.BLOBS['experience2/research-desk/templates/ledger.html'],'403d128c57b9bc82dac7c619651689070edef86c')
  self.assertEqual(s.BLOBS['experience2/apollo-r423/staging-research-desk-bridge.php'],'1491e5eca2f749849136d0b41cc9a2ca7b255023')
 def test_git_object_hash_known_fixture(self):
  self.assertEqual(s.git_blob(b'hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a')
 def test_wrong_blob_rejected_before_any_write(self):
  with tempfile.TemporaryDirectory() as d:
   out=pathlib.Path(d)/'checkout'
   with self.assertRaisesRegex(ValueError,'identity validation failed'):
    s.bootstrap(out, lambda sha, token: b'forged')
   self.assertFalse(out.exists())
 def test_absent_network_or_permission_is_not_success(self):
  with tempfile.TemporaryDirectory() as d:
   out=pathlib.Path(d)/'checkout'
   def offline(sha, token): raise OSError('offline / access denied')
   with self.assertRaisesRegex(OSError,'offline'):
    s.bootstrap(out, offline)
   self.assertFalse(out.exists())
 def test_preexisting_checkout_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   out=pathlib.Path(d)/'checkout';out.mkdir()
   with self.assertRaisesRegex(ValueError,'must not exist'):
    s.bootstrap(out,lambda sha, token: b'')
 def test_symlink_destination_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);outside=root/'elsewhere';outside.mkdir();link=root/'checkout';link.symlink_to(outside,target_is_directory=True)
   with self.assertRaisesRegex(ValueError,'must not exist'):
    s.bootstrap(link,lambda sha,token:b'')
 def test_invalid_sha_refused(self):
  for bad in ['../secrets','x'*40,'ABCDEF'*7]:
   with self.assertRaises(ValueError):s.fetch_blob(bad)
 def test_non_byte_content_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(ValueError,'identity validation failed'):
    s.bootstrap(pathlib.Path(d)/'checkout', lambda sha,token:'not bytes')

if __name__=='__main__': unittest.main(verbosity=2)
