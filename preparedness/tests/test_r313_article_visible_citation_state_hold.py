"""Adversarial R313 fixtures; never touches authentic source or WordPress."""
from __future__ import annotations
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / 'tools/r313_article_visible_citation_state_hold.py'
spec = importlib.util.spec_from_file_location('r313_visible', MODULE)
r313 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r313)

SLUG = 'article-1'
META = {'slug':SLUG,'track':'modern','section':'start-here',
        'status':{'editorial':'drafted','publish':'draft'},
        'safety_review':{'state':'pending','reviewer':None,'date':None},
        'source_use':{'source-a':'Official guidance with limits'}}
TAX = {'slug':SLUG,'track':'modern','section':'start-here','gate':True}
BODY = '<section><p>Before you act, follow the source. {{cite:source-a}}</p></section>'

class VisibilityUnitTests(unittest.TestCase):
    def inspect(self, body=BODY, meta=None, tax=None):
        return r313.inspect_visible_evidence(SLUG,body, META if meta is None else meta,TAX if tax is None else tax)

    def test_baseline_draft_held(self):
        errors,w = self.inspect()
        self.assertEqual(errors,[])
        self.assertEqual(w['visible_citation_occurrences'],1)
        self.assertEqual(w['nonvisible_citation_occurrences'],0)
        self.assertFalse(w['publication_authorized'])
        self.assertFalse(w['claim_safety_verified'])

    def test_multiple_legit_citations(self):
        errors,w = self.inspect('<p>{{cite:source-a}} and {{cite:source-b}}</p>')
        self.assertEqual(errors,[])
        self.assertEqual(w['visible_citation_occurrences'],2)

    def test_comment_citation_is_not_visible(self):
        errors,_ = self.inspect('<p>Unattributed claim.</p><!--{{cite:source-a}}-->')
        self.assertIn('ARTICLE_NONVISIBLE_OR_UNRENDERED_CITATION:'+SLUG,errors)

    def test_attribute_citation_is_not_visible(self):
        errors,_ = self.inspect('<p title="{{cite:source-a}}">Claim</p>')
        self.assertIn('ARTICLE_NONVISIBLE_OR_UNRENDERED_CITATION:'+SLUG,errors)

    def test_visible_and_hidden_duplicate_citation(self):
        errors,w = self.inspect('<p>Claim {{cite:source-a}}</p><template>{{cite:source-a}}</template>')
        self.assertTrue(errors)
        self.assertEqual((w['visible_citation_occurrences'],w['nonvisible_citation_occurrences']),(1,1))

    def test_ordinary_visible_inline_markup(self):
        errors,w = self.inspect('<p><strong>Check.</strong>{{cite:source-a}}</p>')
        self.assertFalse(errors)
        self.assertEqual(w['visible_citation_occurrences'],1)

    def test_void_tag_is_not_left_open(self):
        errors,_ = self.inspect('<p>Text <br/> {{cite:source-a}}</p>')
        self.assertEqual(errors,[])

    def test_not_required_ungated_historical_only(self):
        m={**META,'safety_review':{'state':'not-required','reviewer':None,'date':None}}
        t={**TAX,'gate':False}
        self.assertEqual(self.inspect(meta=m,tax=t)[0],[])

    def test_not_required_gated_rejected(self):
        m={**META,'safety_review':{'state':'not-required','reviewer':None,'date':None}}
        errors,_=self.inspect(meta=m)
        self.assertIn('GATED_ARTICLE_DECLARED_SAFETY_NOT_REQUIRED:'+SLUG,errors)

    def test_inherited_meta_hold_not_approved(self):
        m={**META,'status':{'editorial':'drafted','publish':'draft'},'safety_review':{'state':'pending'}}
        self.assertEqual(self.inspect(meta=m)[0],[])

    def test_encoded_html_entity_in_other_text(self):
        errors,_=self.inspect('<p>Household &amp; emergency {{cite:source-a}}</p>')
        self.assertEqual(errors,[])

    def test_nested_visible_elements(self):
        errors,_=self.inspect('<article><section><p><span>Answer {{cite:source-a}}</span></p></section></article>')
        self.assertEqual(errors,[])


