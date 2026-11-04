"""R128 isolated adversarial fixtures: no writes to Preparedness source tree."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
import unittest

path=Path(__file__).resolve().parents[1]/'tools/r128_hazard_citation_triage.py'
spec=importlib.util.spec_from_file_location('r128gate',path)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

class TestTriage(unittest.TestCase):
    def setUp(self):
        self.meta={'slug':'household-emergency-plan','status':{'publish':'draft'},
                   'safety_review':{'state':'pending'},
                   'source_use':{'official-a':'Agency scope.','official-b':'Other source scope.'}}
        self.body='<p>Generator and carbon monoxide danger.{{cite:official-a}}</p>'
    def test_good(self):
        x=gate.triage_article('household-emergency-plan',self.body,self.meta)
        self.assertEqual(x['citation_occurrences'],1)
        self.assertEqual(x['uncited_hazard_keyword_blocks'],0)
        self.assertTrue(x['hazard_keyword_blocks'][0]['source_ids'])
    def test_uncited_keyword_is_review_not_approval(self):
        x=gate.triage_article('household-emergency-plan','<p>Generator info.</p>'+self.body,self.meta)
        self.assertEqual(x['uncited_hazard_keyword_blocks'],1)
        self.assertEqual(x['hazard_keyword_blocks'][0]['review_state'],'OPEN_HUMAN_SOURCE_AND_SAFETY_REVIEW')
    def test_duplicate_keys_rejected(self):
        with self.assertRaises(gate.Hold):gate.distinct_object_pairs([('a',1),('a',2)])
    def test_blob(self):
        self.assertEqual(gate.gitblob(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_repeated_occurrences(self):
        self.assertEqual(gate.triage_article('household-emergency-plan',self.body*4,self.meta)['citation_occurrences'],4)
    def test_historical_metadata_is_not_QD(self):
        self.meta['safety_review']['state']='approved'
        self.assertNotIn('independent_QD_PASS',gate.triage_article('household-emergency-plan',self.body,self.meta))

class TestRoster(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.article_dir=self.root/'preparedness/content/articles'
        self.article_dir.mkdir(parents=True)
        self.slugs=['household-emergency-plan','three-day-kit','go-bags','preparedness-real-households']+[f'page-{i}' for i in range(31)]
        self.tax={'base_path':'/preparedness/','slate':[{'slug':slug,'gate':True} for slug in self.slugs]}
        self.taxpath=self.root/'preparedness/taxonomy.json'
        self.taxpath.write_text(json.dumps(self.tax),encoding='utf-8')
        for slug in self.slugs:
            (self.article_dir/f'{slug}.meta.json').write_text(json.dumps({'slug':slug,
               'status':{'publish':'draft'},'safety_review':{'state':'pending'},
               'source_use':{'official-a':'Full agency reading scope.'}}),encoding='utf-8')
            (self.article_dir/f'{slug}.body.html').write_text('<p>Generator.{{cite:official-a}}</p>',encoding='utf-8')
    def tearDown(self):self.temp.cleanup()
    def test_roster_holds(self):
        x=gate.audit(self.root,expected_citations=35)
        self.assertEqual(x['article_count'],35)
        self.assertEqual(x['visible_citation_occurrences'],35)
        self.assertEqual(x['status'],'HOLD_HUMAN_REVIEW')
        self.assertFalse(x['may_publish'])
        self.assertFalse(x['independent_QD_PASS'])
    def test_total_change_rejected(self):
        with self.assertRaises(gate.Hold):gate.audit(self.root,expected_citations=2000)
    def test_no_unverified_git_head(self):
        with self.assertRaises(gate.Hold):gate.audit(self.root,expected_citations=35,verify_ref=True)
    def test_dirty_checkout_rejected(self):
        with patch.object(gate.subprocess, 'check_output', side_effect=[gate.RC_SHA+'\n',' M preparedness/content/articles/page-1.body.html\n']):
            with self.assertRaisesRegex(gate.Hold, 'DIRTY_CANDIDATE_WORKTREE'):
                gate.audit(self.root,expected_citations=35,verify_ref=True)
    def test_clean_checkout_with_matching_sha(self):
        with patch.object(gate.subprocess, 'check_output', side_effect=[gate.RC_SHA+'\n','']):
            self.assertEqual(gate.audit(self.root,expected_citations=35,verify_ref=True)['article_count'],35)
    def test_unterminated_citation(self):
        p=self.article_dir/'page-0.body.html'
        p.write_text('<p>Generator.{{cite:official-a</p>')
        with self.assertRaisesRegex(gate.Hold, 'UNTERMINATED_CITATION'):
            gate.audit(self.root,expected_citations=35)
    def test_missing_file(self):
        (self.article_dir/f'{self.slugs[0]}.body.html').unlink()
        with self.assertRaises(OSError):gate.audit(self.root,expected_citations=35)

def hidden_case(markup):
    def check(self):
        with self.assertRaises(gate.Hold):gate.triage_article('household-emergency-plan',markup,self.meta)
    return check
for i,x in enumerate([
 '<p title="{{cite:official-a}}">generator</p>',
 '<!-- {{cite:official-a}} --><p>generator</p>',
 '<p hidden>generator{{cite:official-a}}</p>',
 '<p aria-hidden="true">generator{{cite:official-a}}</p>',
 '<p style="display: none">generator{{cite:official-a}}</p>',
 '<p style="visibility:hidden">generator{{cite:official-a}}</p>',
 '<script>{{cite:official-a}}</script>',
 '<style>{{cite:official-a}}</style>',
 '<template>{{cite:official-a}}</template>',
 '<noscript>{{cite:official-a}}</noscript>',
 '<div inert>generator{{cite:official-a}}</div>',
 '<p>Generator{{cite:official-a}}</p><!--{{cite:official-b}}-->',
 '<p>Generator{{cite:official-a}}</p><script>{{cite:official-b}}</script>',
 '<p>{{cite:Official-a}}</p>',
 '<p>{{cite:official_a}}</p>',
 '<p>{{cite:}}</p>',
 '<p>{{cite:official-a }}</p>',
]):setattr(TestTriage,f'test_hidden_or_malformed_{i:02d}',hidden_case(x))

def meta_case(mutation):
    def check(self):
        meta=copy.deepcopy(self.meta);mutation(meta)
        with self.assertRaises(gate.Hold):gate.triage_article('household-emergency-plan',self.body,meta)
    return check
for i,fn in enumerate([
 lambda m:m.update(slug='other'),
 lambda m:m['status'].update(publish='publish'),
 lambda m:m.pop('status'),
 lambda m:m['safety_review'].update(state='safe'),
 lambda m:m.pop('safety_review'),
 lambda m:m.pop('source_use'),
 lambda m:m.update(source_use={}),
 lambda m:m['source_use'].update({'official-a':' '}),
 lambda m:m['source_use'].update({'official-a':None}),
 lambda m:m.update(source_use={'other':'different interpretation'}),
]):setattr(TestTriage,f'test_meta_mutation_{i:02d}',meta_case(fn))

def keyword_case(category,word):
    def check(self):self.assertIsNotNone(gate.HAZARDS[category].search(word))
    return check
for category,words in {
 'medical_cold_chain':['medicine','refrigerated','insulin','dialysis','prescription'],
 'combustion_co':['generator','gas grill','carbon monoxide','fuel-burning','charcoal'],
 'food_preservation':['pressure canning','botulism','jerky','dehydration','curing meat'],
 'water_safety':['water purification','boil-water','bleach','disinfection','potable'],
 'electric_fire':['fire escape','electrical','main breaker','smoke alarm','fire extinguisher'],
}.items():
    for i,word in enumerate(words):setattr(TestTriage,f'test_hazard_{category}_{i:02d}',keyword_case(category,word))

def block_case(tag):
    def check(self):
        x=gate.triage_article('household-emergency-plan',f'<{tag}>Generator{{{{cite:official-a}}}}</{tag}>',self.meta)
        self.assertEqual(len(x['hazard_keyword_blocks']),1)
    return check
for tag in ('p','li','td','h2','blockquote','figcaption'):
    setattr(TestTriage,f'test_block_{tag}',block_case(tag))

def roster_case(mutate):
    def check(self):
        tax=copy.deepcopy(self.tax);mutate(tax)
        self.taxpath.write_text(json.dumps(tax))
        with self.assertRaises(gate.Hold):gate.audit(self.root,expected_citations=35)
    return check
for i,fn in enumerate([
 lambda t:t['slate'].pop(),
 lambda t:t['slate'].__setitem__(1,dict(t['slate'][0])),
 lambda t:t.update(base_path='/different/'),
 lambda t:t['slate'][0].update(gate=False),
 lambda t:t['slate'][4].update(slug='../wrong'),
]):setattr(TestRoster,f'test_roster_mutation_{i:02d}',roster_case(fn))

if __name__=='__main__':unittest.main()
