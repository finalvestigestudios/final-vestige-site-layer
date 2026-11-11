"""Synthetic adversarial tests. No production corpus, browser, or source approval."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import unittest

P=Path(__file__).resolve().parents[1]/'tools'/'r298_export_content_integrity_hold.py'
spec=importlib.util.spec_from_file_location('r298',P)
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)

def fixture():
    # Synthetic long-form reading body; 35 articles with independent source IDs,
    # stable normalizations and complete WordPress draft wrapper.
    custody={'state':'DRAFT_HARD_HOLD','publication_authorized':False,'independent_qd_pass':False,
             'human_source_approved':False,'medical_safety_verified':False,
             'artifact_count':35,'export_target_count_with_six_tools':41,'articles':[]}
    report={'articles':[],'release_evidence':{'state':'HOLD','independent_qa_verified':False,
            'wordpress_publication_performed':False}}
    originals,wp={},{}
    for i in range(1,36):
        slug=f'guide-{i:02d}'; sec='start-here'
        para=' '.join(f'item{i} text{j} passage{j} sourceverbatim' for j in range(60))
        raw=f'<section><h2>Source narrative {i}</h2><p>{para}</p><p>Keep the evidence intact {{'+'{cite:source-abc}}'+'</p></section>'
        rawb=raw.encode()
        path=f'preparedness/content/articles/{slug}.body.html'
        originals[path]=rawb
        wp[f'preparedness/build/wp/{slug}.html']=(
            '<!-- wp:html -->\n<div class="pa pa-article" data-slug="'+slug+'">'
            '<span>Independent safety/source and QD verification pending</span>'
            '<div class="pa-body">'+raw.replace('{{cite:source-abc}}','<sup>[1]</sup>')+'</div></div>\n<!-- /wp:html -->\n'
        ).encode()
        custody['articles'].append({'n':i,'slug':slug,'section':sec,
            'route':f'/preparedness/{sec}/{slug}/','body_oid':g.blob_oid(rawb),
            'body_bytes':len(rawb)})
        report['articles'].append({'slug':slug,'canonical':f'https://finalvestige.com/preparedness/{sec}/{slug}/'})
    tool_receipt={'tools':[{'slug':f'tool-{i}','status':'draft','file_sha256':'a'*64,'review_only':True} for i in range(6)]}
    return custody,report,originals,wp,tool_receipt

BASE=fixture()

def verify_change(fn=None):
    c,r,o,w,t=copy.deepcopy(BASE)
    if fn:fn(c,r,o,w,t)
    return g.inspect(c,r,o,w,t)

class ExportGuardTests(unittest.TestCase):
    def test_control(self):
        a=verify_change()
        self.assertEqual(a['state'],'DRAFT_HARD_HOLD',a['errors'])
        self.assertEqual(a['article_entries_reviewed'],35)
        self.assertEqual(a['errors'],[])
        self.assertTrue(all(x['unchanged_word_window_fraction']>=.94 for x in a['article_evidence']))
    def test_never_grants_publication(self):
        a=verify_change()
        for k in ('all_41_exports_verified','publication_authorized','independent_qd_pass','medical_safety_verified','merchant_approved','net_revenue_verified'):
            self.assertIs(a[k],False)
    def test_empty(self):self.assertEqual(g.window_coverage([],[]),0)
    def test_coverage(self):
        self.assertEqual(g.window_coverage(list('abcdefghij'),list('abcdefghij')),1.0)
        self.assertLess(g.window_coverage(list('abcdefghij'),list('abcxj')),1.0)
    def test_narrative(self):
        self.assertEqual(g.words('<p>Hello {{cite:a}} &amp; goodbye</p>'),['hello','goodbye'])
        self.assertEqual(g.words('<script>evil</script><p>good</p>'),['good'])
        self.assertEqual(g.words('<div class="pa-body"><p>good</p></div><p>bad</p>',target=True),['good'])

# Independent one-factor adversarial transformations; no source approval granted.
MUTATIONS={
    'custody_state':lambda c,r,o,w,t:c.update(state='APPROVED'),
    'custody_pub':lambda c,r,o,w,t:c.update(publication_authorized=True),
    'custody_qd':lambda c,r,o,w,t:c.update(independent_qd_pass=True),
    'custody_human':lambda c,r,o,w,t:c.update(human_source_approved=True),
    'custody_medical':lambda c,r,o,w,t:c.update(medical_safety_verified=True),
    'custody_count':lambda c,r,o,w,t:c.update(artifact_count=34),
    'custody_exports':lambda c,r,o,w,t:c.update(export_target_count_with_six_tools=35),
    'missing_custody_article':lambda c,r,o,w,t:c['articles'].pop(),
    'duplicate_custody_article':lambda c,r,o,w,t:c['articles'][2].update(slug=c['articles'][1]['slug']),
    'wrong_custody_order':lambda c,r,o,w,t:c['articles'][1].update(n=1),
    'duplicate_custody_url':lambda c,r,o,w,t:c['articles'][2].update(route=c['articles'][1]['route']),
    'wrong_custody_url':lambda c,r,o,w,t:c['articles'][2].update(route='/different/'),
    'missing_build_entry':lambda c,r,o,w,t:r['articles'].pop(),
    'duplicate_build_slug':lambda c,r,o,w,t:r['articles'][2].update(slug=r['articles'][1]['slug']),
    'wrong_build_slug':lambda c,r,o,w,t:r['articles'][2].update(slug='other'),
    'wrong_canonical':lambda c,r,o,w,t:r['articles'][1].update(canonical='https://example.com/'),
    'missing_build_release':lambda c,r,o,w,t:r.pop('release_evidence'),
    'claimed_qd':lambda c,r,o,w,t:r['release_evidence'].update(independent_qa_verified=True),
    'claimed_publication':lambda c,r,o,w,t:r['release_evidence'].update(wordpress_publication_performed=True),
    'wrong_release_state':lambda c,r,o,w,t:r['release_evidence'].update(state='GREEN'),
    'missing_original':lambda c,r,o,w,t:o.pop(next(iter(o))),
    'missing_wp_draft':lambda c,r,o,w,t:w.pop(next(iter(w))),
    'changed_original':lambda c,r,o,w,t:o.__setitem__(next(iter(o)),b'<p>fake</p>'),
    'truncated_original':lambda c,r,o,w,t:o.__setitem__(next(iter(o)),o[next(iter(o))][:20]),
    'wrong_original_type':lambda c,r,o,w,t:o.__setitem__(next(iter(o)),'not bytes'),
    'wrong_wp_type':lambda c,r,o,w,t:w.__setitem__(next(iter(w)),'not bytes'),
    'wrong_wp_encoding':lambda c,r,o,w,t:w.__setitem__(next(iter(w)),b'\xff\xfe'),
    'wrong_wrapper':lambda c,r,o,w,t:w.__setitem__(next(iter(w)),w[next(iter(w))].replace(b'<!-- wp:html -->',b'<!-- wp:paragraph -->')),
    'wrong_article':lambda c,r,o,w,t:w.__setitem__(next(iter(w)),w[next(iter(w))].replace(b'data-slug="guide-01"',b'data-slug="different"')),
    'lost_status':lambda c,r,o,w,t:w.__setitem__(next(iter(w)),w[next(iter(w))].replace(b'Independent safety/source and QD verification pending',b'SAFE TO PUBLISH')),
    'lost_narrative':lambda c,r,o,w,t:w.__setitem__(next(iter(w)),w[next(iter(w))].replace(b'sourceverbatim',b'REDACTED')),
    'lost_long_suffix':lambda c,r,o,w,t:w.__setitem__(next(iter(w)),w[next(iter(w))].replace(b'item1 text59 passage59 sourceverbatim',b'')),
    'missing_tool_receipt':lambda c,r,o,w,t:t.clear(),
    'missing_tool_row':lambda c,r,o,w,t:t['tools'].pop(),
    'duplicate_tool':lambda c,r,o,w,t:t['tools'][2].update(slug=t['tools'][1]['slug']),
    'published_tool':lambda c,r,o,w,t:t['tools'][2].update(status='published'),
    'tool_without_checksum':lambda c,r,o,w,t:t['tools'][2].update(file_sha256=''),
    'tool_without_review_only':lambda c,r,o,w,t:t['tools'][2].update(review_only=False),
}
for name,mutation in MUTATIONS.items():
    def test(self,m=mutation,name=name):
        a=verify_change(m)
        self.assertEqual(a['state'],'INVALID_HARD_HOLD',(name,a['errors']))
        self.assertTrue(a['errors'])
        self.assertIs(a['publication_authorized'],False)
    setattr(ExportGuardTests,'test_mutation_'+name,test)

# Reject repeated drift of many different article indices, not just first article.
for idx in range(1,36):
    def test(self,index=idx):
        def mutate(c,r,o,w,t):
            slug=f'guide-{index:02d}'
            path=f'preparedness/build/wp/{slug}.html'
            w[path]=w[path].replace(b'sourceverbatim',b'OMITTED')
        a=verify_change(mutate)
        self.assertIn('READING_DEPTH_OR_PASSAGE_LOSS:guide-'+str(index).zfill(2),a['errors'])
    setattr(ExportGuardTests,'test_narrative_drift_index_'+str(idx),test)

if __name__=='__main__': unittest.main()