HIDDEN_CASES={
 'script':'<p>Uncited</p><script>{{cite:source-a}}</script>',
 'style':'<style>{{cite:source-a}}</style>',
 'template':'<template>{{cite:source-a}}</template>',
 'noscript':'<noscript>{{cite:source-a}}</noscript>',
 'textarea':'<textarea>{{cite:source-a}}</textarea>',
 'code':'<code>{{cite:source-a}}</code>',
 'pre':'<pre>{{cite:source-a}}</pre>',
 'hidden':'<p hidden>{{cite:source-a}}</p>',
 'inert':'<p inert>{{cite:source-a}}</p>',
 'aria_hidden':'<section aria-hidden="true"><p>{{cite:source-a}}</p></section>',
 'display_none':'<p style="display: none">{{cite:source-a}}</p>',
 'visibility_hidden':'<p style="color: red; visibility: hidden;">{{cite:source-a}}</p>',
 'visibility_collapse':'<p style="visibility: collapse">{{cite:source-a}}</p>',
 'nested_hidden':'<div hidden><div><em>{{cite:source-a}}</em></div></div>',
 'attribute_title':'<a title="{{cite:source-a}}">see more</a>',
 'attribute_data':'<a data-cite="{{cite:source-a}}">see more</a>',
 'html_comment':'<!-- {{cite:source-a}} -->',
 'both_visible_hidden':'<p>{{cite:source-a}}</p><div hidden>{{cite:source-a}}</div>',
 'aria_value_upper':'<div aria-hidden="TRUE">{{cite:source-a}}</div>',
 'style_whitespace':'<div style="display : none ;">{{cite:source-a}}</div>',
}
for case, html in HIDDEN_CASES.items():
    def test(self,body=html):
        errors,w=r313.inspect_visible_evidence(SLUG,body,META,TAX)
        self.assertIn('ARTICLE_NONVISIBLE_OR_UNRENDERED_CITATION:'+SLUG,errors)
        self.assertGreater(w['nonvisible_citation_occurrences'],0)
    setattr(VisibilityUnitTests,'test_hidden_'+case,test)

STATE_CASES={
 'approved':'approved','passed':'passed','cleared':'cleared','safe':'safe',
 'live':'live','published':'published','verified':'verified','complete':'complete',
 'unknown':'not-reviewed','uppercase_pending':'PENDING','uppercase_approved':'APPROVED',
 'empty':'','none':None,'boolean':True,'numeric':3,'list':['pending'],
}
for case, state in STATE_CASES.items():
    def test(self,value=state):
        m={**META,'safety_review':{'state':value}}
        errors,_=r313.inspect_visible_evidence(SLUG,BODY,m,TAX)
        self.assertIn('ARTICLE_UNKNOWN_OR_APPROVED_SAFETY_STATE:'+SLUG,errors)
    setattr(VisibilityUnitTests,'test_safety_state_'+case,test)

STATUS_CASES={
 'public':'publish','published':'published','future':'future','private':'private','inherit':'inherit',
 'uppercase_draft':'DRAFT','editorial_approved':'approved','editorial_ready':'ready',
 'editorial_missing':None,'missing_publish':None,
}
for case, val in STATUS_CASES.items():
    def test(self,value=val,which=case):
        status={'editorial':'drafted','publish':'draft'}
        status['editorial' if which.startswith('editorial') else 'publish']=value
        m={**META,'status':status}
        errors,_=r313.inspect_visible_evidence(SLUG,BODY,m,TAX)
        self.assertIn('ARTICLE_EDITORIAL_RELEASE_STATE_CHANGED:'+SLUG,errors)
    setattr(VisibilityUnitTests,'test_status_'+case,test)

STRUCTURE_CASES={
 'duplicate_attribute':'<p id="a" id="b">{{cite:source-a}}</p>',
 'wrong_end':'<p>{{cite:source-a}}</span>',
 'unclosed_p':'<p>{{cite:source-a}}',
 'stray_end':'<p>{{cite:source-a}}</p></div>',
 'void_end':'<p><br></br>{{cite:source-a}}</p>',
 'swapped_nesting':'<div><p>{{cite:source-a}}</div></p>',
}
for case, html in STRUCTURE_CASES.items():
    def test(self,body=html):
        errors,_=r313.inspect_visible_evidence(SLUG,body,META,TAX)
        self.assertIn('ARTICLE_HTML_STRUCTURE_OR_ATTRIBUTES:'+SLUG,errors)
    setattr(VisibilityUnitTests,'test_html_'+case,test)

