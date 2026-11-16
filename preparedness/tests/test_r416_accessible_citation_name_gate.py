"""R416 35-article synthetic citation accessible-name anti-spoof regression suite."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'tests'))
from test_r415_global_citation_alignment_gate import fixture, ANCHOR
import r415_global_citation_alignment_gate as previous
import r416_accessible_citation_name_gate as gate


def inject(d,m,e,c,attribute):
    html=e['guide-0'][0].replace(ANCHOR,ANCHOR.replace(' href=', ' '+attribute+' href='))
    assert html!=e['guide-0'][0], 'test did not inject attribute'
    e['guide-0']=(html,html)


def run_case(attribute):
    d,m,e,c=fixture();inject(d,m,e,c,attribute)
    return previous.check(d,m,e,c,test_only=True),gate.check(d,m,e,c,test_only=True)


class Positive(unittest.TestCase):
    def test_35_artifact_fixture_integrity_only(self):
        d,m,e,c=fixture();r=gate.check(d,m,e,c,test_only=True)
        self.assertTrue(r['integrity_ok'],r['errors'])
        self.assertEqual(r['articles_inspected'],35)
        self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
        self.assertFalse(r['eligible']);self.assertFalse(r['publication_approved']);self.assertFalse(r['qualified_safety_approved'])
    def test_reader_visible_name_same_as_aria(self):
        _,r=run_case('aria-label="Original source"')
        self.assertTrue(r['integrity_ok'],r['errors'])
    def test_reader_visible_name_spaces_and_case(self):
        _,r=run_case('aria-label="  ORIGINAL   SOURCE  "')
        self.assertTrue(r['integrity_ok'],r['errors'])
    def test_consistent_title(self):
        _,r=run_case('title="Original source"')
        self.assertTrue(r['integrity_ok'],r['errors'])
    def test_role_link(self):
        _,r=run_case('role="link"')
        self.assertTrue(r['integrity_ok'],r['errors'])
    def test_tabindex_zero(self):
        _,r=run_case('tabindex="0"')
        self.assertTrue(r['integrity_ok'],r['errors'])
    def test_blank_target_with_isolation(self):
        _,r=run_case('target="_blank" rel="noopener noreferrer"')
        self.assertTrue(r['integrity_ok'],r['errors'])
    def test_self_target(self):
        _,r=run_case('target="_self"')
        self.assertTrue(r['integrity_ok'],r['errors'])
    def test_explicit_no_referrer(self):
        _,r=run_case('referrerpolicy="no-referrer"')
        self.assertTrue(r['integrity_ok'],r['errors'])
    def test_no_private_manuscript_excerpts_in_report(self):
        d,m,e,c=fixture();r=json.dumps(gate.check(d,m,e,c,test_only=True))
        self.assertNotIn('A museum ledger records',r)
    def test_inputs_unchanged(self):
        d,m,e,c=fixture();old=copy.deepcopy((d,m,e,c));gate.check(d,m,e,c,test_only=True)
        self.assertEqual((d,m,e,c),old)
    def test_missing_private_files_exit_two(self):
        p=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r416_accessible_citation_name_gate.py'),
                         '/missing/a','/missing/b','/missing/c','/missing/d'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertEqual(json.loads(p.stdout)['release_state'],'DRAFT_HARD_HOLD')
    def test_wordpress_preview_different_aria_detected(self):
        d,m,e,c=fixture();wp,pv=e['guide-0']; e['guide-0']=(wp.replace(ANCHOR,ANCHOR.replace(' href=',' aria-label="SPOOFED" href=')),pv)
        r=gate.check(d,m,e,c,test_only=True)
        self.assertFalse(r['integrity_ok'])
    def test_prev_allows_aria_spoof_new_blocks(self):
        old,new=run_case('aria-label="Federal agency certifies this as safe"')
        self.assertTrue(old['integrity_ok'],old['errors'])
        self.assertFalse(new['integrity_ok'])
        self.assertTrue(any('aria-label overrides' in v for v in new['errors']))


ATTACKS = [
('fake_aria_certification','aria-label="Federal agency approves this preparation"'),
('fake_aria_emergency','aria-label="Call this private hotline for medical care"'),
('fake_aria_payment','aria-label="Buy our certified safety kit"'),
('empty_aria','aria-label=""'),
('whitespace_aria','aria-label="   "'),
('aria_label_source_change','aria-label="Different government source"'),
('aria_label_trademark','aria-label="Trademark approved"'),
('aria_label_long','aria-label="Original source with verified medical advice"'),
('aria_label_extra_word','aria-label="Original source certified"'),
('aria_label_Unicode','aria-label="Origínal source"'),
('aria_label_nbsp','aria-label="Original source reviewed"'),
('aria_label_missing_prefix','aria-label="source"'),
('aria_label_random','aria-label="Fake journal citation"'),
('aria_label_lookalike','aria-label="Original sourcе"'),
('aria_label_news','aria-label="Breaking news approved"'),
('aria_label_prep','aria-label="Official warning cancelled"'),
('aria_label_redirect','aria-label="Continue to checkout"'),
('aria_label_alternative','aria-label="Trusted alternative agency"'),
('aria_label_reassurance','aria-label="No need to evacuate"'),
('aria_label_disclaimer','aria-label="This food is safe"'),
('aria_label_unknown','aria-label="Unnamed source"'),
('aria_label_short','aria-label="Orig"'),
('aria_label_ellipsis','aria-label="Original source ..."'),
('aria_label_parenthetical','aria-label="Original source (safe)"'),
('aria_label_topic_swap','aria-label="Article from a different study"'),
('aria_label_missing_data','aria-label="Publication date and safety approval"'),
('aria_label_refund','aria-label="Non-refundable safety pack"'),
('title_bad','title="Other journal claims proven"'),
('title_blank','title=""'),
('title_short','title="Source"'),
('aria_labelledby_fake','aria-labelledby="fake-label"'),
('aria_labelledby_empty','aria-labelledby=""'),
('aria_labelledby_group','aria-labelledby="heading safety seal"'),
('aria_describedby_fake','aria-describedby="external-safety-note"'),
('aria_describedby_group','aria-describedby="ad-checkout"'),
('role_button','role="button"'),
('role_none','role="none"'),
('role_presentation','role="presentation"'),
('role_blank','role=""'),
('role_citation','role="citation"'),
('tabindex_negative_four','tabindex="-4"'),
('tabindex_one','tabindex="1"'),
('tabindex_two','tabindex="2"'),
('tabindex_non_numeric','tabindex="keyboard"'),
('target_new_context','target="affiliate_buy_window"'),
('target_parent','target="_parent"'),
('target_top','target="_top"'),
('target_named','target="purchase-popup"'),
('rel_missing_noreferrer','target="_blank" rel="noopener"'),
('rel_missing_noopener','target="_blank" rel="noreferrer"'),
('rel_missing_both','target="_blank"'),
('aria_current_page','aria-current="page"'),
('aria_current_true','aria-current="true"'),
('contenteditable_true','contenteditable="true"'),
('contenteditable_blank','contenteditable=""'),
('draggable_true','draggable="true"'),
('referrerpolicy_unsafe','referrerpolicy="unsafe-url"'),
('referrerpolicy_origin_when','referrerpolicy="origin-when-cross-origin"'),
('referrerpolicy_no_referrer_when','referrerpolicy="no-referrer-when-downgrade"'),
('duplicate_aria','aria-label="Original source" aria-label="Other"'),
]

class Spoofs(unittest.TestCase):pass
for index,(name,attribute) in enumerate(ATTACKS):
    def make_test(a=attribute, n=name):
        def run(self):
            prev,new=run_case(a)
            self.assertFalse(new['integrity_ok'],(n,new['errors']))
            self.assertFalse(new['eligible']);self.assertFalse(new['publication_approved'])
            self.assertEqual(new['release_state'],'DRAFT_HARD_HOLD')
        return run
    setattr(Spoofs,'test_spoof_'+name,make_test())

if __name__=='__main__':unittest.main()
