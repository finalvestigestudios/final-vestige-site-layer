"""R344 offline source identity/citation gate adversarial regression; synthetic inputs."""
from datetime import date
import json
from pathlib import Path
import sys
import tempfile
import unittest
from copy import deepcopy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import r344_source_url_identity_citation_hold as m

BASE={'id':'source-one','title':'Example evidence','publisher':'Example Agency',
'kind':'regulator','url':'https://www.example.org/path','supports':'Illustrative claim',
'verified_on':'2026-10-29','human_link_check':False}
def item(**kw):
 x=deepcopy(BASE);x.update(kw);return x
def ticket(**kw):
 x={'ticket_id':'a'*24,'source_id':'source-one','claim_text_sha256':'b'*64,
 'source_use_sha256':'c'*64,'human_claim_source_adjudication':'UNREVIEWED_REQUIRED'}
 x.update(kw);return x

class SourceIdentityTests(unittest.TestCase):
 def test_eight_frozen_files(self):
  self.assertEqual(len(m.SOURCE_PINS),8)
 def test_git_blob_empty(self):
  self.assertEqual(m.git_blob(b''),'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391')
 def test_https_normalized(self):
  self.assertEqual(m.canonical_url('https://WWW.Example.org/a')[0],'https://www.example.org/a')
 def test_http_requires_review(self):
  self.assertIn('HTTP_SOURCE_LINK_REQUIRES_HUMAN_CHECK',m.canonical_url('http://www.example.org/a')[2])
 def test_fragment_and_query_retained(self):
  self.assertEqual(m.canonical_url('https://www.example.org/a?q=x#p2')[0],'https://www.example.org/a?q=x#p2')
 def test_empty_path_normalized(self):
  self.assertEqual(m.canonical_url('https://www.example.org')[0],'https://www.example.org/')
 def test_utm_not_conversion_claim(self):
  self.assertIn('URL_CAMPAIGN_QUERY_NOT_A_SOURCE_IDENTITY_SIGNAL',m.canonical_url('https://www.example.org/?utm_source=fv')[2])
 def test_good_record(self):
  e,r=m.record_errors(item(),'register.json');self.assertFalse(e);self.assertEqual(r['verified_on'],'2026-10-29')
 def test_unverified_source_review(self):
  e,r=m.record_errors(item(verified_on=None),'register.json');self.assertFalse(e);self.assertIn('UNVERIFIED_RESEARCH_SOURCE_DO_NOT_CITE',r['notes'])
 def test_nonboolean_check(self):
  for v in ('true',1,0,[],{}):
   with self.subTest(v=v):
    self.assertTrue(any('NONBOOLEAN_HUMAN' in e for e in m.record_errors(item(human_link_check=v),'register.json')[0]))
 def test_future_date(self):
  self.assertIn('FUTURE_VERIFICATION_CLAIM:source-one',m.record_errors(item(verified_on='2026-11-14'),'register.json')[0])
 def test_bad_date(self):
  self.assertIn('BAD_VERIFICATION_DATE:source-one',m.record_errors(item(verified_on='2026-02-31'),'register.json')[0])
 def test_human_link_flag_does_not_approve(self):
  self.assertIn('HUMAN_LINK_FLAG_REQUIRES_INDEPENDENT_REVIEW_RECORD',m.record_errors(item(human_link_check=True),'register.json')[1]['notes'])
 def test_hash_repeatability(self):
  a=m.record_errors(item(),'register.json')[1]['source_identity_sha256']
  b=m.record_errors(item(),'fragments/food.json')[1]['source_identity_sha256']
  self.assertEqual(a,b)
 def test_url_change_changes_hash(self):
  a=m.record_errors(item(),'register.json')[1]['source_identity_sha256']
  b=m.record_errors(item(url='https://else.example.org'),'register.json')[1]['source_identity_sha256']
  self.assertNotEqual(a,b)
 def test_support_change_changes_substantive_hash(self):
  a=m.record_errors(item(),'register.json')[1]['substantive_sha256']
  b=m.record_errors(item(supports='another'),'register.json')[1]['substantive_sha256']
  self.assertNotEqual(a,b)
 def test_single_source(self):
  c=m.catalog_from_records({'register.json':[item()]});self.assertFalse(c['errors'])
 def test_placeholder_upgrade_requires_review(self):
  c=m.catalog_from_records({'register.json':[item(verified_on=None)],'fragments/start.json':[item()]})
  self.assertFalse(c['errors']);self.assertEqual(len(c['events']),1)
  self.assertTrue(c['events'][0]['not_a_human_link_or_claim_check'])
 def test_placeholder_changed_support_requires_review(self):
  c=m.catalog_from_records({'register.json':[item(verified_on=None)],'fragments/start.json':[item(supports='diff')]})
  self.assertFalse(c['errors']);self.assertTrue(c['events'][0]['source_metadata_changed'])
 def test_placeholder_changed_publisher_requires_review(self):
  c=m.catalog_from_records({'register.json':[item(verified_on=None)],'fragments/start.json':[item(publisher='Other')]})
  self.assertFalse(c['errors']);self.assertTrue(c['events'][0]['source_metadata_changed'])
 def test_duplicate_changed_url_fails(self):
  c=m.catalog_from_records({'register.json':[item(verified_on=None)],'fragments/start.json':[item(url='https://else.example.org')]})
  self.assertTrue(c['errors'])
 def test_second_verified_fragment_fails(self):
  c=m.catalog_from_records({'register.json':[item(verified_on=None)],'fragments/food.json':[item()],
                             'fragments/shelter.json':[item(verified_on='2026-11-01',supports='conflicting')]})
  self.assertTrue(any('MULTI_FRAGMENT_CONFLICT' in e for e in c['errors']))
  self.assertEqual(len(c['events']),2);self.assertTrue(c['events'][1]['verified_date_conflict'])
 def test_dup_verified_id_fails(self):
  c=m.catalog_from_records({'register.json':[item()],'fragments/start.json':[item()]})
  self.assertTrue(c['errors'])
 def test_duplicate_within_file_fails(self):
  c=m.catalog_from_records({'register.json':[item(),item()]})
  self.assertTrue(any('ONE_FILE' in e for e in c['errors']))
 def test_one_url_two_ids_review(self):
  c=m.catalog_from_records({'register.json':[item(),item(id='second')]})
  self.assertFalse(c['errors']);self.assertEqual(len(c['warnings']),1)
 def test_catalog_stable_order(self):
  a={'register.json':[item(verified_on=None)],'fragments/start.json':[item()]}
  b={'fragments/start.json':[item()],'register.json':[item(verified_on=None)]}
  self.assertEqual(m.catalog_from_records(a),m.catalog_from_records(b))
 def test_one_ticket_never_approved(self):
  c=m.catalog_from_records({'register.json':[item()]});b=m.bind_tickets(c,[ticket()])
  self.assertFalse(b['errors']);self.assertEqual(b['crosswalk'][0]['adjudication'],'UNREVIEWED_REQUIRED')
  self.assertFalse(b['crosswalk'][0]['claim_source_support_verified'])
 def test_reject_false_approval(self):
  c=m.catalog_from_records({'register.json':[item()]})
  self.assertTrue(m.bind_tickets(c,[ticket(human_claim_source_adjudication='APPROVED')])['errors'])
 def test_reject_unverified_cited(self):
  c=m.catalog_from_records({'register.json':[item(verified_on=None)]})
  self.assertTrue(any('NO_RESEARCH' in x for x in m.bind_tickets(c,[ticket()])['errors']))
 def test_reject_unknown_source(self):
  c=m.catalog_from_records({'register.json':[item()]})
  self.assertTrue(m.bind_tickets(c,[ticket(source_id='absent')])['errors'])
 def test_reject_repeated_ticket(self):
  c=m.catalog_from_records({'register.json':[item()]})
  self.assertTrue(any('COLLIDING' in x for x in m.bind_tickets(c,[ticket(),ticket()])['errors']))
 def test_reject_missing_claim_digest(self):
  c=m.catalog_from_records({'register.json':[item()]})
  self.assertTrue(m.bind_tickets(c,[ticket(claim_text_sha256='invalid')])['errors'])
 def test_reject_missing_source_use_digest(self):
  c=m.catalog_from_records({'register.json':[item()]})
  self.assertTrue(m.bind_tickets(c,[ticket(source_use_sha256='invalid')])['errors'])
 def test_reject_empty_ticket_list(self):
  self.assertTrue(m.bind_tickets({'rows':{}},[])['errors'])
 def test_draft_is_never_qd_pass(self):
  r=m.report([]);self.assertEqual(r['state'],'DRAFT_HARD_HOLD')
  self.assertFalse(r['qualified_qd_pass']);self.assertFalse(r['may_merge'])
 def test_bad_state_never_publishes(self):
  r=m.report(['bad']);self.assertEqual(r['state'],'INVALID_HARD_HOLD');self.assertFalse(r['may_publish'])
 def test_missing_native_fails_closed(self):
  with tempfile.TemporaryDirectory() as d:
   r=m.audit_native(Path(d));self.assertEqual(r['state'],'INVALID_HARD_HOLD')
 def test_catalog_null_rejected(self):
  self.assertTrue(m.catalog_from_records(None)['errors'])
 def test_catalog_wrong_list_type(self):
  self.assertTrue(m.catalog_from_records({'register.json':{}})['errors'])
 def test_record_wrong_type(self):
  self.assertTrue(m.record_errors(None,'register.json')[0])

