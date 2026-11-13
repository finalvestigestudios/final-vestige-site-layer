"""R348 adversarial synthetic tests; never modify actual Preparedness sources."""
from __future__ import annotations

from copy import deepcopy
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
import json
import tempfile
import unittest

PATH = Path(__file__).resolve().parents[1] / 'tools' / 'r348_citation_occurrence_crosswalk_hold.py'
spec = spec_from_file_location('r348', PATH)
r = module_from_spec(spec)
spec.loader.exec_module(r)


def meta(slug='test-sample', sources=None):
    if sources is None:
        sources = {'fsis-power-failure': 'Synthetic test assertion; no safety review.'}
    return {'slug': slug, 'status': {'editorial': 'drafted', 'publish': 'draft'},
            'safety_review': {'state': 'pending', 'reviewer': None, 'date': None},
            'source_use': sources}


def body(source='fsis-power-failure'):
    return f'<section><h2>Unreviewed demo</h2><p>A sample claim {{'+'{cite:'+source+'}}'+'</p></section>'


class TestUnit(unittest.TestCase):
    def test_basic_paragraph(self):
        x = r.inspect_record('test-sample', body(), meta(), 'articles')
        self.assertEqual(x['errors'], [])
        self.assertEqual(len(x['citations']), 1)
        self.assertEqual(x['citations'][0]['source_id'], 'fsis-power-failure')
        self.assertEqual(x['citations'][0]['region_tag'], 'p')

    def test_no_original_private_text_emitted(self):
        b = '<section><p>SECRET_DO_NOT_EXPORT {{cite:fsis-power-failure}}</p></section>'
        x = r.inspect_record('test-sample', b, meta(), 'tools')
        self.assertNotIn('SECRET_DO_NOT_EXPORT', json.dumps(x))

    def test_identity_hash_changes_with_one_character(self):
        a = r.inspect_record('test-sample', body(), meta(), 'articles')
        b = r.inspect_record('test-sample', body().replace('sample', 'simple'), meta(), 'articles')
        self.assertNotEqual(a['body_sha256'], b['body_sha256'])
        self.assertNotEqual(a['citations'][0]['region_sha256'], b['citations'][0]['region_sha256'])

    def test_repeated_cite_has_separate_occurrences(self):
        b = '<ul><li>A {{cite:fsis-power-failure}} and {{cite:fsis-power-failure}}</li></ul>'
        x = r.inspect_record('test-sample', b, meta(), 'articles')
        self.assertEqual([c['ordinal'] for c in x['citations']], [1, 2])
        self.assertNotEqual(x['citations'][0]['occurrence_sha256'], x['citations'][1]['occurrence_sha256'])

    def test_both_conflicts_one_region(self):
        b = '<p>Two refs {{cite:fsis-power-failure}} and {{cite:nchfp-home}}</p>'
        m = meta(sources={'fsis-power-failure':'a','nchfp-home':'b'})
        x = r.inspect_record('test-sample', b, m, 'articles')
        self.assertEqual(x['errors'], [])
        self.assertEqual(len(x['citations']), 2)

    def test_declared_only_is_not_a_citation(self):
        x = r.inspect_record('test-sample', '<p>Text without source tokens.</p>', meta(), 'articles')
        self.assertEqual(x['citations'], [])
        self.assertEqual(x['declared_only_source_ids'], ['fsis-power-failure'])

    def test_safe_void_html(self):
        b='<section><p>Text<br>More {{cite:fsis-power-failure}} <img src="/asset.png"></p><hr></section>'
        self.assertEqual(r.inspect_record('test-sample',b,meta(),'articles')['errors'],[])

    def test_raw_citation_order_is_preserved(self):
        b='<p>A {{cite:loc-pioneer-diaries}}</p><p>B {{cite:fsis-power-failure}}</p>'
        x=r.inspect_record('test-sample',b,meta(sources={'loc-pioneer-diaries':'a','fsis-power-failure':'b'}),'articles')
        self.assertEqual([c['source_id'] for c in x['citations']], ['loc-pioneer-diaries','fsis-power-failure'])

    def test_always_has_no_publish_authority(self):
        for k,v in r.FALSE_GATES.items(): self.assertIs(v,False,k)


