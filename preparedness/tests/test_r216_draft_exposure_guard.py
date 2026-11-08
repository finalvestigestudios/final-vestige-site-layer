"""R216 source-only synthetic tests; not a complete repository QA or medical signoff."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('r216',Path(__file__).resolve().parents[1]/'tools'/'r216_draft_exposure_guard.py')
g = importlib.util.module_from_spec(spec);spec.loader.exec_module(g)


def page(article):
    return (f'<!-- wp:html --><div class="pa"><header><ul class="pa-chips"><li>Draft: not public</li>'
            f'<li>Safety review pending</li></ul></header><div class="pa-shell">'
            f'<div class="pa-body"><p>Household preparation checklist article {article}. '
            f'<a href="#src-1">[1]</a></p></div></div>'
            f'<section class="pa-sources"><ol><li id="src-1">'
            f'<a href="https://www.ready.gov/plan">Official source</a></li></ol></section>'
            f'<section class="pa-review">Pending. A human safety review is required before publication.</section>'
            f'</div><!-- /wp:html -->').encode()


def fixture():
    docs={n:{c:page(n) for c in ('wp','preview')} for n in (7,20)}
    prior={'schema':'fv-preparedness-r215-wp-draft-transport-v1','state':g.HOLD,'errors':[],
           'independent_qd_pass':False,'publication_authorized':False,'medical_safety_verified':False,
           'articles':[{'article':n,'render_sha256':{c:hashlib.sha256(docs[n][c]).hexdigest() for c in ('wp','preview')}} for n in (7,20)]}
    return prior,docs


def with_mutation(edit, number=7, channel='wp'):
    prior,docs=fixture()
    assert g.evaluate(prior,docs)['state']==g.HOLD
    docs[number][channel]=edit(docs[number][channel].decode()).encode()
    # Recompute synthetic upstream digest: R216 must independently reject the dangerous DOM,
    # not merely detect a stale receipt from a prior report.
    row=next(r for r in prior['articles'] if r['article']==number)
    row['render_sha256'][channel]=hashlib.sha256(docs[number][channel]).hexdigest()
    return g.evaluate(prior,docs)


class R216Test(unittest.TestCase):
    def test_healthy_draft_is_hold_not_pass(self):
        p,r=fixture();o=g.evaluate(p,r)
        self.assertEqual(o['state'],g.HOLD,o)
        self.assertEqual(len(o['transports']),4)
        self.assertTrue(all(t['source_count']==1 for t in o['transports']))
        self.assertIs(o['publication_authorized'],False)
        self.assertIs(o['medical_safety_verified'],False)
    def test_stable_receipts(self):
        p,r=fixture();self.assertEqual(g.evaluate(p,r),g.evaluate(p,r))
    def test_wrong_prior_schema(self):
        p,r=fixture();p['schema']='different';self.assertEqual(g.evaluate(p,r)['state'],g.INVALID)
    def test_prior_approved_state_refused(self):
        p,r=fixture();p['state']='QD_PASS';self.assertEqual(g.evaluate(p,r)['state'],g.INVALID)
    def test_prior_empty_errors_required(self):
        p,r=fixture();p['errors']=['unreviewed'];self.assertEqual(g.evaluate(p,r)['state'],g.INVALID)
    def test_prior_flags_false_required(self):
        for key in ('publication_authorized','independent_qd_pass','medical_safety_verified'):
            p,r=fixture();p[key]=True
            with self.subTest(key=key):self.assertEqual(g.evaluate(p,r)['state'],g.INVALID)
    def test_prior_digest_drift_refused(self):
        p,r=fixture();p['articles'][0]['render_sha256']['wp']='f'*64
        self.assertIn('receipt drift',' '.join(g.evaluate(p,r)['errors']))
    def test_missing_channel_refused(self):
        p,r=fixture();del r[7]['preview'];self.assertEqual(g.evaluate(p,r)['state'],g.INVALID)
    def test_unknown_article_refused(self):
        p,r=fixture();r[21]=r[20];self.assertEqual(g.evaluate(p,r)['state'],g.INVALID)
    def test_invalid_utf8_refused(self):
        p,r=fixture();r[7]['wp']=b'\xff';p['articles'][0]['render_sha256']['wp']=hashlib.sha256(b'\xff').hexdigest()
        self.assertEqual(g.evaluate(p,r)['state'],g.INVALID)
    def test_empty_render_refused(self):
        p,r=fixture();r[7]['wp']=b'';p['articles'][0]['render_sha256']['wp']=hashlib.sha256(b'').hexdigest()
        self.assertEqual(g.evaluate(p,r)['state'],g.INVALID)
    def test_source_route_is_no_approval(self):
        p,r=fixture();x=g.evaluate(p,r)
        self.assertEqual(x['source_claim_review'],'REQUIRED')
        self.assertEqual(x['state'],'DRAFT_HARD_HOLD')


def wrap_scope(html,scope,wrap):
    if scope=='pa-chips':
        before='<ul class="pa-chips">'; after='</ul>'
    elif scope=='pa-body':
        before='<div class="pa-body">'; after='</p></div>'
    elif scope=='pa-sources':
        before='<section class="pa-sources">'; after='</ol></section>'
    else:
        before='<section class="pa-review">'; after='before publication.</section>'
    end={'div':'</div>','details':'</details>','dialog':'</dialog>','template':'</template>'}.get(wrap.split()[0][1:],'</div>')
    if '<details' in wrap:end='</details>'
    if '<dialog' in wrap:end='</dialog>'
    if '<template' in wrap:end='</template>'
    return html.replace(before,wrap+before,1).replace(after,after+end,1)


WRAPPERS = [
    '<div hidden>', '<div aria-hidden="true">','<div inert>',
    '<div style="display:none">','<div style="visibility:hidden">',
    '<div style="content-visibility:hidden">','<div style="opacity:0">',
    '<div style="opacity:0!important">','<div style="color:blue; display: none!important">',
    '<div style="background:red; visibility:collapse">',
    '<details>','<dialog>','<template>'
]


def mk_visibility_test(scope,wrap):
    def test(self):
        output=with_mutation(lambda s:wrap_scope(s,scope,wrap))
        self.assertEqual(output['state'],g.INVALID,output)
        self.assertIn('concealed',' '.join(output['errors']))
    return test


LINKS = [
    'javascript:alert(1)', 'data:text/html,evil', 'file:///etc/passwd',
    '//outside.example/path', 'mailto:name@example.com', 'http://example.com',
    'vbscript:msgbox(1)', 'about:blank', 'ftp://mirror.example/file',
    '', 'https://host.test/path"onclick="x', 'https://a.example/evil\nnew',
]

def mk_link_test(url):
    def test(self):
        output=with_mutation(lambda s:s.replace('</p></div>',f'<a href="{url}">Other</a></p></div>',1))
        self.assertEqual(output['state'],g.INVALID,output)
    return test


def mk_source_link_test(url):
    def test(self):
        output=with_mutation(lambda s:s.replace('https://www.ready.gov/plan',url,1),number=20,channel='preview')
        self.assertEqual(output['state'],g.INVALID,output)
    return test


class MutationTest(unittest.TestCase):
    def test_missing_source_li_identifier(self):
        o=with_mutation(lambda s:s.replace('id="src-1"','id="wrong"'))
        self.assertEqual(o['state'],g.INVALID)
    def test_duplicate_source_identifier(self):
        o=with_mutation(lambda s:s.replace('</ol>','<li id="src-1"><a href="https://www.cdc.gov/">duplicate</a></li></ol>'))
        self.assertEqual(o['state'],g.INVALID)
    def test_out_of_order_identifier(self):
        o=with_mutation(lambda s:s.replace('id="src-1"','id="src-2"'))
        self.assertEqual(o['state'],g.INVALID)
    def test_source_without_https(self):
        o=with_mutation(lambda s:s.replace('https://www.ready.gov/plan','http://www.ready.gov/plan'))
        self.assertEqual(o['state'],g.INVALID)
    def test_body_external_new_tab_rel_missing(self):
        o=with_mutation(lambda s:s.replace('href="#src-1"','href="https://example.org/" target="_blank"'))
        self.assertEqual(o['state'],g.INVALID)
    def test_body_external_new_tab_rel_complete_allowed(self):
        o=with_mutation(lambda s:s.replace('href="#src-1"','href="https://example.org/" target="_blank" rel="noopener noreferrer"'))
        self.assertEqual(o['state'],g.HOLD,o)
    def test_duplicate_body_scope(self):
        o=with_mutation(lambda s:s.replace('</div></div><section class="pa-sources">','</div><div class="pa-body">Duplicate</div></div><section class="pa-sources">'))
        self.assertEqual(o['state'],g.INVALID)
    def test_unclosed_article_markup(self):
        o=with_mutation(lambda s:s.replace('</div><!-- /wp:html -->','<!-- /wp:html -->'))
        self.assertEqual(o['state'],g.INVALID)
    def test_document_meta_refresh(self):
        o=with_mutation(lambda s:'<meta http-equiv="refresh" content="0;url=https://evil.example/">'+s)
        self.assertEqual(o['state'],g.INVALID)
    def test_document_base_override(self):
        o=with_mutation(lambda s:'<base href="https://evil.example/">'+s)
        self.assertEqual(o['state'],g.INVALID)
    def test_scripted_body_injection(self):
        o=with_mutation(lambda s:s.replace('</p></div>','<script>inject()</script></p></div>'))
        self.assertEqual(o['state'],g.INVALID)
    def test_false_qd_pass_message(self):
        o=with_mutation(lambda s:s.replace('Safety review pending','QD PASS'))
        self.assertEqual(o['state'],g.INVALID)
    def test_false_medical_certification(self):
        o=with_mutation(lambda s:s.replace('human safety review is required','medical safety verified'))
        self.assertEqual(o['state'],g.INVALID)
    def test_non_utf8_type(self):
        p,r=fixture();r[7]['wp']='text';self.assertEqual(g.evaluate(p,r)['state'],g.INVALID)
    def test_hidden_body_ancestor_was_textual_parity_gap(self):
        o=with_mutation(lambda s:wrap_scope(s,'pa-body','<div aria-hidden="true">'))
        self.assertIn('pa-body concealed', ' '.join(o['errors']))


for scope in g.SCOPES:
    for i,wrap in enumerate(WRAPPERS):
        setattr(MutationTest,f'test_{scope.replace("-","_")}_concealed_{i:02}',mk_visibility_test(scope,wrap))
for i,url in enumerate(LINKS):
    setattr(MutationTest,f'test_unsafe_body_link_{i:02}',mk_link_test(url))
    setattr(MutationTest,f'test_unsafe_source_link_{i:02}',mk_source_link_test(url))

if __name__=='__main__':
    unittest.main()
