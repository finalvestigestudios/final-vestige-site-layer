"""Synthetic unit tests; do not claim native authentic repository execution."""
import importlib.util
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools'/'r297_reunion_privacy_print_crosswalk_hold.py'
spec=importlib.util.spec_from_file_location('r297_hold',P)
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)

B='''<section><p>In an emergency, call 911 for anything life-threatening, and use text messages rather than calls for everything else when networks are busy.{{cite:shelter-ready-tech}} It is not sent or saved. Closing the tab clears it.</p></section>
@media print { .pa-card-mainhide { display: none !important; } }
<noscript><p>The form below still works and prints.</p></noscript>
<form class="pa-sheet pa-card-mainhide" id="rc"></form>
Minimal version: only the out-of-area contact, a phone number, the first meeting place and the review date
<noscript><style>#rc, #rc-warn { display: none; }</style></noscript>'''
J='''var front=keep([row("Household", c.hhName), row("Phone", c.hhPhone), row("Out-of-area contact", c.outName), row("Out-of-area phone", c.outPhone), row("Meet first at", c.meet1)]);
var back = minimal ? keep([row("Reviewed", c.reviewed)]) : keep([]);'''
M={'description':'Nothing is stored'}

class FixtureWitnesses(unittest.TestCase):
    def test_expected_witnesses(self):
        r=g.inspect_source(B,M,J)
        self.assertTrue(all(r['checks'].values()),r)
        self.assertEqual(len(r['claims']),4)
        self.assertTrue(all(r['issue_witnesses'].values()))
    def test_line_numbers(self):
        self.assertEqual(g.line_of('x\ny\nfoo','foo'),3)
        self.assertIsNone(g.line_of('x','q'))
    def test_empty_invalid(self):
        r=g.examine({})
        self.assertEqual(r['state'],'INVALID_HARD_HOLD')
        self.assertEqual(len(r['errors']),4)
        self.assertFalse(r['publication_authorized'])
    def test_changed_invalid(self):
        r=g.examine({p:b'abcd' for p in g.EXPECTED})
        self.assertEqual(len(r['errors']),4)
        self.assertTrue(all(x.startswith('CHANGED_WITNESS:') for x in r['errors']))
    def test_blob(self):
        self.assertEqual(g.blob_oid(b''),'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391')
    def test_no_release_path(self):
        r=g.examine({})
        for k in ('publication_authorized','independent_qd_pass','medical_safety_verified','privacy_approved','paid_offer_approved','revenue_verified'):
            self.assertIs(r[k],False)

# Independent single-factor mutations. All should remove a known evidence witness,
# not silently count a changed claim as reviewed or validated.
MUTATIONS={
 'nojs_promise':'The form below still works and prints.',
 'nojs_hide':'<noscript><style>#rc, #rc-warn { display: none; }</style></noscript>',
 'form_class':'pa-sheet pa-card-mainhide',
 'print_hide':'.pa-card-mainhide { display: none !important; }',
 'min_wording':'Minimal version: only the out-of-area contact, a phone number, the first meeting place and the review date',
 'privacy_claim':'It is not sent or saved. Closing the tab clears it.',
 'emergency_claim':'call 911 for anything life-threatening',
 'citation':'{{cite:shelter-ready-tech}}',
 'j_hhName':'row("Household", c.hhName)',
 'j_hhPhone':'row("Phone", c.hhPhone)',
 'j_outName':'row("Out-of-area contact", c.outName)',
 'j_outPhone':'row("Out-of-area phone", c.outPhone)',
 'j_meet1':'row("Meet first at", c.meet1)',
 'j_back':'var back = minimal ? keep(',
 'meta_privacy':'Nothing is stored',
}
for name,token in MUTATIONS.items():
    for substitute in ('REMOVED', '', 'not-a-match'):
        def test(self,n=name,t=token,s=substitute):
            body,meta,js=B,dict(M),J
            if n.startswith('j_'): js=js.replace(t,s)
            elif n=='meta_privacy':meta['description']=s
            else:body=body.replace(t,s)
            r=g.inspect_source(body,meta,js)
            self.assertFalse(all(r['issue_witnesses'].values()), (n,s,r['checks']))
        setattr(FixtureWitnesses,'test_mutation_'+name+'_'+str(len(substitute)),test)

if __name__=='__main__':unittest.main()
