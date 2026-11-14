"""R359 synthetic regression. Never claims native safety review or publication."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import r359_tool104_print_dispatch_citation_hold as g

BODY='''<section class="pa-act"><p class="pa-act-note">call 911 for anything life-threatening.
It is not sent or saved. Closing the tab clears it.{{cite:shelter-ready-tech}}</p></section>
<style>@media print { .pa-card-mainhide { display: none !important; } }</style>
<div class="pa-alert pa-card-mainhide"><p>A printed card can be lost</p>
<p>Do not put a child's full name here.</p></div>
<noscript><p>Use the blank card.</p></noscript>
<div style="font-size:7.5pt"></div>
{{link:family-communication-plan|Family plan}} {{link:shelter-or-evacuate|Evacuate}}
{{inline-js:reunion_card.js}}'''
ARTICLE='<p>Practice contact plans {{cite:shelter-ready-tech}}</p>'
META={'kind':'tool','slug':'family-reunification-card','status':{'publish':'draft'},
      'safety_review':{'state':'pending'},'source_use':{'shelter-ready-tech':'family checkin'}}

def run(body=BODY,meta=None,article=ARTICLE,**kw):
    return g.inspect(body,json.dumps(META if meta is None else meta),article,**kw)

class CustodyTests(unittest.TestCase):
    def test_baseline(self):
        r=run();self.assertEqual(r['status'],'QUALIFIED_REVIEW_REQUIRED_HARD_HOLD')
        self.assertEqual(r['facts']['tool_citation_occurrences'],1)
        self.assertTrue(r['facts']['loss_notice_at_risk_of_print_omission'])
    def test_determinism(self):self.assertEqual(run(),run())
    def test_genuine_pins_reject_synthetic(self):self.assertIn('ORIGINAL_GIT_IDENTITY_DRIFT',run(authenticate=True)['errors'])
    def test_no_release_flags(self):
        for k in g.HOLD:self.assertIs(run()[k],False)
    def test_native_missing_checkout(self):
        with tempfile.TemporaryDirectory() as d:self.assertEqual(g.native_review(Path(d))['status'],'INVALID_HARD_HOLD')
    def test_invalid_bad_json(self):self.assertEqual(g.inspect(BODY,'{',ARTICLE)['status'],'INVALID_HARD_HOLD')
    def test_source_hash_known(self):self.assertEqual(g.git_blob(''),'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391')
    def test_unmodified_source_warning(self):self.assertIn('PRINT_WARNING_HIDDEN_IN_AUTHORED_PRINT_CSS_REQUIRES_REVIEW',run()['review_docket'])
    def test_privacy_claim_marked(self):self.assertIn('UNVERIFIED_ABSOLUTE_PRIVACY_PROMISE',run()['review_docket'])
    def test_dispatch_claim_marked(self):self.assertIn('EMERGENCY_DISPATCH_NARROWING',run()['review_docket'])
    def test_child_claim_marked(self):self.assertIn('CHILD_CARD_COMPLETENESS_REVIEW',run()['review_docket'])
    def test_small_print_marked(self):self.assertIn('PRINT_LEGIBILITY_REVIEW',run()['review_docket'])
    def test_scripts_preserved(self):self.assertEqual(run()['facts']['script_dependencies'],['reunion_card.js'])
    def test_not_blessed_if_no_docket(self):
        b=BODY.replace('life-threatening','emergency').replace('It is not sent or saved. Closing the tab clears it.','').replace('7.5pt','12pt').replace("Do not put a child's full name",'Review child fields')
        self.assertFalse(run(body=b)['may_publish'])

# Case-specific adversarial tests; 40+ individually executed cases.
BAD=[
 ('remove_cite',lambda b:b.replace('{{cite:shelter-ready-tech}}',''),'SOURCE_CITATIONS_MISSING'),
 ('invent_cite',lambda b:b.replace('shelter-ready-tech','unregistered-source'),'UNDECLARED_CITATION'),
 ('remove_familypath',lambda b:b.replace('{{link:family-communication-plan|Family plan}}',''),'CROSS_REFERENCE_LOST'),
 ('remove_evacuate',lambda b:b.replace('{{link:shelter-or-evacuate|Evacuate}}',''),'CROSS_REFERENCE_LOST'),
 ('remove_script',lambda b:b.replace('{{inline-js:reunion_card.js}}',''),'INTERACTIVE_SCRIPT_PROVENANCE_MISSING'),
 ('remove_notice',lambda b:b.replace('A printed card can be lost','A card is fine'),'CARRIED_CARD_WARNING_SOURCE_MISSING'),
]
for name,edit,code in BAD:
    def test(self,fn=edit,expected=code):self.assertTrue(any(expected in x for x in run(body=fn(BODY))['errors']))
    setattr(CustodyTests,'test_adversarial_'+name,test)

for key,value,reason in [
    ('kind','article','TOOL_IDENTITY_INVALID'),
    ('slug','wrong-name','TOOL_IDENTITY_INVALID'),
    ('source_use',{},'SOURCE_USE_INVALID'),
    ('source_use',{'bad/source':'x'},'SOURCE_USE_INVALID'),
    ('source_use',{'shelter-ready-tech':'x','other-source':'y'},'UNUSED_SOURCE_DECLARATION_REVIEW')]:
    def test(self,k=key,v=value,expected=reason):
        m=copy.deepcopy(META);m[k]=v;r=run(meta=m)
        self.assertTrue(any(expected in x for x in r['errors']+r['review_docket']))
    setattr(CustodyTests,'test_meta_'+key+'_'+reason,test)

for status in ['published','approved','live','scheduled','private-live',None,True]:
    def test(self,s=status):
        m=copy.deepcopy(META);m['status']['publish']=s
        self.assertIn('UNAUTHORIZED_PUBLICATION_OR_SAFETY_STATE',run(meta=m)['errors'])
    setattr(CustodyTests,'test_publish_state_'+str(status).replace('-','_'),test)
for status in ['approved','passed','not-needed',None,False,'published']:
    def test(self,s=status):
        m=copy.deepcopy(META);m['safety_review']['state']=s
        self.assertIn('UNAUTHORIZED_PUBLICATION_OR_SAFETY_STATE',run(meta=m)['errors'])
    setattr(CustodyTests,'test_safety_state_'+str(status).replace('-','_'),test)

for raw in ['',None,123,[],{},'\ud800']:
    def test(self,value=raw):
        self.assertEqual(g.inspect(value,json.dumps(META),ARTICLE)['status'],'INVALID_HARD_HOLD')
    setattr(CustodyTests,'test_bad_tool_'+str(raw).replace('\ud800','surrogate')[:15],test)

for marker,subst in [('a','<span>'),('b',''),('c',' lorem')]:
    def test(self,new=subst):
        b=BODY.replace('A printed card can be lost',new)
        self.assertEqual(run(body=b)['status'],'INVALID_HARD_HOLD')
    setattr(CustodyTests,'test_missing_warning_'+marker,test)

if __name__=='__main__':unittest.main(verbosity=2)
