"""R356: synthetic evidence tests, never release/child-safety certification."""
from __future__ import annotations
import copy
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import r356_noscript_contract_hold as g

B='''<p>It is not sent or saved. Closing the tab clears it. {{cite:one}}</p>
<noscript><p>A blank fold-over card is shown below. The form below still works and prints.
Only the automatic reminders and the text download need JavaScript.</p></noscript>
<form id="rc" class="pa-sheet"><input id="rc-contact"/></form>
<noscript><div class="pa-printsheet"><div class="pa-foldcard">blank</div></div>
<style>#rc, #rc-warn { display: none; }</style></noscript>
<style>@media print { .pa-foldcard .pa-face { font-size: 7.5pt; } }</style>
<script>{{inline-js:shelter_common.js}}{{inline-js:reunion_card.js}}</script>'''
M={'slug':'family-reunification-card','kind':'tool','status':{'publish':'draft'},
   'safety_review':{'state':'pending'},'source_use':{'one':'citation declaration'}}
def run(b=B,m=None): return g.review(b,copy.deepcopy(M if m is None else m))

class TestContract(unittest.TestCase):
    def test_baseline_status(self):self.assertEqual(run()['status'],'REVIEW_REQUIRED_HARD_HOLD')
    def test_form_contradiction(self):self.assertIn('NOSCRIPT_FORM_HIDDEN_CONTRADICTS_COPY',run()['issues'])
    def test_download_not_evidenced(self):self.assertIn('TEXT_DOWNLOAD_UI_NOT_EVIDENCED',run()['issues'])
    def test_paper_branch_present(self):self.assertTrue(run()['blank_print_card_present_in_source'])
    def test_source_print_legibility_hold(self):self.assertIn('ORIGINAL_7_5PT_PRINT_REQUIRES_HUMAN_LEGIBILITY_TEST',run()['issues'])
    def test_privacy_promise_hold(self):self.assertIn('NO_SEND_NO_SAVE_PRIVACY_PROMISE_UNVERIFIED',run()['issues'])
    def test_tab_close_hold(self):self.assertIn('TAB_CLOSE_PRIVACY_PROMISE_UNVERIFIED',run()['issues'])
    def test_source_hash(self):self.assertEqual(len(run()['body_sha256']),64)
    def test_no_form_data_export(self):self.assertFalse(run()['private_form_values_exported'])
    def test_nojs_claim_flag(self):self.assertTrue(run()['form_function_claim'])
    def test_download_claim_flag(self):self.assertTrue(run()['text_download_claim'])
    def test_form_hidden_flag(self):self.assertTrue(run()['form_hidden_by_noscript_css'])
    def test_missing_form(self):self.assertEqual(run(B.replace('id="rc"','id="absent"'))['status'],'INVALID_HARD_HOLD')
    def test_no_form_claim(self):self.assertNotIn('NOSCRIPT_FORM_HIDDEN_CONTRADICTS_COPY',run(B.replace('The form below still works','A blank card'))['issues'])
    def test_unhidden_form_unverified(self):self.assertIn('NOSCRIPT_FORM_BEHAVIOR_UNVERIFIED',run(B.replace('#rc, #rc-warn','#other'))['issues'])
    def test_text_control_not_a_pass(self):self.assertIn('TEXT_DOWNLOAD_RUNTIME_UNVERIFIED',run(B+'<button id="rc-export">Export</button>')['issues'])
    def test_no_paper_branch(self):self.assertIn('BLANK_PRINT_CARD_NOT_EVIDENCED',run(B.replace('pa-printsheet','missing'))['issues'])
    def test_source_not_registered(self):self.assertIn('CITATION_DECLARATIONS_INCOMPLETE',run(B+'{{cite:unknown}}')['issues'])
    def test_missing_js_dependency(self):self.assertIn('EMBEDDED_JS_DEPENDENCIES_DRIFT',run(B.replace('reunion_card.js','other.js'))['issues'])
    def test_published_state_rejected(self):
        m=copy.deepcopy(M);m['status']['publish']='published';self.assertEqual(run(m=m)['status'],'INVALID_HARD_HOLD')
    def test_fake_qd_rejected(self):
        m=copy.deepcopy(M);m['safety_review']['state']='passed';self.assertEqual(run(m=m)['status'],'INVALID_HARD_HOLD')
    def test_non_tool_rejected(self):
        m=copy.deepcopy(M);m['kind']='article';self.assertEqual(run(m=m)['status'],'INVALID_HARD_HOLD')
    def test_non_original_slug_rejected(self):
        m=copy.deepcopy(M);m['slug']='different';self.assertEqual(run(m=m)['status'],'INVALID_HARD_HOLD')
    def test_non_dict_rejected(self):self.assertEqual(g.review(B,[])['status'],'INVALID_HARD_HOLD')
    def test_none_body_rejected(self):self.assertEqual(g.review(None,M)['status'],'INVALID_HARD_HOLD')
    def test_no_noscript_rejected(self):self.assertIn('NOSCRIPT_FALLBACK_MISSING',run(B.replace('<noscript>','<div>').replace('</noscript>','</div>'))['issues'])
    def test_absent_checkout_rejected(self):
        with tempfile.TemporaryDirectory() as p:self.assertEqual(g.native_review(p)['status'],'INVALID_HARD_HOLD')
    def test_fake_checkout_rejected(self):
        with tempfile.TemporaryDirectory() as p:
            (Path(p)/'.git').mkdir(); self.assertEqual(g.native_review(p)['status'],'INVALID_HARD_HOLD')
    def test_visible_text_ignores_styles(self):self.assertEqual(g.visible_text('<p>A</p><style>.a{display:none}</style>'),'A')
    def test_no_synthetic_approval(self):
        for f in ('may_merge','may_publish','qualified_qd_pass','browser_network_safety_verified','print_accessibility_verified','no_js_function_verified','may_activate_paid_cta'):
            self.assertFalse(run()[f])