BAD_URLS={
'javascript':'javascript:alert(1)','file':'file:///tmp/x','data':'data:text/html,x',
'relative':'/foo','protocol-relative':'//example.org/foo','empty':'',
'space-prefix':' https://example.org','space-suffix':'https://example.org ',
'newline':'https://example.org/\nSet-Cookie: x','tab':'https://example.org/\t',
'backslash':'https://example.org\\@evil.org','userinfo':'https://user:pass@example.org',
'atsign':'https://@example.org','localhost':'http://localhost/a',
'local-subdomain':'https://a.local/a','internal':'https://a.internal/a',
'test':'https://a.test/a','invalid':'https://a.invalid/a',
'loopback':'http://127.0.0.1/','private':'http://10.0.0.1/',
'linklocal':'http://169.254.1.1/','multicast':'http://224.0.0.1/',
'hostspace':'https://bad host/a','underscore':'https://bad_host.org/a',
'intranet':'https://intranet/','nul':'https://example.org/\x00',
'port':'https://example.org:8080/a','invalid-port':'https://example.org:abc/a',
'parent-path':'https://example.org/../test','ambiguous-path':'https://example.org//evil'}
for name,url in BAD_URLS.items():
 def run(self,url=url):
  self.assertTrue(m.canonical_url(url)[1],repr(url))
 setattr(SourceIdentityTests,'test_unsafe_url_'+name.replace('-','_'),run)

