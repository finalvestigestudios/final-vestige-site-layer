"""R431 isolated synthetic custody tests; not proof of authentic authorship or advice safety."""
from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_r430_conflict_adjudication_escrow import fixture

SCRIPT = Path(__file__).resolve().parents[1] / 'tools' / 'r431_fork_content_delta_gate.py'
spec = importlib.util.spec_from_file_location('r431_fork_content_delta_gate', SCRIPT)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def materials(root, mutate=None):
    d = fixture()
    blobs = {}
    for i, row in enumerate(d['original_fork_disputes']):
        for j, v in enumerate(row['variants']):
            if row['path'].endswith('.body.html'):
                payload = ('<main><h2>Original heading %d</h2><p>Detailed original passage %s {{cite:s-1}} <a href="https://example.org/%s">Agency link</a></p></main>'
                           % (i, 'a lot ' * (5+j), j)).encode()
            else:
                payload = json.dumps({'path':row['path'],'revision':j,'sources':[{'id':'s-'+str(i)}]},sort_keys=True).encode()
            if mutate:
                payload = mutate(i, j, row['path'], payload)
            sha = g.r430.git_blob(payload)
            v['git_blob_sha'], v['byte_length'] = sha, len(payload)
            blobs[sha] = payload
    for sha, raw in blobs.items():
        (root / (sha+'.blob')).write_bytes(raw)
    return d, blobs


def check(d, root):
    return g.audit(d, root, raw_docket=json.dumps(d, sort_keys=True).encode(), test_only=True)


