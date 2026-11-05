"""R154 synthetic regression suite; passing is never a source/safety approval."""
import copy, importlib.util, unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('r154',Path(__file__).resolve().parents[1]/'tools/r154_review_triage_gate.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def fixture():
 t=[];resolved={('home-fire-escape-worksheet',0),('kit-builder',0),('kit-builder',1),('kit-builder',2),('power-outage-planner',0),('reunification-plan',0)}
 shadow={('home-fire-escape-worksheet',0),('kit-builder',1),('power-outage-planner',0),('reunification-plan',0)}
 for tool,count in m.EXPECTED_TOOL_ROWS.items():
  for i in range(count):
   t.append(dict(type='tool_source_scope',tool=tool,source_id=f's{i}',citations=1,url='https://example.org/s',publisher='Fixture',supports='Synthetic scope',author_specific_use='Synthetic usage',currently_resolvable=tool=='water-planner' or (tool,i) in resolved,interpretation_changed_by_shadow_origin=(tool,i) in shadow,review='PENDING',qualified_reviewer=None,review_fingerprint=f'{len(t)+1:064x}'))
 t[0]['citations']+=106
 h=[dict(type='historic_food_citation',article='pemmican-and-dried-meats' if i<7 else 'pioneer-travel-rations',occurrence=i+1 if i<7 else 1,line=i+1,excerpt='Synthetic context',review='PENDING',qualified_reviewer=None,review_fingerprint=f'{i+68:064x}') for i in range(8)]
 return dict(schema='fv-preparedness-r153-review-interlock-v1',decision='DRAFT_HARD_HOLD',release_authorized=False,qualified_source_review=False,medical_safety_approved=False,independent_qd_pass=False,genuine_paid_preparedness_sku_verified=False,review_tasks_total=75,tool_source_relationships=67,tool_citation_occurrences=173,tool_unresolved=58,source_interpretation_changes=4,historical_food_substitutions=8,tool_review_tasks=t,historic_food_review_tasks=h,packet_fingerprint='f'*64)

def notes(p):
 return dict(schema=m.NOTES_SCHEMA,base_packet_fingerprint=p['packet_fingerprint'],notes=[dict(task_fingerprint=p['tool_review_tasks'][0]['review_fingerprint'],disposition='QUESTION',note='Please check this source.',evidence_urls=['https://www.cdc.gov/test'])])

class Checks(unittest.TestCase):
 def test_queue(self):
  x=m.triage(fixture());self.assertEqual((x['review_tasks_total'],x['priority_hist_food'],x['priority_reunification'],x['priority_interpretation'],x['remaining_tool_source']),(75,8,11,4,52))
 def test_all_holds(self):
  x=m.triage(fixture());self.assertTrue(all(not x[k] for k in ('independent_qd_pass','qualified_source_review','safety_approved','publication_authorized','merchant_offer_verified')))
 def test_notes_hold(self):
  p=fixture();x=m.triage(p,notes(p));self.assertEqual(x['notes_count'],1);self.assertTrue(all(not r['publication_allowed'] for r in x['tasks']))
 def test_immutable_deterministic(self):
  p=fixture();b=copy.deepcopy(p);self.assertEqual(m.triage(p),m.triage(b));self.assertEqual(p,b)
 def test_each_tool_fake_review(self):
  for i in range(67):
   with self.subTest(i=i):
    p=fixture();p['tool_review_tasks'][i]['review']='APPROVED'
    with self.assertRaises(ValueError):m.triage(p)
 def test_each_historic_context_loss(self):
  for i in range(8):
   with self.subTest(i=i):
    p=fixture();p['historic_food_review_tasks'][i]['excerpt']=''
    with self.assertRaises(ValueError):m.triage(p)
 def test_git_blob(self):self.assertEqual(m.git_blob(b'hi'),'32f95c0d1244a78b2be1bab8de17906fabb2c4a8')
 def test_safe_urls(self):
  self.assertTrue(m.safe_evidence_url('https://www.cdc.gov/test'))
  for u in ('http://www.cdc.gov/','https://localhost/','https://127.0.0.1/','https://user:pw@www.cdc.gov/','javascript:alert(1)'):
   with self.subTest(u=u):self.assertFalse(m.safe_evidence_url(u))

# Each mutation is a separately named test; source data is always synthetic.
MUTATIONS=[
 ('schema','bad'),('release_authorized',True),('qualified_source_review',True),('medical_safety_approved',True),('independent_qd_pass',True),('genuine_paid_preparedness_sku_verified',True),('review_tasks_total',76),('tool_source_relationships',66),('tool_citation_occurrences',172),('tool_unresolved',57),('source_interpretation_changes',3),('historical_food_substitutions',7),('packet_fingerprint','bad')]
for k,v in MUTATIONS:
 def make(key,value):
  def test(self):
   p=fixture();p[key]=value
   with self.assertRaises(ValueError):m.triage(p)
  return test
 setattr(Checks,'test_top_'+k,make(k,v))
for k,v in [('review','APPROVED'),('qualified_reviewer','fake'),('tool','unknown'),('source_id',''),('citations',0),('url','http://invalid'),('publisher',''),('supports',''),('author_specific_use',''),('currently_resolvable','yes'),('interpretation_changed_by_shadow_origin','yes'),('review_fingerprint','bad')]:
 def make(key,value):
  def test(self):
   p=fixture();p['tool_review_tasks'][0][key]=value
   with self.assertRaises(ValueError):m.triage(p)
  return test
 setattr(Checks,'test_source_'+k,make(k,v))
for k,v in [('schema','fake'),('base_packet_fingerprint','0'*64)]:
 def make(key,value):
  def test(self):
   p=fixture();n=notes(p);n[key]=value
   with self.assertRaises(ValueError):m.triage(p,n)
  return test
 setattr(Checks,'test_notes_'+k,make(k,v))
for k,v in [('disposition','APPROVED'),('note','<script>x</script>'),('evidence_urls',['javascript:alert(1)']),('task_fingerprint','0'*64),('medical_safety_approved',True)]:
 def make(key,value):
  def test(self):
   p=fixture();n=notes(p);n['notes'][0][key]=value
   with self.assertRaises(ValueError):m.triage(p,n)
  return test
 setattr(Checks,'test_note_item_'+k,make(k,v))
if __name__=='__main__':unittest.main()
