"""R287 synthetic fail-closed body-to-metadata/source crosswalk tests.
All synthetic mutation tests are side-effect-free: no network, CMS, sales, or
source-directory writes. Authentic 41-file checkout still requires native CI.
"""
from __future__ import annotations
import importlib.util
import copy
import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('r287',ROOT/'tools/r287_body_citation_provenance_hold.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
def fixture():
    entries=[];bodies={};meta={}
    for role,amount in (('article',35),('tool',6)):
        for i in range(amount):
            slug=f'{role}-{i:02d}'
            stem=f'content/{role}s/{slug}'
            bp=stem+'.body.html';mp=stem+'.meta.json'
            entries.extend([{'role':role+'_body','path':bp},
                            {'role':role+'_meta','path':mp}])
            bodies[bp]=b'<p>Source {{cite:src-1}} for readers.</p>'
            meta[mp]={'slug':slug,'source_use':{'src-1':'Synthetic scope'}}
    names=['sources/register.json']+['sources/fragments/'+x+'.json' for x in
           ('start','shelter','food','health','hist-field','hist-food','hist-home')]
    sources={k:{'sources':[]} for k in names}
    for n in range(244):
        sources[names[n%8]]['sources'].append(
            {'id':f'src-{n}','url':f'https://example.invalid/{n}',
             'verified_on':None,'human_link_check':False})
    entries += [{'role':'source_origin','path':s} for s in names]
    entries += [{'role':'docket','path':f'audit/extra-{x}'} for x in range(6)]
    assert len(entries)==96
    return entries,bodies,meta,sources
class SyntheticCrosswalk(unittest.TestCase):
    def setUp(self):self.e,self.b,self.m,self.s=fixture()
    def result(self):return g.evaluate(self.e,self.b,self.m,self.s)
    def test_complete_count(self):
        a=self.result();self.assertEqual((a['body_count'],a['article_count'],a['tool_count']),(41,35,6))
    def test_source_row_count(self):self.assertEqual(self.result()['frozen_source_rows'],244)
    def test_41_paired_edges(self):self.assertEqual(self.result()['body_source_edges'],41)
    def test_occurrence_count(self):self.assertEqual(self.result()['inline_citation_occurrences'],41)
    def test_no_unverified_source_promotion(self):
        self.assertIsNone(self.result()['crosswalk'][0]['candidates'][0]['verified_on'])
    def test_stable_order(self):
        self.assertEqual(self.result()['crosswalk'],
                         sorted(self.result()['crosswalk'],key=lambda x:(x['body'],x['source_id'])))
    def test_draft_hold(self):self.assertEqual(self.result()['state'],g.HOLD)
    def test_no_auto_release(self):
        r=self.result()
        for key in ('publication_authorized','independent_qd_pass','medical_safety_verified','privacy_approved'):
            self.assertIs(r[key],False)
    def test_review_remains_required(self):
        self.assertTrue(self.result()['requires_human_citation_scope_review'])
        self.assertTrue(self.result()['requires_qualified_safety_review'])
    def test_repeated_citation_counts(self):
        k=next(iter(self.b));self.b[k]+=b' {{cite:src-1}}'
        self.assertEqual(self.result()['inline_citation_occurrences'],42)
        self.assertEqual(self.result()['body_source_edges'],41)
    def test_unused_meta_is_review_only(self):
        mp=next(iter(self.m));self.m[mp]['source_use']['src-5']='Historical contextual source'
        self.assertEqual(len(self.result()['metadata_only_source_review']),1)
    def test_body_without_marker_is_review_only(self):
        bp=next(iter(self.b));self.b[bp]=b'<p>Still draft</p>'
        self.assertIn(bp,self.result()['uncited_body_review'])
    def test_collision_stays_ambiguous(self):
        keys=sorted(self.s);self.s[keys[0]]['sources'][0]['id']='src-1'
        r=self.result();self.assertEqual(len(r['ambiguous_body_source_edges']),41)
        self.assertEqual(len(r['crosswalk'][0]['candidates']),2)
    def test_missing_body_rejected(self):
        self.b.pop(next(iter(self.b)))
        with self.assertRaisesRegex(ValueError,'body bytes missing'):self.result()
    def test_extra_body_rejected(self):
        self.b['content/articles/rogue.body.html']=b''
        with self.assertRaisesRegex(ValueError,'body bytes missing'):self.result()
    def test_missing_meta_rejected(self):
        self.m.pop(next(iter(self.m)))
        with self.assertRaisesRegex(ValueError,'metadata rows missing'):self.result()
    def test_source_missing_rejected(self):
        p=next(iter(self.s));self.s[p]['sources'].pop()
        with self.assertRaisesRegex(ValueError,'source identity census'):self.result()
    def test_extra_source_rejected(self):
        p=next(iter(self.s));self.s[p]['sources'].append({'id':'injected','url':'https://x'})
        with self.assertRaisesRegex(ValueError,'source identity census'):self.result()
    def test_duplicate_manifest_path(self):
        self.e[-1]['path']=self.e[-2]['path']
        with self.assertRaisesRegex(ValueError,'duplicate inventory paths'):self.result()
    def test_wrong_role(self):
        self.e[0]['role']='tool_body'
        with self.assertRaisesRegex(ValueError,'article_body census'):self.result()
    def test_orphan_marker_missing_metadata(self):
        k=next(iter(self.b));self.b[k]=b'{{cite:ghost}}'
        with self.assertRaisesRegex(ValueError,'missing metadata source_use'):self.result()
    def test_orphan_marker_missing_register(self):
        k=next(iter(self.b));self.b[k]=b'{{cite:ghost}}'
        self.m[k.replace('.body.html','.meta.json')]['source_use']['ghost']='fiction'
        with self.assertRaisesRegex(ValueError,'absent from frozen register'):self.result()
    def test_exact_bridge_source_present(self):
        p=(ROOT/'tools/r285_metadata_source_bridge_hold.py')
        self.assertEqual(g.git_blob(p.read_bytes()),g.BRIDGE_SHA)
    def test_missing_bridge_fails(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,'bridge missing'):g.load_bridge(td)
    def test_bridge_modified_fails(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/g.BRIDGE_FILE;p.parent.mkdir(parents=True)
            p.write_bytes(b'def audit(root):return {"state":"LIVE"}')
            with self.assertRaisesRegex(ValueError,'Git identity'):g.load_bridge(td)
    def test_bridge_symlink_fails(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/g.BRIDGE_FILE;p.parent.mkdir(parents=True)
            p.symlink_to(ROOT/'tools/r285_metadata_source_bridge_hold.py')
            with self.assertRaises(ValueError):g.load_bridge(td)
    def test_pinned_loader_compiles_verified_source(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/g.BRIDGE_FILE;p.parent.mkdir(parents=True)
            p.write_bytes((ROOT/'tools/r285_metadata_source_bridge_hold.py').read_bytes())
            self.assertEqual(g.load_bridge(td).HOLD,g.HOLD)

class MarkerParsing(unittest.TestCase):
    def test_basic(self):self.assertEqual(g.parse_cites(b'{{cite:src-1}}','sample'),Counter({'src-1':1}))
    def test_unicode_text(self):self.assertIn('src-1',g.parse_cites('Café {{cite:src-1}}'.encode(),'sample'))
    def test_empty_body(self):self.assertEqual(len(g.parse_cites(b'<p>No cite</p>','sample')),0)
    def test_nonbytes(self):
        with self.assertRaises(ValueError):g.parse_cites('{{cite:x}}','sample')
    def test_invalid_utf8(self):
        with self.assertRaises(UnicodeError):g.parse_cites(b'\xff','sample')

MALFORMED=[
  '{{cite:}}','{{cite:one','{{cite:two three}}','{{cite:one,two}}',
  '{{cite: one}}','{{cite:one }}','{{cite:one|page=12}}','{{CITE:one}}',
  '{{ cite:one}}','{{cite:one\n}}','{{cite:one\t}}','{{cite:one/two}}',
  '{{cite:../one}}','{{cite:one?x=3}}','{{cite:one#two}}',
  '{{cite:one&t=2}}','{{cite:one<t}}','{{cite:one\r}}','{{cite:{one}}}'
]
for idx,marker in enumerate(MALFORMED):
    def invalid(self, value=marker):
        with self.assertRaises(ValueError):g.parse_cites(value.encode(),'fixture')
    setattr(MarkerParsing,f'test_malformed_{idx:02d}',invalid)
if __name__=='__main__':unittest.main(verbosity=2)
