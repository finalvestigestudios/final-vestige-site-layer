"""Offline synthetic fixtures only; does not authenticate real editorial or CMS output."""
import copy
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest

SOURCE=Path(__file__).resolve().parents[1]/'tools/r207_wordpress_render_parity_gate.py'
spec=importlib.util.spec_from_file_location('r207',SOURCE)
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)


def fixture():
    heads={f'cluster-{i}':str(i)*40 for i in range(1,8)}
    rows=[];materials={};wp={};previews={};build=[]
    template='''<section class="pa-act"><h2>What to do now</h2><p>
Household plan {n} has deliberate practical detail.{{{{cite:source-a}}}} Contact a person.
{{{{link:article-1|Keep reading}}}} and prepare a second copy.{{{{cite:source-b}}}}
Safety warning for article {n}: preserve the whole paragraph.
</p></section>'''
    def token(m):
        return '<sup class="pa-cite"><a href="#src-'+str({'source-a':1,'source-b':2}[m.group(1)])+'" aria-label="Source">[number]</a></sup>'
    for n in range(1,36):
        slug=f'article-{n}';section='start-here' if n<21 else 'lost-ways'
        owner=f'cluster-{(n-1)%7+1}'
        body=template.format(n=n).encode()
        meta={'slug':slug,'section':section,'track':'modern' if n<=20 else 'lost-ways',
              'status':{'publish':'draft'},'safety_review':{'state':'pending'}}
        meta_raw=json.dumps(meta,ensure_ascii=False).encode()
        route=f'/preparedness/{section}/{slug}/'
        rows.append({'n':n,'slug':slug,'track':meta['track'],'section':section,'route':route,
                     'source_cluster':owner,'branch_sha':heads[owner],
                     'body_oid':gate.git_oid(body),'meta_oid':gate.git_oid(meta_raw),
                     'body_bytes':len(body),'meta_bytes':len(meta_raw)})
        materials[slug]={'body':body,'meta':meta_raw}
        markup=body.decode()
        markup=re.sub(r'\{\{cite:(source-[ab])\}\}',token,markup)
        markup=re.sub(r'\{\{link:article-1\|Keep reading\}\}',
                      '<a href="/preparedness/start-here/article-1/">Keep reading</a>',markup)
        ld={'@graph':[{'@type':'Article','mainEntityOfPage':'https://finalvestige.com'+route,
                       'isAccessibleForFree':True}]}
        inner=(f'<div class="pa pa-article" data-slug="{slug}" data-track="{meta["track"]}" '
               f'data-section="{section}"><header>Draft: not public | Safety review pending</header>'
               f'<div class="pa-body" id="pa-main">{markup}</div>'
               '<div>Pending. A human safety review is required before this page can be published.</div>'
               f'<script type="application/ld+json">{json.dumps(ld)}</script></div>')
        wp[slug]=('<!-- wp:html -->\n<style>.pa { color: white; }</style>'+inner+'<!-- /wp:html -->').encode()
        previews[slug]=('<!doctype html><html><head><style>.pa {color:white}</style></head><body>'+
                        inner+'</body></html>').encode()
        build.append({'slug':slug,'canonical':'https://finalvestige.com'+route,
                      'sources':['source-a','source-b'],'words':70})
    manifest={'schema':'fv-preparedness-r200-seven-cluster-35-article-frozen-custody-v1',
       'issue':136,'conversion_issue':820,'state':gate.HOLD,
       'publication_authorized':False,'independent_qd_pass':False,
       'human_source_approved':False,'medical_safety_verified':False,
       'merchant_offer_verified':False,'verified_paid_orders':None,
       'realized_net_revenue':None,'artifact_count':35,
       'export_target_count_with_six_tools':41,'articles':rows,'branch_heads':heads}
    return manifest,materials,wp,previews,{'articles':build}

