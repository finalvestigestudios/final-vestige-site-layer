"""R300 fail-closed synthetic provenance and safety regression tests."""
import importlib.util
from pathlib import Path
from unittest.mock import patch
import tempfile
import unittest

P=Path(__file__).resolve().parents[1]/'tools/r300_metadata_css_pin_hold.py'
S=importlib.util.spec_from_file_location('r300',P)
M=importlib.util.module_from_spec(S)
S.loader.exec_module(M)

class MetadataCSSGateTests(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
  self.root=Path(t.name)
  self.dir=self.root/'preparedness/content/articles';self.dir.mkdir(parents=True)
  self.style=self.root/M.CSS;self.style.parent.mkdir(parents=True)
  self.style.write_bytes(b'/* stylesheet source */\n')
  self.patch_css=patch.object(M,'CSS_OID',M.blob(self.style.read_bytes()))
  self.patch_css.start();self.addCleanup(self.patch_css.stop)
  override={}
  rows=[]
  for i,slug in enumerate(M.OVERRIDES):
   content=('{"slug":"'+slug+'","order":'+str(i)+'}').encode()
   (self.dir/(slug+'.meta.json')).write_bytes(content)
   override[slug]=M.blob(content)
   rows.append({'slug':slug,'meta_oid':'a'*40})
  for i in range(23):
   slug='additional-article-'+str(i)
   content=('{"slug":"'+slug+'"}').encode()
   (self.dir/(slug+'.meta.json')).write_bytes(content)
   rows.append({'slug':slug,'meta_oid':M.blob(content)})
  self.custody={'articles':rows}
  self.p=patch.object(M,'OVERRIDES',override);self.p.start();self.addCleanup(self.p.stop)
  self.prev={'state':'DRAFT_HARD_HOLD','errors':[],
   'native_export_byte_matches':41,'publication_authorized':False,
   'independent_qd_pass':False,'all_41_exports_independently_approved':False}
 def audit(self,prev=None):return M.audit(self.root,self.custody,self.prev if prev is None else prev)
 def check_bad(self,code):
  r=self.audit();self.assertEqual(r['state'],'INVALID_HARD_HOLD');self.assertIn(code,r['errors'])
  self.assertFalse(r['publication_authorized']);self.assertFalse(r['independent_qd_pass'])
  self.assertFalse(r['medical_safety_verified']);self.assertFalse(r['privacy_verified'])
 def test_clean_fixture_still_not_releasable(self):
  r=self.audit();self.assertEqual(r['state'],'DRAFT_HARD_HOLD')
  self.assertEqual(r['article_metadata_pinned'],35)
  self.assertEqual(len(r['r200_metadata_lineage_holds']),12)
  self.assertIsNone(r['paid_order_count']);self.assertIsNone(r['net_revenue_per_1000_qualified_sessions'])
 def test_metadata_drift_must_remain_unadjudicated(self):
  self.assertTrue(all(x['status']=='UNADJUDICATED_METADATA_LINEAGE' for x in self.audit()['r200_metadata_lineage_holds']))
  self.assertIs(self.audit()['lineage_reviewed'],False)
 def test_r200_frozen_meta_change_detected(self):
  self.custody['articles'][13]['meta_oid']='b'*40
  self.check_bad('CHANGED_META:additional-article-1')
 def test_injected_extra_meta_detected(self):
  (self.dir/'extra.meta.json').write_text('{}');self.check_bad('ARTICLE_METADATA_FILE_INVENTORY_CHANGED')
 def test_missing_file_detected(self):
  (self.dir/'additional-article-0.meta.json').unlink();self.check_bad('ARTICLE_METADATA_FILE_INVENTORY_CHANGED')
 def test_css_subtle_comment_edit_detected(self):
  self.style.write_bytes(self.style.read_bytes()+b'/* changed */');self.check_bad('CHANGED_STYLESHEET')
 def test_css_deletion_detected(self):
  self.style.unlink();self.check_bad('MISSING_OR_SYMLINK_STYLESHEET')
 def test_css_symlink_detected(self):
  alt=self.root/'style';alt.write_bytes(self.style.read_bytes());self.style.unlink();self.style.symlink_to(alt)
  self.check_bad('MISSING_OR_SYMLINK_STYLESHEET')
 def test_metadata_symlink_detected(self):
  q=self.dir/'additional-article-0.meta.json';alt=self.root/'metadata';alt.write_bytes(q.read_bytes());q.unlink();q.symlink_to(alt)
  self.check_bad('MISSING_OR_SYMLINK_META:additional-article-0')
 def test_meta_directory_deleted_detected(self):
  for q in self.dir.glob('*'):q.unlink()
  self.dir.rmdir();self.check_bad('ARTICLE_METADATA_DIRECTORY_MISSING')
 def test_duplicate_slug_detected(self):
  self.custody['articles'][13]['slug']=self.custody['articles'][12]['slug']
  self.check_bad('R200_SLUG_INVALID')
 def test_truncated_custody_detected(self):
  self.custody['articles'].pop();self.check_bad('R200_35_ARTICLES_MISSING')
 def test_missing_frozen_articles_detected(self):
  self.custody.pop('articles');self.check_bad('R200_35_ARTICLES_MISSING')
 def test_extra_custody_row_detected(self):
  self.custody['articles'].append({'slug':'extra','meta_oid':'a'*40})
  self.check_bad('R200_35_ARTICLES_MISSING')
 def test_slash_slug_detected(self):
  self.custody['articles'][0]['slug']='../outside';self.check_bad('R200_OVERRIDE_SLUG_MISSING')
 def test_missing_override_slug_detected(self):
  self.custody['articles'][0]['slug']='substitution';self.check_bad('R200_OVERRIDE_SLUG_MISSING')
 def test_previous_export_count_40_rejected(self):
  r=M.audit(self.root,self.custody,dict(self.prev,native_export_byte_matches=40))
  self.assertIn('R299_EXACT_EXPORT_GATE_NOT_VERIFIED',r['errors'])
 def test_previous_published_state_rejected(self):
  r=M.audit(self.root,self.custody,dict(self.prev,publication_authorized=True))
  self.assertIn('R299_EXACT_EXPORT_GATE_NOT_VERIFIED',r['errors'])
 def test_previous_qd_pass_rejected(self):
  r=M.audit(self.root,self.custody,dict(self.prev,independent_qd_pass=True))
  self.assertIn('R299_EXACT_EXPORT_GATE_NOT_VERIFIED',r['errors'])
 def test_previous_invalid_state_rejected(self):
  r=M.audit(self.root,self.custody,dict(self.prev,state='INVALID_HARD_HOLD'))
  self.assertIn('R299_EXACT_EXPORT_GATE_NOT_VERIFIED',r['errors'])
 def test_previous_errors_rejected(self):
  r=M.audit(self.root,self.custody,dict(self.prev,errors=['missing-citation']))
  self.assertIn('R299_EXACT_EXPORT_GATE_NOT_VERIFIED',r['errors'])
 def test_previous_invalid_format_rejected(self):
  r=M.audit(self.root,self.custody,'wrong-type');self.assertEqual(r['state'],'INVALID_HARD_HOLD')
 def test_r300_entry_with_no_authentic_upstream_fails_closed(self):
  with self.assertRaises(ValueError):M.run(self.root)
 def test_file_outside_repo_cannot_pass(self):
  with tempfile.TemporaryDirectory() as t:
   f=Path(t)/'outside';f.write_text('data');self.assertFalse(M.safe_file(self.root,f))
 def test_git_blob_oid_not_plain_sha(self):
  from hashlib import sha1
  self.assertNotEqual(M.blob(b'abc'),sha1(b'abc').hexdigest())

# Each of the 35 metadata files receives its own independent mutation test.
def make_case(slug):
 def test(self):
  p=self.dir/(slug+'.meta.json');p.write_bytes(p.read_bytes()+b' ')
  self.check_bad('CHANGED_META:'+slug)
 return test
for _slug in list(M.OVERRIDES)+['additional-article-'+str(i) for i in range(23)]:
 setattr(MetadataCSSGateTests,'test_mutation_'+_slug.replace('-','_'),make_case(_slug))

if __name__=='__main__':unittest.main()
