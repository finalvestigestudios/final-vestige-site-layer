"""R314 synthetic copy/state mutations (not a human safety determination)."""
import importlib.util, json, subprocess, sys, tempfile, unittest
from pathlib import Path
P=Path(__file__).resolve().parent.parent/'tools/r314_family_contact_release_hold.py'
s=importlib.util.spec_from_file_location('r314_gate',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
C='{{cite:shelter-fcc-comms}}'
A='<p class="pa-act-note">For immediate help call 911 if you can. '+C+'</p><p>{{link:family-reunification-card|card}}</p>'
T='<p class="pa-act-note">For immediate help call 911 if you can. '+C+'</p><noscript><div class="pa-foldcard">blank card</div></noscript>'
MA={'slug':'family-communication-plan','status':{'editorial':'drafted','publish':'draft'},'safety_review':{'state':'pending'},'source_use':{'shelter-fcc-comms':'source'}}
MT={**MA,'slug':'family-reunification-card'}
class Tests(unittest.TestCase):
 def chk(self,a=A,am=MA,t=T,tm=MT):return m.inspect(a,am,t,tm)
 def test_clean_is_still_hard_hold(self):self.assertEqual(self.chk()['state'],'COPY_REVIEW_HARD_HOLD')
 def test_never_claims_approval(self):
  v=self.chk();self.assertFalse(v['independent_qd_pass']);self.assertFalse(v['medical_safety_verified']);self.assertFalse(v['publication_authorized'])
 def test_no_paid_orders_from_citations(self):self.assertFalse(self.chk()['paid_order_verified'])
 def test_note_witness_is_reproducible(self):self.assertEqual(self.chk()['note_witnesses'],self.chk()['note_witnesses'])
 def test_note_witness_changes_with_copy(self):self.assertNotEqual(self.chk()['note_witnesses'],self.chk(a=A.replace('immediate','urgent'))['note_witnesses'])
 def test_no_checkout_rejected(self):
  with tempfile.TemporaryDirectory() as d:self.assertEqual(m.run(Path(d))['state'],'INVALID_HARD_HOLD')
 def test_cli_no_checkout_exits_failure(self):
  with tempfile.TemporaryDirectory() as d:
   r=subprocess.run([sys.executable,'-I',str(P),'--root',d],text=True,capture_output=True)
   self.assertEqual(r.returncode,1);self.assertEqual(json.loads(r.stdout)['state'],'INVALID_HARD_HOLD')
 def test_predecessor_oid(self):self.assertEqual(m.oid((P.parent/'r313_article_visible_citation_state_hold.py').read_bytes()),m.PRED[1])
 def test_five_original_source_pins(self):self.assertEqual(len(m.PINS),5)
 def test_comment_only_emergency_note_rejected(self):self.assertIn('ARTICLE_NOTE_STRUCTURE',self.chk(a='<!--'+A+'-->') ['errors'])
 def test_two_surfaces_independent(self):
  v=self.chk(a=A.replace('help','help now'),t=T.replace('help','help now'))
  self.assertEqual(len(v['note_witnesses']),2)
# 40 individually reported adversarial cases, plus 11 foundation checks.
CASES=[('ARTICLE_NARROW_911','a','For immediate help call 911 if you can.','call 911 for anything life-threatening'),
 ('TOOL_NARROW_911','t','For immediate help call 911 if you can.','call 911 for anything life-threatening'),
 ('ARTICLE_PRIVACY_UNVERIFIED','a','</p>',' keeps what you type on your own device.</p>'),
 ('ARTICLE_CHILD_COMPARISON_UNSOURCED','a','</p>',' A child is calmer than a child with another script.</p>'),
 ('TOOL_PRIVACY_UNVERIFIED','t','</p>',' What you type stays on this page. Closing the tab clears it.</p>'),
 ('ARTICLE_TOOL_LINK_MISSING','a','{{link:family-reunification-card|card}}','card'),
 ('TOOL_PRINT_FALLBACK_UNPROVEN','t','pa-foldcard','not-a-card'),
 ('ARTICLE_CITATION_PARITY','a',C,'{{cite:new-source}}'),
 ('TOOL_CITATION_PARITY','t',C,'{{cite:new-source}}')]
for i,(code,surface,old,new) in enumerate(CASES):
 for j in range(4):
  def test(self,code=code,surface=surface,old=old,new=new,j=j):
   base=A if surface=='a' else T
   transformed=base.replace(old,new,1)
   if j==1:transformed=transformed+'\n'
   elif j==2:transformed='<!-- independent review -->'+transformed
   elif j==3:transformed=transformed.replace('<p ', '<p data-review="pending" ',1)
   kw={surface:transformed}
   self.assertIn(code,self.chk(**kw)['errors'])
  setattr(Tests,f'test_mutation_{i:02}_{j}',test)
for i,state in enumerate(['approved','published','safe','PENDING']):
 def test(self,state=state):self.assertIn('ARTICLE_DRAFT_SAFETY_STATE',self.chk(am={**MA,'safety_review':{'state':state}})['errors'])
 setattr(Tests,f'test_reviewer_state_{i}',test)
if __name__=='__main__':unittest.main()