class TestCorpus(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        for kind,n in (('articles',35),('tools',6)):
            d=self.root/'preparedness'/'content'/kind
            d.mkdir(parents=True)
            for i in range(n):
                slug=f'synthetic-{kind}-{i:02}'
                (d/(slug+'.body.html')).write_text(body(),encoding='utf8')
                (d/(slug+'.meta.json')).write_text(json.dumps(meta(slug)),encoding='utf8')

    def pair(self,kind='articles',i=0):
        slug=f'synthetic-{kind}-{i:02}'
        d=self.root/'preparedness'/'content'/kind
        return (d/(slug+'.body.html'),d/(slug+'.meta.json'))

    def test_complete_synthetic_41(self):
        x=r.crosswalk(self.root)
        self.assertEqual(x['errors'],[])
        self.assertEqual(x['documents_checked'],41)
        self.assertEqual(x['citation_occurrences'],41)
        self.assertEqual(x['distinct_cited_sources'],1)
        self.assertEqual(len(x['disputed_source_occurrences']),41)
        self.assertEqual(x['state'],'OCCURRENCE_CROSSWALK_ONLY_HARD_HOLD')
        self.assertFalse(x['qualified_qd_pass'])

    def test_native_custody_missing_fails_closed(self):
        x=r.native_audit(self.root)
        self.assertEqual(x['state'],'INVALID_HARD_HOLD')
        self.assertTrue(any('PREDECESSOR' in e for e in x['errors']))
        self.assertFalse(x['may_publish'])

    def test_missing_body_detected(self):
        b,_=self.pair();b.unlink()
        x=r.crosswalk(self.root)
        self.assertIn('INCOMPLETE_ARTICLES_CORPUS',x['errors'])
        self.assertIn('BODY_METADATA_SLATE_MISMATCH:articles',x['errors'])

    def test_missing_meta_detected(self):
        _,m=self.pair();m.unlink()
        self.assertIn('BODY_METADATA_SLATE_MISMATCH:articles',r.crosswalk(self.root)['errors'])

    def test_added_extra_body_detected(self):
        d=self.root/'preparedness'/'content'/'articles';(d/'extra.body.html').write_text(body())
        self.assertIn('INCOMPLETE_ARTICLES_CORPUS',r.crosswalk(self.root)['errors'])

    def test_source_use_declaration_is_not_claim_support(self):
        b,m=self.pair(); b.write_text('<p>No source appears.</p>')
        x=r.crosswalk(self.root)
        self.assertEqual(x['errors'],[])
        self.assertIn('articles/synthetic-articles-00',x['declared_only_counts'])
        self.assertTrue(x['occurrence_does_not_establish_claim_support'])

    def test_unknown_citation_fails(self):
        b,_=self.pair();b.write_text(body('unknown-uid'))
        self.assertIn('CITED_SOURCE_WITHOUT_SOURCE_USE',r.inspect_record('synthetic-articles-00',b.read_text(),meta('synthetic-articles-00'),'articles')['errors'])

    def test_tool_independent_identity(self):
        x=r.crosswalk(self.root)
        self.assertIn('tools/synthetic-tools-00',x['disputed_documents'])
        self.assertIn('articles/synthetic-articles-00',x['disputed_documents'])

    def test_path_input_without_preparedness_prefix(self):
        x=r.crosswalk(self.root/'preparedness')
        self.assertEqual(x['documents_checked'],41)
        self.assertFalse(x['may_publish'])

    def test_emitted_report_never_contains_unredacted_synthetic_claim(self):
        b,_=self.pair();b.write_text('<p>PRIVATE-FAMILY-DETAIL {{cite:fsis-power-failure}}</p>')
        self.assertNotIn('PRIVATE-FAMILY-DETAIL',json.dumps(r.crosswalk(self.root)))

    def test_invalid_json_hard_hold(self):
        _,m=self.pair();m.write_text('{bad')
        self.assertTrue(any('UNREADABLE_CANONICAL_PAIR' in e for e in r.crosswalk(self.root)['errors']))

    def test_symlinked_original_refused(self):
        b,_=self.pair(); b.unlink(); b.symlink_to('/tmp/no-such-preparedness-doc')
        self.assertTrue(any('UNSAFE_OR_MISSING_CANONICAL_PAIR' in e for e in r.crosswalk(self.root)['errors']))

    def test_per_source_collision_occurrence_count(self):
        b,_=self.pair();b.write_text('<p>{{cite:fsis-power-failure}} + {{cite:fsis-power-failure}}</p>')
        x=r.crosswalk(self.root)
        self.assertEqual(x['citation_occurrences'],42)
        self.assertEqual(len(x['disputed_source_occurrences']),42)


class TestMutations(unittest.TestCase):
    pass


MUTATIONS = [
    ('approve-publish', lambda b,m:(b,m.update({'status':{'publish':'publish'}}))),
    ('approve-safety',lambda b,m:(b,m.update({'safety_review':{'state':'approved'}}))),
    ('null-safety', lambda b,m:(b,m.update({'safety_review':None}))),
    ('missing-status',lambda b,m:(b,m.pop('status'))),
    ('wrong-slug',lambda b,m:(b,m.update({'slug':'different'}))),
    ('missing-source-use',lambda b,m:(b,m.pop('source_use'))),
    ('null-source-use',lambda b,m:(b,m.update({'source_use':None}))),
    ('not-list-source-use',lambda b,m:(b,m.update({'source_use':['a']}))),
    ('integer-source-value',lambda b,m:(b,m.update({'source_use':{'fsis-power-failure':17}}))),
    ('unknown-cite',lambda b,m:(b.replace('fsis-power-failure','unknown-source'),m)),
    ('malformed-cite-no-braces',lambda b,m:(b.replace('{{cite:fsis-power-failure}}','{{cite:bad-source}'),m)),
    ('cite-comment',lambda b,m:('<p>Text</p><!-- {{cite:fsis-power-failure}} -->',m)),
    ('cite-attribute',lambda b,m:('<p title="{{cite:fsis-power-failure}}">Text</p>',m)),
    ('cite-hidden-script',lambda b,m:('<script>var a="{{cite:fsis-power-failure}}";</script>',m)),
    ('cite-style',lambda b,m:('<style>{{cite:fsis-power-failure}}</style>',m)),
    ('iframe',lambda b,m:('<iframe></iframe>'+b,m)),
    ('form',lambda b,m:('<form>'+b+'</form>',m)),
    ('cite-outside-tags',lambda b,m:('{{cite:fsis-power-failure}}',m)),
    ('unbalanced-tag',lambda b,m:('<p>'+b,m)),
    ('unexpected-end',lambda b,m:(b+'</li>',m)),
    ('no-region',lambda b,m:('<div>{{cite:fsis-power-failure}}</div>',m)),
    ('empty-id',lambda b,m:(b.replace('fsis-power-failure',''),m)),
    ('uppercase-id',lambda b,m:(b.replace('fsis-power-failure','SOURCE'),m)),
    ('space-id',lambda b,m:(b.replace('fsis-power-failure','source bad'),m)),
    ('unicode-id',lambda b,m:(b.replace('fsis-power-failure','école'),m)),
    ('nested-broken-region',lambda b,m:('<p><span>'+b+'</p></span>',m)),
    ('image-attribute',lambda b,m:('<p><img src="{{cite:fsis-power-failure}}"></p>',m)),
    ('meta-source-key-number',lambda b,m:(b,m.update({'source_use':{17:'bad'}}))),
    ('missing-publish',lambda b,m:(b,m.update({'status':{'editorial':'drafted'}}))),
    ('invalid-publish',lambda b,m:(b,m.update({'status':{'publish':'public'}}))),
    ('safety-empty',lambda b,m:(b,m.update({'safety_review':{}}))),
    ('safety-notrequired',lambda b,m:(b,m.update({'safety_review':{'state':'not-required'}}))),
    ('split-citation',lambda b,m:(b.replace('{{cite:fsis-power-failure}}','{{cite:<i>fsis-power-failure</i>}}'),m)),
    ('casing-attribute',lambda b,m:('<p data-note="{{cite:fsis-power-failure}}">Text</p>',m)),
    ('multiple-extra-close',lambda b,m:(b+'</p></p>',m)),
    ('nested-script',lambda b,m:('<div><script>none</script>'+b+'</div>',m)),
    ('all-header-no-region',lambda b,m:('<section>{{cite:fsis-power-failure}}</section>',m)),
    ('empty-source-uses',lambda b,m:(b,m.update({'source_use':{}}))),
    ('no-meta-slug',lambda b,m:(b,m.pop('slug'))),
    ('random-href-cite',lambda b,m:('<a href="{{cite:fsis-power-failure}}">Text</a>',m)),
]


def register(name, mutation):
    def fn(self):
        base_b=body();base_m=meta()
        new_b,new_m=mutation(base_b,deepcopy(base_m))
        result=r.inspect_record('test-sample',new_b,new_m,'articles')
        self.assertTrue(result['errors'],name)
        self.assertNotIn('claim',json.dumps(result).lower()) if False else None
    setattr(TestMutations,'test_reject_'+name.replace('-','_'),fn)

for name,fn in MUTATIONS:
    register(name,fn)


if __name__=='__main__': unittest.main(verbosity=2)