class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='fv-r313-artifact-')
        self.root=Path(self.tmp.name)
        self.folder=self.root/'preparedness/content/articles'
        self.folder.mkdir(parents=True)
        self.ledger={'articles':[]}
        self.taxonomy={'slate':[]}
        for n in range(1,36):
            slug=f'article-{n}'
            b=BODY.replace('Claim','Fact')
            m={**META,'slug':slug}
            self.write(slug,b,m)
            self.ledger['articles'].append({'slug':slug,
                                            'integrated_body_blob':r313.r310.oid((self.folder/f'{slug}.body.html').read_bytes()),
                                            'integrated_meta_blob':r313.r310.oid((self.folder/f'{slug}.meta.json').read_bytes())})
            self.taxonomy['slate'].append({**TAX,'slug':slug})

    def tearDown(self): self.tmp.cleanup()

    def write(self,slug,body,meta):
        (self.folder/f'{slug}.body.html').write_text(body,encoding='utf-8')
        (self.folder/f'{slug}.meta.json').write_text(json.dumps(meta),encoding='utf-8')

    def audit(self): return r313.audit_visibility(self.root,ledger=self.ledger,taxonomy=self.taxonomy)

    def test_baseline_is_not_release_pass(self):
        result=self.audit()
        self.assertEqual(result['state'],'DRAFT_HARD_HOLD',result['errors'])
        self.assertEqual((result['article_count'],result['visible_citations'],result['nonvisible_citations']),(35,35,0))
        self.assertFalse(result['publication_authorized'])
        self.assertFalse(result['all_41_wordpress_draft_exports_verified'])

    def test_real_metadata_json_duplicate_safety_review_key_fails(self):
        p=self.folder/'article-2.meta.json'
        p.write_text('{"safety_review":{"state":"pending"}, "safety_review":{"state":"approved"}}')
        self.ledger['articles'][1]['integrated_meta_blob']=r313.r310.oid(p.read_bytes())
        self.assertIn('ARTICLE_DUPLICATE_METADATA_KEY_OR_ENCODING:article-2',self.audit()['errors'])

    def test_a_single_hidden_source_in_35_articles_blocks(self):
        slug='article-21';p=self.folder/f'{slug}.body.html'
        p.write_text('<div hidden>{{cite:source-a}}</div>')
        self.ledger['articles'][20]['integrated_body_blob']=r313.r310.oid(p.read_bytes())
        self.assertIn('ARTICLE_NONVISIBLE_OR_UNRENDERED_CITATION:'+slug,self.audit()['errors'])

    def test_missing_article_source(self):
        (self.folder/'article-3.body.html').unlink()
        self.assertIn('ARTICLE_SOURCE_MISSING_OR_SYMLINK:article-3',self.audit()['errors'])

    def test_drift_pin(self):
        p=self.folder/'article-7.body.html';p.write_text(p.read_text()+' ') 
        self.assertIn('ARTICLE_SOURCE_BLOB_DRIFT:article-7',self.audit()['errors'])

    def test_symlink_source(self):
        p=self.folder/'article-5.body.html';v=p.read_bytes();p.unlink()
        other=self.root/'other';other.write_bytes(v);p.symlink_to(other)
        self.assertIn('ARTICLE_SOURCE_MISSING_OR_SYMLINK:article-5',self.audit()['errors'])

    def test_taxonomy_duplicate_slug(self):
        self.taxonomy['slate'][3]['slug']='article-1'
        self.assertIn('TAXONOMY_ARTICLE_SLATE_MISMATCH',self.audit()['errors'])

    def test_unmatched_taxonomy_count(self):
        self.taxonomy['slate'].pop()
        self.assertIn('EXPECTED_35_ARTICLES_AND_TAXONOMY_ROWS',self.audit()['errors'])

    def test_incomplete_checkout_fails(self):
        run=subprocess.run([sys.executable,'-I',str(MODULE),'--root',str(self.root)],capture_output=True,text=True)
        self.assertEqual(run.returncode,1,run.stdout+run.stderr)
        self.assertEqual(json.loads(run.stdout)['state'],'INVALID_HARD_HOLD')

    def test_predecessor_sha_matches_provided_r312_package(self):
        path=ROOT/'tools/r312_article_citation_parity_hold.py'
        self.assertEqual(r313.r310.oid(path.read_bytes()),r313.PREDECESSOR_OID)

if __name__=='__main__':unittest.main()
