#!/usr/bin/env python3
"""R367 offline adversarial custody: 41 document + 8 hub + 1 landing fixture, no network."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'tools'/'r367_wp_preview_source_custody.py'
spec=importlib.util.spec_from_file_location('r367_output',SCRIPT)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

SLUG='family-contact-card'
SRC='ready-plan'
IN='''<div class="pa pa-article" data-slug="family-contact-card"><p>Draft: not public</p>
<p>Independent safety/source and QD verification pending</p>
<p>Human source-link check pending</p>
<p>Sources and verification</p><p>Plan<sup class="pa-cite"><a href="#src-1" aria-label="Source 1: Ready">[1]</a></sup></p>
<ol><li id="src-1"><a href="https://www.ready.gov/plan" rel="noopener">Ready</a></li></ol>
<script type="application/ld+json">{"isAccessibleForFree": true}</script></div>'''

def wrap(body=IN):
    return ('<!-- wp:html -->\n<style>.pa{color:black}</style>\n'+body+'\n<!-- /wp:html -->\n',
            '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><style>.pa{color:black}</style></head><body><main>'+body+'</main></body></html>')

def validate(*,body=IN,wp=None,preview=None,sources=None):
    a,b=wrap(body)
    return m.pair(wp if wp is not None else a,preview if preview is not None else b,SLUG,[SRC] if sources is None else sources)

class PairChecks(unittest.TestCase):
    def test_clean_pair(self):
        e,r,f=validate();self.assertFalse(e,e);self.assertEqual(f['source_ids'],1)
        self.assertEqual(f['citation_occurrences'],1)
    def test_deterministic(self):self.assertEqual(validate(),validate())
    def test_no_approval_flags(self):
        self.assertTrue(all(value is False for value in m.make_report([],[],{}) .values() if isinstance(value,bool)))
    def test_hard_hold_without_error(self):self.assertEqual(m.make_report([],[],{})['status'],'REVIEW_REQUIRED_HARD_HOLD')
    def test_hard_hold_with_error(self):self.assertEqual(m.make_report(['E'],[],{})['status'],'INVALID_HARD_HOLD')
    def test_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json';p.write_text('{"x":1,"x":2}')
            with self.assertRaisesRegex(ValueError,'DUPLICATE_JSON_KEY'):m.json_clean(p)
    def test_source_url_same(self):
        self.assertFalse(m.pair(*wrap(),SLUG,[SRC],source_urls=['https://www.ready.gov/plan'])[0])
    def test_source_url_wrong(self):
        self.assertIn('SOURCE_DESTINATION_CHANGED:1',m.pair(*wrap(),SLUG,[SRC],source_urls=['https://evil.example/'])[0])
    def test_digest_stable(self):self.assertEqual(m.digest('hello'),m.digest('hello'))
    def test_invalid_type_export(self):self.assertIn('BAD_EXPORT_CONTENT',m.pair(None,'',SLUG,[SRC])[0])
    def test_invalid_oversized_export(self):self.assertIn('BAD_EXPORT_CONTENT',m.pair('X'*2000001,'',SLUG,[SRC])[0])
    def test_no_checkout_hard_hold(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIn('AUTHENTIC_NATIVE_PREPAREDNESS_ROOT_REQUIRED',m.audit(Path(d))['errors'])

BODY_CHANGES={
'wrong_slug':IN.replace('family-contact-card','other-card'),
'zero_footnote':IN.replace('<sup class="pa-cite"><a href="#src-1" aria-label="Source 1: Ready">[1]</a></sup>',''),
'wrong_footnote':IN.replace('href="#src-1"','href="#src-2"'),
'wrong_label':IN.replace('aria-label="Source 1: Ready"','aria-label="Source 2: Ready"'),
'wrong_display':IN.replace('>[1]</a>','>[2]</a>'),
'wrong_src_number':IN.replace('id="src-1"','id="src-2"'),
'no_source_list':IN.replace('<li id="src-1"><a href="https://www.ready.gov/plan" rel="noopener">Ready</a></li>',''),
'wrong_src_url':IN.replace('https://www.ready.gov/plan','https://example.org/plan'),
'no_draft':IN.replace('Draft: not public','Draft'),
'no_qd_notice':IN.replace('Independent safety/source and QD verification pending','Reviewed'),
'no_human_notice':IN.replace('Human source-link check pending','Human verified'),
'no_source_heading':IN.replace('Sources and verification','Links'),
'false_free':IN.replace('"isAccessibleForFree": true','"isAccessibleForFree": false'),
'no_free_schema':IN.replace('"isAccessibleForFree": true','"name": "unfree"'),
'no_container':IN.replace('class="pa pa-article"','class="unrelated"'),
'leftover_cite':IN+'{{cite:unknown}}',
'leftover_link':IN+'{{link:elsewhere|go}}',
'partial_token':IN+'}}',
'new_human_link_check':IN.replace('Human source-link check pending','Human source-link check pending; Human source-link check complete'),
'wrong_src_attribute':IN.replace(' rel="noopener"',''),
'missing_sup_class':IN.replace('class="pa-cite"','class="bad-cite"'),
'missing_aria':IN.replace('aria-label="Source 1: Ready"','aria-label=""'),
'duplicate_source_id':IN.replace('</ol>','<li id="src-1"><a href="https://www.ready.gov/plan" rel="noopener">Ready</a></li></ol>'),
'wrong_article_status':IN.replace('Draft: not public','Published'),
}
class BodyRegressions(unittest.TestCase):pass
for key,body in BODY_CHANGES.items():
    def test(self,b=body,k=key):
        e,r,_=m.pair(*wrap(b),SLUG,[SRC],source_urls=['https://www.ready.gov/plan'])
        self.assertTrue(e or r,k)
    setattr(BodyRegressions,'test_body_'+key,test)

WRAPPER_CHANGES={
'wp_prefix':lambda a,b:('prefix'+a,b),
'wp_suffix':lambda a,b:(a+'suffix',b),
'wp_double_blocks':lambda a,b:(a+'<!-- wp:html -->',b),
'wp_no_close':lambda a,b:(a.replace('<!-- /wp:html -->',''),b),
'wp_wrong_block':lambda a,b:(a.replace('wp:html','wp:paragraph'),b),
'preview_no_noindex':lambda a,b:(a,b.replace('<meta name="robots" content="noindex,nofollow">','')),
'preview_index':lambda a,b:(a,b.replace('noindex,nofollow','index,follow')),
'preview_no_main':lambda a,b:(a,b.replace('<main>','')),
'preview_wrong_ending':lambda a,b:(a,b[:-7]),
'preview_wrong_inner':lambda a,b:(a,b.replace('Plan<sup','Plans<sup')),
'preview_uppercase_doctype':lambda a,b:(a,b.replace('<!doctype html>','<!DOCTYPE HTML>')),
'preview_extra_body':lambda a,b:(a,b.replace('</main>','<p>injected</p></main>')),
'wp_extra_inner':lambda a,b:(a.replace('</div>\n<!-- /wp','</div><p>injected</p>\n<!-- /wp'),b),
}
class WrapperRegressions(unittest.TestCase):pass
for key,mutate in WRAPPER_CHANGES.items():
    def test(self,f=mutate,k=key):
        a,b=wrap();a,b=f(a,b)
        e,_,_=validate(wp=a,preview=b)
        self.assertTrue(e,k)
    setattr(WrapperRegressions,'test_wrapper_'+key,test)


def full_fixture(base):
    root=base/'preparedness'; (root/'content'/'articles').mkdir(parents=True)
    (root/'content'/'tools').mkdir(parents=True);(root/'tools').mkdir()
    (root/'tools'/'build.py').write_text('fixture only')
    (root/'taxonomy.json').write_text('{}')
    (root/'sources'/'fragments').mkdir(parents=True)
    (root/'sources'/'register.json').write_text(json.dumps({'sources':[{'id':'ready-plan','url':'https://www.ready.gov/plan'}]}))
    b=root/'build';(b/'wp').mkdir(parents=True);(b/'preview').mkdir()
    article_rows=[]
    for n in range(1,42):
        slug=f'guide-{n:02d}'
        folder=root/'content'/('articles' if n<=35 else 'tools')
        (folder/f'{slug}.meta.json').write_text(json.dumps({'slug':slug,'status':{'publish':'draft'}}))
        (folder/f'{slug}.body.html').write_text('<p>Plan {{cite:ready-plan}}</p>')
        body=IN.replace(SLUG,slug)
        a,c=wrap(body)
        (b/'wp'/f'{slug}.html').write_text(a)
        (b/'preview'/f'{slug}.html').write_text(c)
        article_rows.append({'slug':slug,'sources':['ready-plan'],'canonical':'https://finalvestige.com/preparedness/plan/'+slug+'/'})
    hubs=[{'section':f'section-{n}','guides':1} for n in range(1,9)]
    for slug in [f'hub-section-{n}' for n in range(1,9)]+['landing']:
        a,c=wrap('<div>static archive hub</div>');(b/'wp'/f'{slug}.html').write_text(a);(b/'preview'/f'{slug}.html').write_text(c)
    (root/'sources'/'crosswalk.json').write_text(json.dumps({'article_origins':{row['slug']:'base' for row in article_rows}}))
    report={'articles':article_rows,'hubs':hubs,'release_evidence':{'independent_qa_verified':False,'wordpress_publication_performed':False,'state':'HOLD'}}
    (b/'build-report.json').write_text(json.dumps(report))
    return root,b

class FullExportChecks(unittest.TestCase):
    def test_full_50_pair_synthetic(self):
        with tempfile.TemporaryDirectory() as d:
            p,b=full_fixture(Path(d));r=m.audit(p,b)
            self.assertEqual(r['status'],'REVIEW_REQUIRED_HARD_HOLD',r['errors']);self.assertEqual(r['evidence']['paired_exports_inspected'],50)
            self.assertTrue(all(r[k] is False for k in m.HOLD))
    def test_missing_export_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p,b=full_fixture(Path(d));(b/'wp'/'guide-01.html').unlink()
            self.assertEqual(m.audit(p,b)['status'],'INVALID_HARD_HOLD')
    def test_extra_export_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p,b=full_fixture(Path(d));(b/'preview'/'new.html').write_text('foo')
            self.assertTrue(any('INVENTORY_DRIFT' in x for x in m.audit(p,b)['errors']))
    def test_wrong_nameless_article_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p,b=full_fixture(Path(d));f=p/'content'/'articles'/'guide-01.meta.json'
            f.write_text(json.dumps({'slug':'guide-02','status':{'publish':'draft'}}))
            self.assertEqual(m.audit(p,b)['status'],'INVALID_HARD_HOLD')
    def test_revenue_promotion_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p,b=full_fixture(Path(d));f=b/'build-report.json';r=json.loads(f.read_text())
            r['release_evidence']['independent_qa_verified']=True;f.write_text(json.dumps(r))
            self.assertTrue(any('RELEASE_ASSERTION' in x for x in m.audit(p,b)['errors']))
    def test_wrong_source_order_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p,b=full_fixture(Path(d));f=b/'build-report.json';r=json.loads(f.read_text())
            r['articles'][0]['sources']=['fake-id'];f.write_text(json.dumps(r))
            self.assertTrue(any('RAW_CITATION_ORDER' in x for x in m.audit(p,b)['errors']))
    def test_canonical_retarget_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p,b=full_fixture(Path(d));f=b/'build-report.json';r=json.loads(f.read_text())
            r['articles'][0]['canonical']='https://evil.example/checkout';f.write_text(json.dumps(r))
            self.assertTrue(any('CANONICAL_URL_DRIFT' in x for x in m.audit(p,b)['errors']))
    def test_non_draft_source_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p,b=full_fixture(Path(d));f=p/'content'/'tools'/'guide-40.meta.json';r=json.loads(f.read_text())
            r['status']['publish']='published';f.write_text(json.dumps(r))
            self.assertTrue(any('NON_DRAFT_INPUT' in x for x in m.audit(p,b)['errors']))
    def test_missing_hub_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p,b=full_fixture(Path(d));f=b/'build-report.json';r=json.loads(f.read_text())
            r['hubs'].pop();f.write_text(json.dumps(r))
            self.assertTrue(any('PRIVATE_HUB_COUNT_NOT_8' in x for x in m.audit(p,b)['errors']))
    def test_report_duplicate_json_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p,b=full_fixture(Path(d));(b/'build-report.json').write_text('{"articles":[],"articles":[]}')
            self.assertEqual(m.audit(p,b)['status'],'INVALID_HARD_HOLD')

if __name__=='__main__':unittest.main()
