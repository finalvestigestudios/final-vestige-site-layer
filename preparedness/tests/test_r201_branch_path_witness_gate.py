"""Deterministic R201 branch-path evidence checks, using synthetic fixtures only."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'tools/r201_branch_path_witness_gate.py'
SPEC = importlib.util.spec_from_file_location('r201_gate', SOURCE)
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)


def make_sample(size=5):
    rows = []
    trees = {k: {} for k in GATE.HEADS}
    for n in range(1, size + 1):
        slug = f'preparedness-article-{n}'
        owner = list(GATE.HEADS)[(n - 1) % len(GATE.HEADS)]
        witnesses = [owner, 'start'] if owner != 'start' else [owner]
        body = f'{n:040x}'
        meta = f'{n+100:040x}'
        rows.append({'n': n, 'slug': slug, 'section': 'lost-ways',
                     'route': f'/preparedness/lost-ways/{slug}/',
                     'source_cluster': owner, 'branch_sha': GATE.HEADS[owner],
                     'body_oid': body, 'meta_oid': meta, 'also_in': witnesses})
        for k in witnesses:
            for suffix, oid in (('body.html',body), ('meta.json',meta)):
                trees[k][GATE.ARTICLE_DIR + slug + '.' + suffix] = ('100644','blob',oid)
    manifest = {'schema': GATE.SCHEMA, 'issue':136, 'conversion_issue':820,
                'state':GATE.HOLD, 'publication_authorized':False,
                'independent_qd_pass':False, 'human_source_approved':False,
                'medical_safety_verified':False, 'merchant_offer_verified':False,
                'verified_paid_orders':None, 'realized_net_revenue':None,
                'branch_heads':dict(GATE.HEADS), 'artifact_count': size,
                'export_target_count_with_six_tools':size+6, 'articles':rows}
    return manifest, trees

class BranchPathTests(unittest.TestCase):
    def setUp(self):
        self.manifest, self.trees = make_sample(7)

    def ok(self):
        result = GATE.check(self.manifest,self.trees,strict=False)
        self.assertEqual(result['state'],GATE.HOLD,result['errors'])
        self.assertFalse(result['publication_authorized'])
        self.assertFalse(result['independent_qd_pass'])
        return result

    def bad(self, needle):
        result = GATE.check(self.manifest,self.trees,strict=False)
        self.assertEqual(result['state'],GATE.INVALID,result)
        self.assertEqual(result['evidence'],[])
        self.assertIn(needle,' '.join(result['errors']))

    def test_accepted_fixture_still_hard_hold(self):
        report = self.ok()
        self.assertEqual(report['summary']['articles'],7)
        self.assertEqual(report['summary']['branch_heads'],7)
        self.assertEqual(report['summary']['verified_git_paths'],2*len(report['evidence']))

    def test_git_blob_identity_known(self):
        self.assertEqual(GATE.blob_oid(b'hello'), 'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')

    def test_rejects_unexpected_schema(self):
        self.manifest['schema']='wrong';self.bad('schema')

    def test_rejects_nondraft_manifest(self):
        self.manifest['state']='QD_PASS';self.bad('hold')

    def test_rejects_changed_source_head(self):
        self.manifest['branch_heads']['start']='a'*40;self.bad('head')

    def test_rejects_missing_branch_tree(self):
        del self.trees['start'];self.bad('branch tree')

    def test_rejects_extra_branch_tree(self):
        self.trees['rogue']={};self.bad('branch tree')

    def test_rejects_wrong_governance(self):
        self.manifest['issue']=999;self.bad('governance')

    def test_rejects_wrong_article_count(self):
        self.manifest['artifact_count']=100;self.bad('census')

    def test_rejects_duplicate_routes(self):
        self.manifest['articles'][1]['slug']=self.manifest['articles'][0]['slug']
        self.bad('slug')

    def test_rejects_missing_article(self):
        self.manifest['articles']=[];self.bad('roster')

    def test_rejects_wrong_declared_route(self):
        self.manifest['articles'][0]['route']='/preparedness/other/';self.bad('route')

    def test_rejects_nonregular_mode(self):
        path=GATE.ARTICLE_DIR+'preparedness-article-1.body.html'
        self.trees['start'][path]=('120000','blob',self.manifest['articles'][0]['body_oid'])
        self.bad('mismatch')

    def test_rejects_nonblob_object(self):
        path=GATE.ARTICLE_DIR+'preparedness-article-1.body.html'
        self.trees['start'][path]=('100644','tree',self.manifest['articles'][0]['body_oid'])
        self.bad('mismatch')

    def test_rejects_missing_owner_metadata_path(self):
        del self.trees['start'][GATE.ARTICLE_DIR+'preparedness-article-1.meta.json']
        self.bad('missing path')

    def test_rejects_unsafe_slug(self):
        self.manifest['articles'][0]['slug']='../../evil';self.bad('slug')

    def test_rejects_duplicate_witness(self):
        self.manifest['articles'][0]['also_in']=['start','start'];self.bad('witness')

    def test_rejects_invalid_oid(self):
        self.manifest['articles'][0]['meta_oid']='abc';self.bad('blob')

    def test_rejects_explicit_paid_order(self):
        self.manifest['verified_paid_orders']=1;self.bad('revenue')

    def test_strict_must_have_35_articles(self):
        result=GATE.check(self.manifest,self.trees)
        self.assertEqual(result['state'],GATE.INVALID)

    def test_exact_path_mode_and_oid_every_original_article(self):
        # 35 distinct corruption cases: one per original slate position.
        for n in range(1,36):
            with self.subTest(article=n):
                manifest,trees=make_sample(35)
                row=manifest['articles'][n-1]
                key=row['source_cluster']
                path=GATE.ARTICLE_DIR+row['slug']+'.body.html'
                trees[key][path]=('100644','blob','f'*40)
                result=GATE.check(manifest,trees,strict=False)
                self.assertEqual(result['state'],GATE.INVALID)

    def test_exact_meta_oid_every_original_article(self):
        # Another 35 independent source metadata substitution cases.
        for n in range(1,36):
            with self.subTest(article=n):
                manifest,trees=make_sample(35)
                row=manifest['articles'][n-1]
                key=row['source_cluster']
                path=GATE.ARTICLE_DIR+row['slug']+'.meta.json'
                trees[key][path]=('100644','blob','e'*40)
                result=GATE.check(manifest,trees,strict=False)
                self.assertEqual(result['state'],GATE.INVALID)

    def test_inherited_path_substitution_all_covered(self):
        manifest,trees=make_sample(35)
        for row in manifest['articles']:
            if len(row['also_in'])<2:
                continue
            with self.subTest(slug=row['slug']):
                mutated=copy.deepcopy(trees)
                path=GATE.ARTICLE_DIR+row['slug']+'.body.html'
                mutated[row['also_in'][1]][path]=('100644','blob','d'*40)
                report=GATE.check(manifest,mutated,strict=False)
                self.assertEqual(report['state'],GATE.INVALID)

    def test_duplicate_json_is_rejected(self):
        with self.assertRaisesRegex(GATE.CustodyError,'duplicate JSON key'):
            GATE.strict_json(b'{"a":1,"a":2}')

    def test_json_nan_is_rejected(self):
        with self.assertRaisesRegex(GATE.CustodyError,'non-JSON constant'):
            GATE.strict_json(b'{"a":NaN}')

    def test_cli_with_missing_repo_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(GATE.main(['--repo',td,'--report',td+'/report.json']),3)
            obj=json.loads(Path(td,'report.json').read_text())
            self.assertEqual(obj['state'],GATE.INVALID)
            self.assertFalse(obj['publication_authorized'])

def make_flag_check(flag):
    def test(self):
        self.manifest[flag]=True
        self.bad('unsupported')
    return test
for flag in ('publication_authorized','independent_qd_pass','human_source_approved',
             'medical_safety_verified','merchant_offer_verified'):
    setattr(BranchPathTests, 'test_rejects_false_approval_'+flag, make_flag_check(flag))

# Separate real unittest methods, rather than relying on subtest counts.
def make_path_mutation(n,kind):
    def test(self):
        manifest,trees=make_sample(35)
        row=manifest['articles'][n-1]
        path=GATE.ARTICLE_DIR+row['slug']+('.body.html' if kind=='body' else '.meta.json')
        trees[row['source_cluster']][path]=('100644','blob','f'*40)
        self.assertEqual(GATE.check(manifest,trees,strict=False)['state'],GATE.INVALID)
    return test
for n in range(1,36):
    for kind in ('body','meta'):
        setattr(BranchPathTests,f'test_frozen_{kind}_path_mutation_{n:02d}',make_path_mutation(n,kind))

if __name__=='__main__': unittest.main()
