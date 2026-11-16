"""R410 35-article paired draft-export adversarial fixtures. Never genuine WordPress/QD proof."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import r410_full_slate_export_gate as gate
import r409_source_equivalence_gate as g

def fixture():
    ids=[]; groups=[]
    for i in range(203):
        u=f'https://www.ready.gov/asset-{i//2 if i<34 else i}'
        vs=[{'branch':'branch-0','source_blob':f'{i+1000:040x}','url':u}]
        if i<77: vs.append({'branch':'branch-1','source_blob':f'{i+2000:040x}','url':u})
        ids.append({'source_id':f'src-{i}','variants':vs})
    for j in range(17):
        groups.append({'url':f'https://www.ready.gov/asset-{j}','ids':[f'src-{2*j}',f'src-{2*j+1}'],'review_required':True})
    pins=[{'branch':f'branch-{i}','sha':f'{i+3000:040x}'} for i in range(9)]
    disputes=[{'source_id':f'scope-{i}','decision':'HUMAN_REVIEW_REQUIRED','selected_record':None,'variants':[{'branch':'branch-0'},{'branch':'branch-1'}]} for i in range(5)]
    forks=[{'path':f'f-{i}','decision':'HUMAN_REVIEW_REQUIRED','selected_sha':None,'variants':[{'branch':'branch-0'},{'branch':'branch-1'}],'requires_reading_depth_review':True,'requires_source_citation_review':True} for i in range(9)]
    d={'schema':1,'provenance':'ORIGINAL_UNSELECTED_GIT_SOURCE_INVENTORY','issue':136,
       'release_state':'DRAFT_HARD_HOLD','publication_approved':False,'qualified_safety_approved':False,'merchant_offer_verified':False,'automatic_variant_selection':False,
       'expected':dict(g.COUNTS),'observed':dict(g.COUNTS),
       'original_articles':[{'slug':f'guide-{i}'} for i in range(35)],
       'all_original_source_id_crosswalk':ids,'shared_exact_url_review_groups':groups,
       'source_evidence_disputes':disputes,'original_fork_disputes':forks,'branch_pins':pins}
    entries=[]; exports={}
    for i in range(35):
        slug=f'guide-{i}'; url=ids[i]['variants'][0]['url']; sid=f'src-{i}'
        entries.append({'slug':slug,'canonical_path':f'/preparedness/{slug}/','sources':[sid]})
        html=f'<article><h1>Verified only as synthetic source-citation fixture</h1><p>{"This is draft synthetic placeholder text for comparative source auditing only. "*7}</p><a data-source-id="{sid}" href="{url}">Original source</a></article>'
        exports[slug]=(html,html)
    m={'schema':1,'release_state':'DRAFT_HARD_HOLD','approved':False,'articles':entries}
    return d,m,exports

def run(d=None,m=None,ex=None):
    if d is None:d,m,ex=fixture()
    return gate.check(d,m,ex,test_only=True)

class Baseline(unittest.TestCase):
    def test_baseline(self):
        r=run(); self.assertTrue(r['integrity_ok'],r['errors']); self.assertEqual(r['articles_inspected'],35)
        self.assertFalse(r['eligible']);self.assertFalse(r['publication_approved']);self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
    def test_original_graph_synthetic_control(self):
        self.assertTrue(g.audit(fixture()[0],require_pin=False)['integrity_ok'])
    def test_original_git_pin_mandatory_production(self):
        d,m,ex=fixture();self.assertFalse(gate.check(d,m,ex)['integrity_ok'])
    def test_no_original_artifacts_cli_holds(self):
        p=subprocess.run([sys.executable,str(ROOT/'tools'/'r410_full_slate_export_gate.py'),'/no/original','/no/manifest','/no/exports'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2); self.assertFalse(json.loads(p.stdout)['eligible'])
    def test_manual_17_url_aliases_not_merged(self):
        d,m,ex=fixture();m['articles'][1]['sources']=['src-1'];self.assertTrue(run(d,m,ex)['integrity_ok'])
    def test_duplicate_html_attribute_rejected(self):
        d,m,e=fixture(); e['guide-0']=(e['guide-0'][0].replace('data-source-id="src-0"','data-source-id="src-0" data-source-id="src-0"'),e['guide-0'][1])
        self.assertFalse(run(d,m,e)['integrity_ok'])
    def test_missing_all_exports(self):
        d,m,ex=fixture();self.assertFalse(run(d,m,{})['integrity_ok'])

# Each mutation is a DISTINCT test against a fresh complete 35-article/203-ID/17-URL fixture.
ATTACKS=[]
for k,v in [('schema',4),('release_state','PASS'),('approved',True),('approved',None),('articles',None)]:
    ATTACKS.append((f'manifest_{k}_{str(v)}',lambda d,m,e,k=k,v=v:m.__setitem__(k,v)))
ATTACKS += [
('drop_article',lambda d,m,e:m['articles'].pop()),
('duplicate_article',lambda d,m,e:m['articles'][1].__setitem__('slug','guide-0')),
('foreign_article',lambda d,m,e:m['articles'][1].__setitem__('slug','injected')),
('unsafe_slug',lambda d,m,e:m['articles'][0].__setitem__('slug','../bad')),
('unsafe_route',lambda d,m,e:m['articles'][0].__setitem__('canonical_path','https://evil.invalid/guide-0')),
('route_query',lambda d,m,e:m['articles'][0].__setitem__('canonical_path','/preparedness/guide-0/?ref=bad')),
('route_traversal',lambda d,m,e:m['articles'][0].__setitem__('canonical_path','/preparedness/../guide-0/')),
('route_duplicate',lambda d,m,e:m['articles'][1].__setitem__('canonical_path','/preparedness/guide-0/')),
('missing_sources',lambda d,m,e:m['articles'][0].__setitem__('sources',[])),
('source_not_list',lambda d,m,e:m['articles'][0].__setitem__('sources','src-0')),
('source_duplicate',lambda d,m,e:m['articles'][0].__setitem__('sources',['src-0','src-0'])),
('unknown_source',lambda d,m,e:m['articles'][0].__setitem__('sources',['fake'])) ,
('no_html',lambda d,m,e:e.pop('guide-0')),
('extra_html',lambda d,m,e:e.__setitem__('guide-unknown',e['guide-0'])),
('html_not_pair',lambda d,m,e:e.__setitem__('guide-0',None)),
('html_one_side',lambda d,m,e:e.__setitem__('guide-0',[e['guide-0'][0]])),
('invalid_utf8',lambda d,m,e:e.__setitem__('guide-0',(b'\xff',e['guide-0'][1]))),
('empty_html',lambda d,m,e:e.__setitem__('guide-0',('',e['guide-0'][1]))),
('huge_html',lambda d,m,e:e.__setitem__('guide-0',('A'*1000001,e['guide-0'][1]))),
('no_heading',lambda d,m,e:e.__setitem__('guide-0',(e['guide-0'][0].replace('<h1>','<p>').replace('</h1>','</p>'),e['guide-0'][1]))),
('heading_drift',lambda d,m,e:e.__setitem__('guide-0',(e['guide-0'][0].replace('<h1>','<h2>').replace('</h1>','</h2>'),e['guide-0'][1]))),
('shortened_copy',lambda d,m,e:e.__setitem__('guide-0',(e['guide-0'][0].replace('This is draft synthetic placeholder text for comparative source auditing only. '*7,'short'),e['guide-0'][1]))),
('source_id_rewrite',lambda d,m,e:e.__setitem__('guide-0',(e['guide-0'][0].replace('data-source-id="src-0"','data-source-id="src-1"'),e['guide-0'][1]))),
('source_url_rewrite',lambda d,m,e:e.__setitem__('guide-0',(e['guide-0'][0].replace('asset-0','asset-3'),e['guide-0'][1]))),
('citation_removed',lambda d,m,e:e.__setitem__('guide-0',(e['guide-0'][0].replace('data-source-id="src-0"','data-unbound-id="src-0"'),e['guide-0'][1]))),
('citation_new_unknown',lambda d,m,e:e.__setitem__('guide-0',(e['guide-0'][0].replace('</article>','<a href="https://other.invalid/" data-source-id="bad">x</a></article>'),e['guide-0'][1]))),
('citation_reordered',lambda d,m,e:e.__setitem__('guide-0',(e['guide-0'][0].replace('</article>','<a data-source-id="src-0" href="https://www.ready.gov/asset-0">More</a></article>'),e['guide-0'][1]))),
('non_https_citation',lambda d,m,e:e.__setitem__('guide-0',(e['guide-0'][0].replace('https://www.ready.gov','http://www.ready.gov'),e['guide-0'][1]))),
('unbound_link',lambda d,m,e:e.__setitem__('guide-0',(e['guide-0'][0].replace('</article>','<a href="https://track.invalid">x</a></article>'),e['guide-0'][1]))),
('event_handler',lambda d,m,e:e.__setitem__('guide-0',(e['guide-0'][0].replace('<article>','<article onload="run()">'),e['guide-0'][1]))),
('inline_style',lambda d,m,e:e.__setitem__('guide-0',(e['guide-0'][0].replace('<article>','<article style="background:url(https://x.invalid)">'),e['guide-0'][1]))),
('external_src',lambda d,m,e:e.__setitem__('guide-0',(e['guide-0'][0].replace('<article>','<article src="https://track.invalid/">'),e['guide-0'][1]))),
('javascript_href',lambda d,m,e:e.__setitem__('guide-0',(e['guide-0'][0].replace('https://www.ready.gov/asset-0','javascript:alert(1)'),e['guide-0'][1]))),
('data_href',lambda d,m,e:e.__setitem__('guide-0',(e['guide-0'][0].replace('https://www.ready.gov/asset-0','data:text/html;base64,AA=='),e['guide-0'][1]))),
('original_article_removed',lambda d,m,e:d['original_articles'].pop()),
('unhashable_slug',lambda d,m,e:m['articles'][0].__setitem__('slug',[])),
('unhashable_source_id',lambda d,m,e:m['articles'][0].__setitem__('sources',[[]])),
('unhashable_canonical',lambda d,m,e:m['articles'][0].__setitem__('canonical_path',[])),
('wrong_original_graph_type',lambda d,m,e:d.__setitem__('original_articles',None)),
('wrong_source_graph_type',lambda d,m,e:d.__setitem__('all_original_source_id_crosswalk',None)),
('original_graph_url_rewritten',lambda d,m,e:d['all_original_source_id_crosswalk'][0]['variants'][0].__setitem__('url','https://else.invalid/')),
('original_source_dropped',lambda d,m,e:d['all_original_source_id_crosswalk'].pop()),
('original_branch_dropped',lambda d,m,e:d['branch_pins'].pop()),
('original_dispute_approved',lambda d,m,e:d['source_evidence_disputes'][0].__setitem__('decision','PASS')),
('original_fork_approved',lambda d,m,e:d['original_fork_disputes'][0].__setitem__('selected_sha','a'*40)),
]
for t in ['script','iframe','object','embed','form','input','button','textarea','select','style','link','svg','video','audio','img']:
    ATTACKS.append((f'active_element_{t}',lambda d,m,e,t=t:e.__setitem__('guide-0',(e['guide-0'][0].replace('<article>','<article><'+t+'>'),e['guide-0'][1]))))

class Attacks(unittest.TestCase): pass

def make_attack(name,edit):
    def test(self):
        d,m,e=fixture();edit(d,m,e);r=run(d,m,e)
        self.assertFalse(r['integrity_ok'],f'{name}: {r}')
        self.assertFalse(r['eligible'])
    test.__name__='test_reject_'+name
    return test
for n,f in ATTACKS:setattr(Attacks,'test_reject_'+n.replace('/','_').replace(' ','_'),make_attack(n,f))

if __name__=='__main__':unittest.main()
