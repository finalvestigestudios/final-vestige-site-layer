"""Synthetic adversarial tests; these do NOT substitute for 35 authentic originals."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / 'tools' / 'r379_all_article_source_scope_gate.py'
sp = importlib.util.spec_from_file_location('r379gate', TOOL)
gate = importlib.util.module_from_spec(sp)
sp.loader.exec_module(gate)

BRANCHES = ['claude/prep-start-bbfeb8','claude/prep-food-ccdc55',
            'claude/prep-health-837444','claude/prep-hist-field-9db767',
            'claude/prep-hist-food-b81f19','claude/prep-hist-home-0e0e38',
            'claude/prep-shelter-5e1e0e','claude/prep-shelter-continuation',
            'claude/prep-shelter-followup-evidence']
SHELTER = ['family-communication-plan','home-fire-escape-plan',
           'outage-heat-cold-generators','shelter-or-evacuate']
SLUGS = SHELTER + [f'original-safe-article-{i:02d}' for i in range(1,32)]
TEXT = 'A unique evidence-grounded reading passage with explanation and caveats. ' * 130


def fixture():
    store = {}
    def put(raw):
        raw = raw if isinstance(raw, bytes) else raw.encode()
        sha = gate.git_blob(raw)
        store[sha] = raw
        return {'sha':sha, 'size':len(raw)}
    pins = [{'branch':b, 'sha':f'{i+1:040x}'} for i,b in enumerate(BRANCHES)]
    items = []
    origins = {}
    def add(path, specs):
        variants = [{'branch':branch, **put(value)} for branch,value in specs]
        items.append({'path':path, 'variants':variants,
                      'decision':'REVIEW_REQUIRED' if len({v['sha'] for v in variants})>1 else 'IDENTICAL_OR_SINGLE',
                      'selected_sha':None})
    for i,slug in enumerate(SLUGS):
        is_shelter = slug in SHELTER
        origins[slug] = 'shelter' if is_shelter else 'start'
        branches = [BRANCHES[6], BRANCHES[8]] if is_shelter else [BRANCHES[0]]
        bodies = []
        metas = []
        for j,branch in enumerate(branches):
            body = f'<p>{TEXT} version-{j} ' + '{{cite:local-ref}} {{cite:base-ref}} {{link:' + slug + '}}</p>'
            meta = {'n':i+1,'slug':slug,'section':'family-communication' if is_shelter else 'start-here',
                    'status':{'editorial':'drafted','publish':'draft'},
                    'safety_review':{'state':'pending','reviewer':None,'date':None},
                    'source_use':{'local-ref':'Exact local reading scope','base-ref':'Original BASE reading scope'}, 'variant_review_marker':j}
            bodies.append((branch,body))
            metas.append((branch,json.dumps(meta,sort_keys=True)))
        add(f'preparedness/content/articles/{slug}.body.html',bodies)
        add(f'preparedness/content/articles/{slug}.meta.json',metas)
    def fragment(support='Original local claim scope.'):
        return json.dumps({'sources':[{'id':'local-ref','url':'https://example.org/source',
            'supports': support,'human_link_check':False,'verified_on':'2026-10-30'}]},sort_keys=True)
    for orig, branch in [('start',BRANCHES[0]),('food',BRANCHES[1]),('health',BRANCHES[2]),
                         ('hist-field',BRANCHES[3]),('hist-food',BRANCHES[4]),('hist-home',BRANCHES[5])]:
        add(f'preparedness/sources/fragments/{orig}.json',[(branch,fragment())])
    add('preparedness/sources/fragments/shelter.json',[(BRANCHES[6],fragment('First Shelter scope')),
          (BRANCHES[8],fragment('Second Shelter scope'))])
    return ({'schema_version':1,'repository':gate.REPO,'release_state':'DRAFT_HARD_HOLD',
             'branch_pins':pins,'article_count':35,'conflict_count':9,'objects':items},
            {'article_origins':origins},
            {'sources':[{'id':'base-ref','url':'https://example.org/base','supports':'Base source claim',
                         'verified_on':'2026-10-29','human_link_check':False}]},store)


def find(manifest, slug, typ):
    return next(o for o in manifest['objects'] if o['path'].endswith('/'+slug+'.'+typ))


def altered(m, store, slug, typ, fn, which=0):
    item = find(m,slug,typ)['variants'][which]
    old = store[item['sha']]
    if typ == 'meta.json':
        raw = json.dumps(fn(json.loads(old)),sort_keys=True).encode()
    else:
        raw = fn(old.decode()).encode()
    new_sha = gate.git_blob(raw)
    item['sha'],item['size'] = new_sha,len(raw)
    store[new_sha] = raw
    return new_sha


def report(docs):
    m,x,reg,store=docs
    return gate.evaluate(m,x,reg,lambda sha:store[sha])


class R379Tests(unittest.TestCase):
    def setUp(self):
        self.docs=fixture()

    def assert_bad(self,needle):
        result=report(self.docs)
        self.assertEqual(result['status'],'INVALID_HARD_HOLD')
        self.assertTrue(any(needle in e for e in result['errors']),result['errors'])
        self.assertFalse(result['publication_approved'])

    def test_full_synthetic_baseline_is_custody_only(self):
        r=report(self.docs)
        self.assertEqual(r['status'],'CUSTODY_COMPLETE_REVIEW_REQUIRED',r['errors'])
        self.assertEqual(r['article_count'],35)
        self.assertEqual(r['article_variants'],39)
        self.assertEqual(r['object_conflicts'],9)
        self.assertFalse(r['publication_approved'])
        self.assertFalse(r['qualified_safety_approved'])
        self.assertIsNone(r['verified_net_revenue'])
        self.assertEqual(r['canonical_duplicate_groups'],[])
        self.assertTrue(all(a['unchecked_human_source_ids'] for a in r['per_variant']))

    def test_forged_publication_manifest_rejected(self):
        self.docs[0]['approval']=True;self.assert_bad('release hold')
    def test_missing_branch_pin_rejected(self):
        self.docs[0]['branch_pins'].pop();self.assert_bad('nine immutable')
    def test_malformed_branch_sha_rejected(self):
        self.docs[0]['branch_pins'][0]['sha']='bogus';self.assert_bad('malformed contributor')
    def test_auto_selected_sha_rejected(self):
        self.docs[0]['objects'][0]['selected_sha']='a'*40;self.assert_bad('unreviewed version')
    def test_hiding_conflict_rejected(self):
        find(self.docs[0],SHELTER[0],'body.html')['decision']='IDENTICAL_OR_SINGLE';self.assert_bad('conflict hidden')
    def test_changed_conflict_count_rejected(self):
        self.docs[0]['conflict_count']=8;self.assert_bad('nine unresolved')
    def test_missing_body_rejected(self):
        obj=find(self.docs[0],SLUGS[8],'body.html');self.docs[0]['objects'].remove(obj);self.assert_bad('35-body')
    def test_unpaired_variant_rejected(self):
        find(self.docs[0],SHELTER[0],'meta.json')['variants'].pop();self.assert_bad('unpaired article')
    def test_duplicate_object_path_rejected(self):
        self.docs[0]['objects'].append(copy.deepcopy(self.docs[0]['objects'][0]));self.assert_bad('duplicate object path')
    def test_new_untrusted_branch_variant_rejected(self):
        find(self.docs[0],SLUGS[8],'body.html')['variants'][0]['branch']='untrusted';self.assert_bad('unpinned branch')
    def test_original_blob_mutation_rejected(self):
        store=self.docs[3];k=next(iter(store));store[k]=b'tampered';self.assert_bad('article original Git blob unreadable')
    def test_tampered_metadata_source_use_rejected(self):
        altered(self.docs[0],self.docs[3],SLUGS[8],'meta.json',lambda m:{**m,'source_use':{'local-ref':'still present'}});self.assert_bad('body/metadata cite mismatch')
    def test_added_unresolved_citation_rejected(self):
        altered(self.docs[0],self.docs[3],SLUGS[8],'body.html',lambda b:b+'{{cite:unknown-id}}');self.assert_bad('unresolved IDs')
    def test_removed_original_source_support_rejected(self):
        self.docs[2]['sources'][0]['supports']='';self.assert_bad('missing source/claim reading scope')
    def test_unsafe_source_url_rejected(self):
        self.docs[2]['sources'][0]['url']='http://example.com/insecure';self.assert_bad('unsafe citation destination')
    def test_duplicate_base_source_id_rejected(self):
        self.docs[2]['sources'].append(copy.deepcopy(self.docs[2]['sources'][0]));self.assert_bad('duplicate or malformed BASE')
    def test_changed_draft_status_rejected(self):
        altered(self.docs[0],self.docs[3],SLUGS[8],'meta.json',lambda m:{**m,'status':{'publish':'published'}});self.assert_bad('no longer draft')
    def test_approval_bypass_rejected(self):
        altered(self.docs[0],self.docs[3],SLUGS[8],'meta.json',lambda m:{**m,'safety_review':{'state':'approved'}});self.assert_bad('no longer draft')
    def test_reading_depth_warning_does_not_approve(self):
        altered(self.docs[0],self.docs[3],SLUGS[8],'body.html',lambda b:b.replace(TEXT,'Short explanation. '));r=report(self.docs)
        self.assertTrue(any('reading-depth below' in w for w in r['warnings']))
        self.assertFalse(r['publication_approved'])
    def test_all_variants_remain_visible(self):
        r=report(self.docs);versions=[x for x in r['per_variant'] if x['slug']==SHELTER[0]]
        self.assertEqual(len(versions),2)
        self.assertNotEqual(versions[0]['body_git_blob'],versions[1]['body_git_blob'])
        self.assertEqual(len([d for d in r['reading_depth_comparison'] if d['human_adjudication']]),4)
    def test_base_fallback_not_same_as_human_verified(self):
        r=report(self.docs);self.assertEqual(r['per_variant'][0]['base_fallback_ids'],['base-ref'])
        self.assertFalse(r['qualified_safety_approved'])
    def test_untrusted_meta_slug_detected(self):
        altered(self.docs[0],self.docs[3],SLUGS[8],'meta.json',lambda m:{**m,'slug':'alien'});self.assert_bad('article identity')
    def test_origin_removed_detected(self):
        del self.docs[1]['article_origins'][SLUGS[8]];self.assert_bad('article missing original source owner')
    def test_fragment_deleted_detected(self):
        self.docs[0]['objects']=[o for o in self.docs[0]['objects'] if not o['path'].endswith('fragments/start.json')]
        self.assert_bad('reading-scope fragment absent')


def make_citation_mutation_test(slug):
    def case(self):
        m,x,reg,store=self.docs
        altered(m,store,slug,'body.html',lambda h:h+'{{cite:absent-from-origin-and-base}}')
        self.assert_bad('unresolved IDs: '+slug)
    return case

for index,slug in enumerate(SLUGS):
    setattr(R379Tests,f'test_original_{index+1:02d}_citation_scope_hold',make_citation_mutation_test(slug))

if __name__ == '__main__':
    unittest.main()