class ParityTests(unittest.TestCase):
    def setUp(self):self.man,self.materials,self.wp,self.preview,self.report=fixture()
    def run_gate(self):return gate.audit(self.man,self.materials,self.wp,self.preview,self.report)
    def reject(self):
        result=self.run_gate()
        self.assertEqual(result['state'],gate.INVALID,result)
        self.assertFalse(result['publication_authorized'])
        self.assertFalse(result['independent_qd_pass'])
        self.assertEqual(result['summary'],{})
    def test_complete_slate_structural_hold(self):
        result=self.run_gate()
        self.assertEqual(result['state'],gate.HOLD,result)
        self.assertEqual(result['summary']['original_articles'],35)
        self.assertEqual(result['summary']['wp_draft_exports_checked'],35)
        self.assertEqual(result['summary']['citation_occurrences'],70)
        self.assertFalse(result['summary']['independent_safety_qd_verified'])
        self.assertIsNone(result['realized_net_revenue'])
    def test_repeatable(self): self.assertEqual(self.run_gate(),self.run_gate())
    def test_missing_preview(self): self.preview.pop('article-7');self.reject()
    def test_unknown_extra_wp(self): self.wp['unreviewed'] =b'hello';self.reject()
    def test_duplicate_canonical_route(self):
        self.man['articles'][1]['route']=self.man['articles'][0]['route'];self.reject()
    def test_report_wrong_source_order(self):
        self.report['articles'][4]['sources']=['source-b','source-a'];self.reject()
    def test_build_report_extra_duplicate(self):
        self.report['articles'].append(copy.deepcopy(self.report['articles'][0]));self.reject()
    def test_fake_qd_permission(self):self.man['independent_qd_pass']=True;self.reject()
    def test_fake_publish_permission(self):self.man['publication_authorized']=True;self.reject()
    def test_fake_merchant_approval(self):self.man['merchant_offer_verified']=True;self.reject()
    def test_fake_revenue(self):self.man['realized_net_revenue']=10;self.reject()
    def test_bad_head(self):self.man['branch_heads']['cluster-5']='a'*40;self.reject()
    def test_missing_source_token(self):
        self.materials['article-6']['body']=b'<p>No sources.</p>';self.reject()
    def test_html_source_not_complete(self):
        self.wp['article-9']=self.wp['article-9'].replace(b'</div>',b'',1);self.reject()
    def test_wp_provenance_missing(self):
        self.wp['article-2']=self.wp['article-2'].replace(b'application/ld+json',b'text/plain');self.reject()
    def test_wp_not_one_block(self):
        self.wp['article-2']=self.wp['article-2'].replace(b'<!-- wp:html -->',b'');self.reject()
    def test_post_not_free(self):
        self.wp['article-2']=self.wp['article-2'].replace(b'"isAccessibleForFree": true',b'"isAccessibleForFree": false');self.reject()
    def test_false_date_published(self):
        self.wp['article-2']=self.wp['article-2'].replace(b'"isAccessibleForFree": true',b'"isAccessibleForFree": true, "datePublished":"2026-11-08"');self.reject()
    def test_preview_not_draft(self):
        self.preview['article-8']=self.preview['article-8'].replace(b'Draft: not public',b'Public');self.reject()
    def test_html_injected_script_in_body(self):
        self.wp['article-3']=self.wp['article-3'].replace(b'</section>',b'<script>evil()</script></section>',1)
        self.reject()
    def test_cli_missing_checkout_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(gate.main(['--repo',tmp,'--report',tmp+'/out.json']),3)
            self.assertEqual(json.loads(Path(tmp,'out.json').read_text())['state'],gate.INVALID)


def changed_paragraph(n):
    def test(self):
        key=f'article-{n}'
        self.wp[key]=self.wp[key].replace(b'Safety warning for article',b'Safety omission for article')
        self.reject()
    return test

def changed_preview(n):
    def test(self):
        key=f'article-{n}'
        self.preview[key]=self.preview[key].replace(b'Contact a person',b'Contact nobody')
        self.reject()
    return test

def dropped_citation(n):
    def test(self):
        key=f'article-{n}'
        self.wp[key]=self.wp[key].replace(b'<sup class="pa-cite"><a href="#src-2" aria-label="Source">[number]</a></sup>',b'',1)
        self.reject()
    return test

def wrong_oid(n):
    def test(self):
        self.man['articles'][n-1]['body_oid']='0'*40
        self.reject()
    return test

for n in range(1,36):
    setattr(ParityTests,f'test_all35_wp_prose_{n:02}',changed_paragraph(n))
    setattr(ParityTests,f'test_all35_preview_prose_{n:02}',changed_preview(n))
    setattr(ParityTests,f'test_all35_missing_citation_{n:02}',dropped_citation(n))
    setattr(ParityTests,f'test_all35_source_identity_{n:02}',wrong_oid(n))

if __name__=='__main__':unittest.main()
