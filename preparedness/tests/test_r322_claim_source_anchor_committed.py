"""R322 exact-committed synthetic regressions; no authentic source writes."""
import copy
import json
import unittest
from preparedness.tests.test_r321_conflict_content_delta_hold import synthetic
from preparedness.tools import r322_claim_source_anchor_hold as gate


def inventory(s): return gate.claim_inventory(s.encode('utf-8'))
def compare(a,b): return gate.compare_claims(a.encode('utf-8'),b.encode('utf-8'))


class R322CommittedTests(unittest.TestCase):
    def setUp(self): self.m,self.d,self.blobs=synthetic()
    def report(self):return gate.build_report(self.m,self.d,self.blobs.__getitem__)
    def test_35_article_six_tool_docket_hold(self):self.assertEqual(self.report()['source_docket_conflicts_held'],15)
    def test_six_conflicted_bodies(self):self.assertEqual(self.report()['body_conflicts_audited'],6)
    def test_qualified_approval_false(self):self.assertTrue(all(x['qualified_review'] is False for x in self.report()['rows']))
    def test_state_still_hold(self):self.assertEqual(self.report()['state'],'DRAFT_HARD_HOLD')
    def test_no_public_release(self):self.assertIs(self.report()['release']['publication_authorized'],False)
    def test_no_claim_of_qd(self):self.assertIs(self.report()['release']['independent_qd_pass'],False)
    def test_no_paid_sales(self):self.assertIs(self.report()['release']['paid_conversion_verified'],False)
    def test_no_auto_merge(self):self.assertIs(self.report()['release']['automatic_merge_permitted'],False)
    def test_read_only_docket(self):
        old=copy.deepcopy(self.d);self.report();self.assertEqual(self.d,old)
    def test_read_only_manifest(self):
        old=copy.deepcopy(self.m);self.report();self.assertEqual(self.m,old)
    def test_deterministic(self):self.assertEqual(self.report(),self.report())
    def test_source_mismatch_fail_closed(self):
        self.blobs.clear();self.assertEqual(self.report()['state'],'INVALID_HARD_HOLD')
    def test_invalid_approval_fail_closed(self):
        self.d['release']['independent_qd_pass']=True
        self.assertEqual(self.report()['state'],'INVALID_HARD_HOLD')
    def test_no_raw_pii_in_output(self):
        self.assertNotIn('local bulletin',json.dumps(self.report()))
    def test_actual_citation_syntax(self):
        self.assertEqual(inventory('<li><strong>Contact.</strong> Text them.{{cite:shelter-fcc-comms}}</li>')['visible_citation_ids'],['shelter-fcc-comms'])
    def test_anchors_detect_same_count_reassignment(self):
        a='<p>Do not enter {{cite:fire-source}}</p><p>Phone first {{cite:comms-source}}</p>'
        b='<p>Do not enter {{cite:comms-source}}</p><p>Phone first {{cite:fire-source}}</p>'
        d=compare(a,b)
        self.assertEqual(d['before_visible_citations'],d['after_visible_citations'])
        self.assertEqual(len(d['removed_claim_source_anchors']),2)
    def test_lost_warning_cue(self):
        self.assertIn('never',compare('<p>Never put generator indoors {{cite:source-a}}</p>','<p>Put it indoors {{cite:source-a}}</p>')['warning_cue_decreases'])
    def test_nul_rejected(self):
        with self.assertRaises(ValueError):gate.claim_inventory(b'<p>\x00</p>')
    def test_invalid_utf8_rejected(self):
        with self.assertRaises(UnicodeDecodeError):gate.claim_inventory(b'\xff')
    def test_missing_source_use_is_not_pass(self):
        self.assertEqual(gate.source_use_audit(b'<p>Act {{cite:source-a}}</p>',b'{}')['state'],'SOURCE_USE_UNAVAILABLE_HOLD')
    def test_published_metadata_not_safe(self):
        a=b'{"source_use":{"source-a":"note"},"status":{"publish":"published"}}'
        self.assertTrue(gate.source_use_audit(b'<p>Act {{cite:source-a}}</p>',a)['unsafe_release_state'])
    def test_duplicate_source_use_key_rejected(self):
        with self.assertRaises(ValueError):gate.source_use_audit(b'<p>Act</p>',b'{"source_use":{},"source_use":{}}')
    def test_source_set_not_claim_of_safety(self):
        a=b'{"source_use":{"source-a":"note"},"status":{"publish":"draft"}}'
        self.assertIs(gate.source_use_audit(b'<p>Act {{cite:source-a}}</p>',a)['qualified_approval'],False)


def hidden_case(name, html):
    def t(self):self.assertIn('source-a',inventory(html)['hidden_citation_ids'])
    t.__name__='test_hidden_'+name
    return t

for name,html in {
    'comment':'<!-- {{cite:source-a}} -->',
    'script':'<script>{{cite:source-a}}</script>',
    'style':'<style>{{cite:source-a}}</style>',
    'template':'<template><p>Read {{cite:source-a}}</p></template>',
    'noscript':'<noscript><p>Read {{cite:source-a}}</p></noscript>',
    'attribute':'<p title="{{cite:source-a}}">Read</p>',
    'hidden':'<div hidden><p>Read {{cite:source-a}}</p></div>',
    'aria':'<div aria-hidden="true"><p>Read {{cite:source-a}}</p></div>',
    'display':'<div style="display:none"><p>Read {{cite:source-a}}</p></div>',
    'visibility':'<div style="visibility:hidden"><p>Read {{cite:source-a}}</p></div>',
    'opacity':'<div style="opacity:0"><p>Read {{cite:source-a}}</p></div>',
    'input':'<input value="{{cite:source-a}}">',
}.items():setattr(R322CommittedTests,'test_hidden_'+name,hidden_case(name,html))


def variant_mutation(i,method):
    def t(self):
        r=self.d['records'][i];obj=r['source_refs']['integrated']
        if method=='hash':obj['sha']='0'*40
        elif method=='size':obj['size']+=1
        elif method=='missing':self.blobs.pop(obj['sha'],None)
        else:self.blobs[obj['sha']]=b'synthetic-bad-byte-content'
        self.assertEqual(self.report()['state'],'INVALID_HARD_HOLD')
    return t

for idx in range(15):
    for method in ('hash','size','missing','tampered'):
        setattr(R322CommittedTests,f'test_pinned_{idx:02}_{method}',variant_mutation(idx,method))

if __name__=='__main__':unittest.main()