class Baseline(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.d, self.blobs = materials(self.root)

    def test_all_nine_forks(self):
        r = check(self.d,self.root)
        self.assertTrue(r['all_original_fork_bytes_verified'],r['errors'])
        self.assertEqual(len(r['fork_reviews']),9)
        self.assertEqual(sum(x['verified_candidate_count'] for x in r['fork_reviews']),18)

    def test_hard_hold_even_when_structurally_complete(self):
        r = check(self.d,self.root)
        for k in ('eligible','publication_approved','qualified_safety_approved','merchant_offer_verified','paid_activation_approved'):
            self.assertIs(r[k],False)
        self.assertIsNone(r['verified_orders'])
        self.assertIsNone(r['net_revenue_per_1000_qualified_human_sessions'])
        self.assertEqual(r['native_35_article_build_and_70_export_parity'],'NOT_TESTED_BY_R431')

    def test_human_selection_always_none(self):
        r=check(self.d,self.root)
        self.assertTrue(all(c['selection'] is None for c in r['fork_reviews']))
        self.assertTrue(all(v['human_selected'] is False for c in r['fork_reviews'] for v in c['candidates']))

    def test_deterministic_receipt(self):
        a=check(self.d,self.root)['review_receipt_sha256']
        b=check(self.d,self.root)['review_receipt_sha256']
        self.assertEqual(a,b)
        self.assertEqual(len(a),64)

    def test_case_order_does_not_change_receipt(self):
        a=check(self.d,self.root)['review_receipt_sha256']
        self.d['original_fork_disputes'].reverse()
        self.assertEqual(a,check(self.d,self.root)['review_receipt_sha256'])

    def test_candidate_order_does_not_change_receipt(self):
        a=check(self.d,self.root)['review_receipt_sha256']
        self.d['original_fork_disputes'][0]['variants'].reverse()
        self.assertEqual(a,check(self.d,self.root)['review_receipt_sha256'])

    def test_missing_docket_pin_fails(self):
        r=g.audit(self.d,self.root,raw_docket=json.dumps(self.d).encode())
        self.assertIn('R431_R430_ESCROW_FAILED',r['errors'])

    def test_missing_candidate_bytes_hard_hold(self):
        self.root.joinpath(next(iter(self.blobs))+'.blob').unlink()
        r=check(self.d,self.root)
        self.assertFalse(r['all_original_fork_bytes_verified'])
        self.assertIsNone(r['review_receipt_sha256'])

    def test_truncated_bytes(self):
        key=next(iter(self.blobs))
        self.root.joinpath(key+'.blob').write_bytes(self.blobs[key][:3])
        self.assertTrue(check(self.d,self.root)['errors'])

    def test_mutated_same_length_bytes(self):
        key=next(iter(self.blobs))
        self.root.joinpath(key+'.blob').write_bytes(b'x'*len(self.blobs[key]))
        self.assertTrue(check(self.d,self.root)['errors'])

    def test_symlink_candidate_fails(self):
        key=next(iter(self.blobs))
        f=self.root/(key+'.blob'); target=self.root/'actual';f.rename(target);f.symlink_to(target)
        self.assertTrue(check(self.d,self.root)['errors'])

    def test_hardlink_candidate_fails(self):
        key=next(iter(self.blobs))
        f=self.root/(key+'.blob');os.link(f,self.root/'other')
        self.assertTrue(check(self.d,self.root)['errors'])

    def test_root_symlink_fails(self):
        linked=self.root.parent/(self.root.name+'-link')
        linked.symlink_to(self.root, target_is_directory=True)
        self.addCleanup(lambda:linked.unlink(missing_ok=True))
        self.assertTrue(check(self.d,linked)['errors'])

    def test_body_cite_tokens_and_word_count(self):
        x=next(c for c in check(self.d,self.root)['fork_reviews'] if c['path'].endswith('body.html'))
        m=x['candidates'][0]['metrics']
        self.assertIn('s-1',m['citation_ids_in_order'])
        self.assertGreater(m['visible_words_estimate'],8)
        self.assertIn('Original heading',m['headings_in_order'][0])

    def test_body_citation_loss_and_added_heading(self):
        a=g.inspect_bytes('preparedness/content/articles/x.body.html',b'<h2>A</h2><p>text {{cite:a}} {{cite:a}}</p>')
        b=g.inspect_bytes('preparedness/content/articles/x.body.html',b'<h2>B</h2><p>text {{cite:b}}</p>')
        out=g.delta({'branch':'a','sha':'a','metrics':a},{'branch':'b','sha':'b','metrics':b})
        self.assertEqual(out['citations_removed_from_b'],['a','a'])
        self.assertEqual(out['citations_added_in_b'],['b'])
        self.assertEqual(out['headings_removed_from_b'],['A'])
        self.assertEqual(out['headings_added_in_b'],['B'])
        self.assertTrue(out['citation_sequence_changed'])

    def test_citation_order_changed_without_count_loss(self):
        a=g.inspect_bytes('x.body.html',b'<p>{{cite:a}} {{cite:b}}</p>')
        b=g.inspect_bytes('x.body.html',b'<p>{{cite:b}} {{cite:a}}</p>')
        out=g.delta({'branch':'x','sha':'a','metrics':a},{'branch':'y','sha':'b','metrics':b})
        self.assertEqual(out['citations_removed_from_b'],[])
        self.assertTrue(out['citation_sequence_changed'])

    def test_hidden_script_not_reading_words(self):
        x=g.inspect_bytes('x.body.html',b'<script>hidden hidden</script><div aria-hidden="true">private</div><p>visible words here</p>')
        self.assertEqual(x['visible_words_estimate'],3)

    def test_void_tag_does_not_hide_visible_body(self):
        x=g.inspect_bytes('x.body.html',b'<p>word one<img src="image">word two<br>word three</p>')
        self.assertEqual(x['visible_words_estimate'],6)

    def test_meta_json_rejects_duplicate_keys(self):
        with self.assertRaises(ValueError):g.inspect_bytes('x.meta.json',b'{"a":1,"a":2}')

    def test_meta_json_preserves_sources(self):
        v=g.inspect_bytes('x.meta.json',b'{"sources":[{"id":"a"},{"id":"b"}]}')
        self.assertEqual(v['source_ids_in_source_array'],['a','b'])

    def test_source_fragment_not_safety_approval(self):
        v=g.inspect_bytes('preparedness/sources/fragments/x.json',b'{"sources":[{"id":"a"}]}')
        self.assertEqual(v['kind'],'SOURCE_FRAGMENT')
        self.assertEqual(v['source_count'],1)

    def test_no_docket_cli_returns_hold(self):
        p=subprocess.run([sys.executable,'-I',str(SCRIPT),str(self.root/'absent.json'),str(self.root)],
                         capture_output=True,text=True,timeout=15)
        self.assertEqual(p.returncode,2)
        self.assertFalse(json.loads(p.stdout)['eligible'])

    def test_synthetic_docket_cli_cannot_pass_pin(self):
        d=self.root/'docket.json';d.write_text(json.dumps(self.d))
        p=subprocess.run([sys.executable,'-I',str(SCRIPT),str(d),str(self.root)],capture_output=True,text=True,timeout=15)
        self.assertEqual(p.returncode,2)
        self.assertIn('R431_R430_ESCROW_FAILED',json.loads(p.stdout)['errors'])

    def test_symlink_docket_cli_rejected(self):
        d=self.root/'docket.json';d.write_text(json.dumps(self.d))
        alias=self.root/'alias.json';alias.symlink_to(d)
        p=subprocess.run([sys.executable,'-I',str(SCRIPT),str(alias),str(self.root)],capture_output=True,text=True,timeout=15)
        self.assertEqual(p.returncode,2)
        self.assertIn('R431_ORIGINAL_DOCKET_UNAVAILABLE_OR_INVALID:ValueError',json.loads(p.stdout)['errors'])

    def test_citation_literal_inside_hidden_block_ignored(self):
        x=g.inspect_bytes('x.body.html',b'<template>{{cite:fake}}</template><p>{{cite:real}}</p>')
        self.assertEqual(x['citation_ids_in_order'],['real'])

    def test_reader_recovers_nested_markup(self):
        x=g.inspect_bytes('x.body.html',b'<div><span>one</span><span>two</span></div>')
        self.assertEqual(x['visible_words_estimate'],2)

    def test_unmatched_close_does_not_hang(self):
        x=g.inspect_bytes('x.body.html',b'</span><p>good</p>')
        self.assertEqual(x['visible_words_estimate'],1)

    def test_nonobject_json_rejected(self):
        with self.assertRaises(ValueError):g.inspect_bytes('x.meta.json',b'[]')

    def test_nan_json_rejected(self):
        with self.assertRaises(ValueError):g.inspect_bytes('x.meta.json',b'{"x":NaN}')

    def test_no_blank_receipt_when_complete(self):
        self.assertTrue(check(self.d,self.root)['review_receipt_sha256'])


# Every mutated editorial byte must be rejected against the original Git SHA.
BAD_BODY = [
    ('bad_token_space', b'<p>{{cite: a}}</p>'),
    ('bad_token_upper', b'<p>{{cite:ABC}}</p>'),
    ('bad_token_empty', b'<p>{{cite:}}</p>'),
    ('bad_link_space', b'<p>{{link: a}}</p>'),
    ('bad_link_upper', b'<p>{{link:ABC}}</p>'),
    ('nul_body', b'<p>zero\x00word</p>'),
    ('invalid_utf8', b'<p>\xff</p>'),
]

for name,payload in BAD_BODY:
    def fn(self, body=payload):
        with self.assertRaises((ValueError,UnicodeError)):
            g.inspect_bytes('x.body.html',body)
    setattr(Baseline,'test_reject_'+name,fn)

BAD_JSON = [
    ('duplicate', b'{"x":1,"x":2}'),
    ('nan', b'{"x":NaN}'),
    ('inf', b'{"x":Infinity}'),
    ('list', b'[]'),
    ('str', b'"string"'),
    ('int', b'42'),
    ('null', b'null'),
    ('bad_utf8', b'{"x":"\xff"}'),
    ('nul', b'{"x":"\\u0000"}'),
]
for name,payload in BAD_JSON:
    def fn(self, raw=payload):
        with self.assertRaises((ValueError,UnicodeError)):
            # NUL in JSON string is not acceptable
            g.inspect_bytes('x.meta.json',raw)
    setattr(Baseline,'test_reject_json_'+name,fn)

BAD_BLOB_PARAMS = [
    ('sha_short','abc',20),('sha_upper','A'*40,20),('sha_traversal','../'+'a'*40,20),
    ('sha_slash','a'*39+'/',20),('length_bool','a'*40,True),('length_zero','a'*40,0),
    ('length_negative','a'*40,-1),('length_huge','a'*40,2_000_001),
    ('length_string','a'*40,'12'),('length_float','a'*40,1.2),
]
for name,sha,length in BAD_BLOB_PARAMS:
    def fn(self,s=sha,n=length):
        with self.assertRaises(ValueError):g.safe_blob(self.root,s,n)
    setattr(Baseline,'test_reject_blob_'+name,fn)

if __name__ == '__main__':unittest.main()