"""R362 source alias and provenance regression suite; synthetic, not QD approval."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import r362_alias_review_gate as g


def fixture():
 a={'id':'source-a','url':'https://agency.test/guide','supports':'A'}
 b={'id':'source-b','url':'https://agency.test/guide/','supports':'B'}
 c={'id':'source-c','url':'https://agency.test/other','supports':'C'}
 f={'base':[a,c],'food':[b]}
 group={'url':a['url'],'review_status':'pending-human-source-and-reading-scope-review',
  'reviewer':None,'reviewed_on':None,'identities':[
   {'origin':'base','row_index':0,'id':'source-a'},
   {'origin':'food','row_index':0,'id':'source-b'}],
  'variants':[{'origin':'base','row_index':0,'source':copy.deepcopy(a)},
              {'origin':'food','row_index':0,'source':copy.deepcopy(b)}]}
 c={'status':'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
    'raw_source_rows':3,'unique_source_urls':3,'duplicate_url_groups':1,'duplicate_id_groups':0,
    'groups':[group]}
 return c,f


def set_path(root,path,value):
 at=root
 for name in path[:-1]:at=at[name]
 at[path[-1]]=value

def del_path(root,path):
 at=root
 for name in path[:-1]:at=at[name]
 del at[path[-1]]

class Tests(unittest.TestCase):
 def test_clean_synthetic(self):self.assertEqual(g.verify(*fixture()),[])
 def test_missing_checkout(self):
  with tempfile.TemporaryDirectory() as t:self.assertEqual(g.audit(t)['status'],'INVALID_HARD_HOLD')
 def test_cli_exit_hard_hold(self):
  with tempfile.TemporaryDirectory() as t:
   p=subprocess.run([sys.executable,g.__file__,'--repo-root',t],capture_output=True,text=True)
   self.assertEqual(p.returncode,2)
   self.assertEqual(json.loads(p.stdout)['status'],'INVALID_HARD_HOLD')
 def test_git_blob(self):self.assertEqual(g.blob(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
 def test_status_not_pass(self):self.assertEqual(g.receipt([])['status'],'REVIEW_REQUIRED_HARD_HOLD')
 def test_error_is_hold(self):self.assertEqual(g.receipt(['a'])['status'],'INVALID_HARD_HOLD')
 def test_no_approval_flags(self):self.assertFalse(any(g.receipt([])[k] for k in g.HOLD))
 def test_no_mutation(self):
  a=fixture();saved=copy.deepcopy(a);g.verify(*a);self.assertEqual(a,saved)
 def test_strict_requires_original_inventory(self):self.assertIn('ORIGINAL_INVENTORY_DRIFT',g.verify(*fixture(),pin=True))
 def test_unknown_input(self):self.assertEqual(g.verify(None,{}),['INVALID_INPUT'])
 def test_repeated_json_key(self):
  with self.assertRaises(ValueError):json.loads('{"a":1,"a":2}',object_pairs_hook=g.pairs)
 def test_alias_keeps_query(self):self.assertNotEqual(g.alias('https://a.test/q'),g.alias('https://a.test/q?a=1'))
 def test_alias_keeps_fragment(self):self.assertNotEqual(g.alias('https://a.test/q'),g.alias('https://a.test/q#x'))
 def test_alias_keeps_host(self):self.assertNotEqual(g.alias('https://a.test/q'),g.alias('https://b.test/q'))
 def test_alias_removes_terminal_slash_only(self):self.assertEqual(g.alias('https://a.test/q/'),g.alias('https://a.test/q'))

# Mutation cases each becomes a distinct executable unittest, not subtests.
CASES=[
 ('raw_rows',0,['raw_source_rows'],7,'COUNT_DRIFT:raw_source_rows'),
 ('unique_urls',0,['unique_source_urls'],99,'COUNT_DRIFT:unique_source_urls'),
 ('dup_urls',0,['duplicate_url_groups'],2,'COUNT_DRIFT:duplicate_url_groups'),
 ('dup_ids',0,['duplicate_id_groups'],1,'COUNT_DRIFT:duplicate_id_groups'),
 ('fragment_not_list',1,['food'],None,'BAD_FRAGMENT:food'),
 ('fragment_empty',1,['food'],[],'COUNT_DRIFT:raw_source_rows'),
 ('source_not_object',1,['food',0],True,'BAD_SOURCE:food:0'),
 ('source_no_url',1,['food',0,'url'],None,'BAD_SOURCE:food:0'),
 ('source_http',1,['food',0,'url'],'http://agency.test/guide','BAD_SOURCE:food:0'),
 ('source_number_url',1,['food',0,'url'],3,'BAD_SOURCE:food:0'),
 ('source_id_number',1,['food',0,'id'],8,'BAD_SOURCE_ID:food:0'),
 ('source_id_missing',1,['food',0,'id'],None,'BAD_SOURCE_ID:food:0'),
 ('source_extra',1,['food'],[{'id':'extra','url':'https://agency.test/another'}],'COUNT_DRIFT:duplicate_url_groups'),
 ('group_nonlist',0,['groups'],42,'MISSING_GROUPS'),
 ('group_removed',0,['groups'],[],'GROUP_CLOSURE_DRIFT'),
 ('group_bad',0,['groups',0],None,'BAD_GROUP'),
 ('group_bad_url',0,['groups',0,'url'],None,'BAD_GROUP'),
 ('group_new_url',0,['groups',0,'url'],'https://agency.test/other','NOT_DUPLICATED'),
 ('identities_missing',0,['groups',0,'identities'],None,'BAD_MEMBERS'),
 ('variants_missing',0,['groups',0,'variants'],None,'BAD_MEMBERS'),
 ('identity_removed',0,['groups',0,'identities'],[{'origin':'base','row_index':0,'id':'source-a'}],'IDENTITY_CLOSURE'),
 ('variant_removed',0,['groups',0,'variants'],[{'origin':'base','row_index':0,'source':{'id':'source-a','url':'https://agency.test/guide','supports':'A'}}],'VARIANT_CLOSURE'),
 ('identity_id_rewrite',0,['groups',0,'identities',0,'id'],'source-b','SOURCE_ID_REASSIGNED'),
 ('source_support_rewrite',0,['groups',0,'variants',1,'source','supports'],'new scope','READING_SCOPE_CHANGED'),
 ('source_url_rewrite',0,['groups',0,'variants',1,'source','url'],'https://agency.test/else','READING_SCOPE_CHANGED'),
 ('source_id_rewrite',0,['groups',0,'variants',1,'source','id'],'source-a','READING_SCOPE_CHANGED'),
 ('identity_origin_rewrite',0,['groups',0,'identities',1,'origin'],'unowned','IDENTITY_CLOSURE'),
 ('variant_origin_rewrite',0,['groups',0,'variants',1,'origin'],'unowned','VARIANT_CLOSURE'),
 ('identity_index_rewrite',0,['groups',0,'identities',1,'row_index'],9,'IDENTITY_CLOSURE'),
 ('variant_index_rewrite',0,['groups',0,'variants',1,'row_index'],9,'VARIANT_CLOSURE'),
 ('identity_nonobject',0,['groups',0,'identities',0],None,'BAD_IDENTITY'),
 ('variant_nonobject',0,['groups',0,'variants',0],None,'BAD_VARIANT'),
 ('different_real_url',1,['food',0,'url'],'https://agency.test/other','COUNT_DRIFT:unique_source_urls'),
 ('different_query',1,['food',0,'url'],'https://agency.test/guide/?x=1','COUNT_DRIFT:duplicate_url_groups'),
 ('different_fragment',1,['food',0,'url'],'https://agency.test/guide/#x','COUNT_DRIFT:duplicate_url_groups'),
 ('different_host',1,['food',0,'url'],'https://fake.test/guide','COUNT_DRIFT:duplicate_url_groups'),
]

def build_case(name,target,path,value,required):
 def test(self):
  data=list(fixture());set_path(data[target],path,value)
  errors=g.verify(*data)
  self.assertTrue(any(item.startswith(required) for item in errors),(name,errors))
 return test
for name,target,path,value,required in CASES:
 setattr(Tests,'test_mutant_'+name,build_case(name,target,path,value,required))

if __name__=='__main__':unittest.main()