CASES={
 'direct_id':('#rc{display:none}',True),'form_id':('form#rc{display:none}',True),
 'class':('.pa-sheet{display:none}',True),'comma':('#other,#rc{display:none}',True),
 'important':('#rc{display:none!important}',True),'other':('#other{display:none}',False),
 'visible':('#rc{display:block}',False),'opacity':('#rc{opacity:0}',False),
 'visibility':('#rc{visibility:hidden}',False),'random':('.random{display:none}',False),
}
for name,(css,expected) in CASES.items():
    def make(value,want):
        def f(self):self.assertEqual(g.hides_form(['<style>'+value+'</style>'],'<form id="rc" class="pa-sheet">'),want)
        return f
    setattr(TestContract,'test_css_'+name,make(css,expected))

MUTATIONS={
 'remove_print':('pa-printsheet','not-card','BLANK_PRINT_CARD_NOT_EVIDENCED'),
 'remove_fold':('pa-foldcard','not-fold','BLANK_PRINT_CARD_NOT_EVIDENCED'),
 'remove_helper':('shelter_common.js','unknown.js','EMBEDDED_JS_DEPENDENCIES_DRIFT'),
 'remove_model':('reunion_card.js','unknown.js','EMBEDDED_JS_DEPENDENCIES_DRIFT'),
 'remove_form':('id="rc"','id="other"','FORM_ID_MISSING'),
 'unknown_cite':('{{cite:one}}','{{cite:unregistered}}','CITATION_DECLARATIONS_INCOMPLETE'),
 'wording_change':('The form below still works','A blank card is available',''),
 'privacy_change':('It is not sent or saved','Verify local privacy',''),
 'nojs_download_change':('the text download','some separate features',''),
 'tab_claim_change':('Closing the tab clears it','Avoid sensitive inputs',''),
 'font_change':('font-size: 7.5pt','font-size: 10pt',''),
 'blank_change':('pa-printsheet','not-a-print-sheet','BLANK_PRINT_CARD_NOT_EVIDENCED'),
}
for name,(old,new,expected) in MUTATIONS.items():
    def make(a,b,want):
        def f(self):
            r=run(B.replace(a,b))
            if want:self.assertIn(want,r['issues'])
            self.assertFalse(r['may_publish']);self.assertFalse(r['qualified_qd_pass'])
        return f
    setattr(TestContract,'test_mutation_'+name,make(old,new,expected))

if __name__=='__main__':unittest.main()
