import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r360',HERE/'r360_guardrail_evidence_chain_hold.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
NAME=next(iter(r.GATES))
BASE={'status':'REVIEW_REQUIRED_HARD_HOLD','may_publish':False,'may_merge':False,'qd_pass':False}

class GateChainTests(unittest.TestCase):
 def test_all_real_gates_pinned(self):
  self.assertEqual(10,len(r.GATES))
  self.assertTrue(all(len(v)==40 for v in r.GATES.values()))
 def test_good_child_never_approves(self):
  x=r.evaluate_child(NAME,2,json.dumps(BASE))
  self.assertEqual(x['admission'],'REVIEW_ONLY_HARD_HOLD')
 def test_native_missing_is_hold(self):
  with tempfile.TemporaryDirectory() as d:
   result=r.audit(Path(d))
   self.assertEqual(result['status'],'INVALID_HARD_HOLD')
   self.assertFalse(result['qd_pass'])
 def test_source_blob_and_drift(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x.py';p.write_text('pass\n')
   sha=r.git_blob(p.read_bytes())
   self.assertIsNone(r.verify_source(p,sha))
   self.assertEqual('CHILD_BLOB_DRIFT',r.verify_source(p,'0'*40))
 def test_symlink_source_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'a';p.write_text('x')
   q=Path(d)/'b';q.symlink_to(p)
   self.assertEqual('MISSING_UNSAFE_OR_OVERSIZE_CHILD',r.verify_source(q,r.git_blob(b'x')))
 def test_unknown_child_rejected(self):
  self.assertIn('UNREGISTERED_CHILD',r.evaluate_child('rogue.py',2,json.dumps(BASE))['errors'])
 def test_coverage_refuses_empty(self):
  self.assertIn('INCOMPLETE_GATE_COVERAGE',r.summarize([])['errors'])
 def test_coverage_accepts_all_review_only_but_never_qd(self):
  rows=[r.evaluate_child(name,2,json.dumps(BASE)) for name in r.GATES]
  d=r.summarize(rows)
  self.assertEqual('REVIEW_REQUIRED_HARD_HOLD',d['status'])
  self.assertFalse(d['may_publish'])
 def test_duplicate_gate_rejected(self):
  rows=[r.evaluate_child(name,2,json.dumps(BASE)) for name in r.GATES]
  rows[-1]=rows[0]
  self.assertIn('GATE_NAME_COVERAGE_MISMATCH',r.summarize(rows)['errors'])
 def test_invalid_child_invalidates_entire_chain(self):
  rows=[r.evaluate_child(name,2,json.dumps(BASE)) for name in r.GATES]
  rows[3]=r.evaluate_child(list(r.GATES)[3],0,json.dumps(BASE))
  self.assertEqual('INVALID_HARD_HOLD',r.summarize(rows)['status'])
 def test_missing_pin_invalidates_chain(self):
  rows=[r.evaluate_child(name,2,json.dumps(BASE)) for name in r.GATES]
  self.assertIn('UNAVAILABLE_OR_DRIFTED_SOURCE',r.summarize(rows,missing=['sha drift'])['errors'])

# Each scenario stays independent; these cases MUST reject or retain a hard hold.
BAD_STATUSES=['PASS','VERIFIED','LIVE','APPROVED','READY','DRAFT','SAFE','REVIEW_COMPLETE',
              'PUBLISH_READY','INVALID','HARD_HOLDLESS','safely_ok','RELEASED','OK']
BAD_JSON=['', '[]','null','3','"pass"','{}','{"status":"A","status":"REVIEW_REQUIRED_HARD_HOLD"}',
          '{bad json}', '{"status":123}', '{"status":null}',
          '{"status":"REVIEW_REQUIRED_HARD_HOLD","may_publish":true,"may_publish":false}']
BAD_EXIT=[-9,-1,0,1,3,4,5,10,124,127,255]
BAD_FLAG_VALUES=[True,None,'false','true',1,0,[],{},'approved']

def attach_test(kind, idx, value):
 def check(self):
  payload=dict(BASE)
  if kind=='status': payload['status']=value; doc=json.dumps(payload); code=2
  elif kind=='json':doc=value;code=2
  elif kind=='exit':doc=json.dumps(BASE);code=value
  elif kind=='flag':payload['qd_pass']=value;doc=json.dumps(payload);code=2
  result=r.evaluate_child(NAME,code,doc)
  self.assertEqual('INVALID_HARD_HOLD',result['admission'],repr(value))
 setattr(GateChainTests,f'test_{kind}_{idx:02d}',check)

for category,vals in [('status',BAD_STATUSES),('json',BAD_JSON),('exit',BAD_EXIT),('flag',BAD_FLAG_VALUES)]:
 for i,v in enumerate(vals):attach_test(category,i,v)

for flag in r.NO_APPROVAL:
 def check(self,flag=flag):
  payload=dict(BASE);payload[flag]=True
  x=r.evaluate_child(NAME,2,json.dumps(payload))
  self.assertIn('UNAUTHORIZED_APPROVAL:'+flag,x['errors'])
 setattr(GateChainTests,'test_refuse_claim_'+flag,check)

if __name__=='__main__':unittest.main()