BAD_RECORDS={
'missing-title':{'title':''},'missing-publisher':{'publisher':' '},
'missing-kind':{'kind':''},'missing-supports':{'supports':''},
'nonstring-title':{'title':[]},'nonstring-publisher':{'publisher':None},
'bad-id':{'id':'Not Valid'},'underscore-id':{'id':'a_b'},
'empty-id':{'id':''},'bad-date':{'verified_on':'tomorrow'},
'future-date':{'verified_on':'2099-01-01'},'invalid-date':{'verified_on':'2026-13-33'},
'nonbool':{'human_link_check':1},'nonbool-string':{'human_link_check':'false'},
'unsafe-host':{'url':'http://localhost'},'nonhttp':{'url':'mailto:test@example.org'}}
for name,change in BAD_RECORDS.items():
 def run(self,change=change):
  self.assertTrue(m.record_errors(item(**change),'register.json')[0])
 setattr(SourceIdentityTests,'test_unsafe_record_'+name.replace('-','_'),run)

class FrozenFileTests(unittest.TestCase):
 def mk(self,root,data):
  p=Path(root)/'sources';p.mkdir();raw=json.dumps(data).encode();(p/'register.json').write_bytes(raw)
  return m.git_blob(raw)
 def test_valid_pinned_synthetic_source(self):
  with tempfile.TemporaryDirectory() as d:
   sha=self.mk(d,{'sources':[item()]});r=m.read_frozen_catalog(Path(d),{'register.json':sha})
   self.assertFalse(r['errors'])
 def test_mutated_git_blob(self):
  with tempfile.TemporaryDirectory() as d:
   self.mk(d,{'sources':[item()]});r=m.read_frozen_catalog(Path(d),{'register.json':'0'*40})
   self.assertTrue(any('GIT_BLOB_DRIFT' in e for e in r['errors']))
 def test_extra_source_file(self):
  with tempfile.TemporaryDirectory() as d:
   sha=self.mk(d,{'sources':[item()]});(Path(d)/'sources'/'extra.json').write_text('{"sources":[]}')
   r=m.read_frozen_catalog(Path(d),{'register.json':sha})
   self.assertTrue(any('FILE_SET_DRIFT' in e for e in r['errors']))
 def test_missing_source_file(self):
  with tempfile.TemporaryDirectory() as d:
   self.assertTrue(m.read_frozen_catalog(Path(d),{'register.json':'0'*40})['errors'])
 def test_symlink_source_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'sources';p.mkdir();(p/'register.json').symlink_to('/tmp/nonexistent')
   self.assertTrue(any('SYMLINK' in e for e in m.read_frozen_catalog(Path(d),{'register.json':'0'*40})['errors']))
 def test_invalid_json_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'sources';p.mkdir();(p/'register.json').write_bytes(b'{')
   self.assertTrue(m.read_frozen_catalog(Path(d),{'register.json':m.git_blob(b'{')})['errors'])
 def test_missing_sources_array_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   sha=self.mk(d,{});self.assertTrue(m.read_frozen_catalog(Path(d),{'register.json':sha})['errors'])
if __name__=='__main__':unittest.main()
