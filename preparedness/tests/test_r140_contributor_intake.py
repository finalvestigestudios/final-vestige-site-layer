"""R140 intake manifest parser and fail-closed drift tests."""
import copy, importlib.util, json, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('r140_gate', ROOT/'tools'/'r140_contributor_intake.py')
g=importlib.util.module_from_spec(spec);sys.modules[spec.name]=g;spec.loader.exec_module(g)
MANIFEST=ROOT/'docs'/'r140'/'branch_intake_evidence.json'

class IntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.original=json.loads(MANIFEST.read_text())
    def test_grounded_census(self):
        a=g.validate_manifest(self.original)
        self.assertEqual(14,len(a));self.assertEqual(7,len(self.original['branch_heads']))
        self.assertEqual(8,sum(g.issue_class(x)=='DEPTH_OR_CITATION_REGRESSION_HOLD' for x in a))
        self.assertEqual(2,sum(g.issue_class(x)=='CITATION_ID_RETARGET_HOLD' for x in a))
        self.assertEqual(4,sum(g.issue_class(x)=='BLOB_DRIFT_REQUIRES_REVIEW' for x in a))
        self.assertEqual(3245,sum(x['baseline_words']-x['contributor_words'] for x in a))
        self.assertEqual(29,sum(x['baseline_citations']-x['contributor_citations'] for x in a))
    def test_observed_replacements_are_different(self):
        for x in self.original['drifts']:
            with self.subTest(x=x['slug']):self.assertNotEqual(x['baseline_blob'],x['contributor_blob'])
    def test_unknown_checkout_hold(self):
        with tempfile.TemporaryDirectory() as d:
            a=g.evaluate(self.original,Path(d))
            self.assertEqual(0,a['baseline_preserved']);self.assertEqual(14,a['total_drifted_articles'])
            self.assertTrue(all(x['status']=='MISSING_ARTICLE_HOLD' for x in a['article_checks']))
            self.assertFalse(a['qd_approved']);self.assertFalse(a['publish_authorized'])
    def test_baseline_contributor_third_version_and_symlink(self):
        data=b'<p>word {{cite:official-1}}</p>'
        rec=copy.deepcopy(self.original['drifts'][0]);rec['baseline_blob']=g.git_blob(data)
        rec['contributor_blob']=g.git_blob(data+b' changed')
        obj=copy.deepcopy(self.original);obj['drifts']=[rec]
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/'preparedness/content/articles'/f"{rec['slug']}.body.html"
            p.parent.mkdir(parents=True);p.write_bytes(data)
            self.assertEqual('BASELINE_BLOB_PRESERVED_NOT_SAFETY_APPROVED',g.evaluate(obj,Path(root))['article_checks'][0]['status'])
            p.write_bytes(data+b' changed')
            self.assertEqual('UNREVIEWED_CONTRIBUTOR_REPLACEMENT_HOLD',g.evaluate(obj,Path(root))['article_checks'][0]['status'])
            p.write_bytes(data+b' different')
            self.assertEqual('UNREVIEWED_THIRD_VERSION_HOLD',g.evaluate(obj,Path(root))['article_checks'][0]['status'])
            p.unlink();p.symlink_to('/etc/hosts')
            self.assertEqual('SYMLINK_ARTICLE_HOLD',g.evaluate(obj,Path(root))['article_checks'][0]['status'])
    def test_git_identity(self):
        self.assertEqual('e69de29bb2d1d6434b8b29ae775ad8c2e48c5391',g.git_blob(b''))
        self.assertEqual(1,g.inspect_bytes(b'<p>word {{cite:a}}</p>')['words'])

class TamperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.original=json.loads(MANIFEST.read_text())
    def fails(self,obj):
        with self.assertRaises(ValueError):g.validate_manifest(obj)
    def test_7_missing_branches(self):
        for name in g.EXPECTED:
            with self.subTest(name=name):
                a=copy.deepcopy(self.original);del a['branch_heads'][name];self.fails(a)
    def test_7_malformed_branches(self):
        for name in g.EXPECTED:
            with self.subTest(name=name):
                a=copy.deepcopy(self.original);a['branch_heads'][name]='bad';self.fails(a)
    def test_28_broken_blob_identities(self):
        for i in range(14):
            for key in ('baseline_blob','contributor_blob'):
                with self.subTest(i=i,key=key):
                    a=copy.deepcopy(self.original);a['drifts'][i][key]='notsha';self.fails(a)
    def test_14_duplicate_paths(self):
        for i in range(14):
            with self.subTest(i=i):
                a=copy.deepcopy(self.original);a['drifts'].append(copy.deepcopy(a['drifts'][i]));self.fails(a)
    def test_14_negative_citation_counts(self):
        for i in range(14):
            with self.subTest(i=i):
                a=copy.deepcopy(self.original);a['drifts'][i]['baseline_citations']=-1;self.fails(a)
    def test_14_boolean_word_counts(self):
        for i in range(14):
            with self.subTest(i=i):
                a=copy.deepcopy(self.original);a['drifts'][i]['contributor_words']=True;self.fails(a)
    def test_5_fake_approvals(self):
        for key in ('qd_pass','medically_safe','publish_authorized','reviewer_approved','production_status'):
            with self.subTest(key=key):
                a=copy.deepcopy(self.original);a['drifts'][0][key]=True;self.fails(a)
    def test_7_path_traversals(self):
        for slug in ('../escape','One two','sub/path','ABC','slug--double','slug.html','a\\b'):
            with self.subTest(slug=slug):
                a=copy.deepcopy(self.original);a['drifts'][0]['slug']=slug;self.fails(a)
    def test_invalid_source_mapping(self):
        a=copy.deepcopy(self.original);a['drifts'][0]['removed_source_ids']=['abc'];a['drifts'][0]['added_source_ids']=['abc'];self.fails(a)
        a=copy.deepcopy(self.original);a['source_note']='AUTO PASS';self.fails(a)
        a=copy.deepcopy(self.original);a['drifts'][0]['added_source_ids']=['javascript:alert(1)'];self.fails(a)
    def test_schema_top_level_approval(self):
        for key,val in [('schema','R140-INTAKE-2'),('rc_sha','bad')]:
            a=copy.deepcopy(self.original);a[key]=val;self.fails(a)
        a=copy.deepcopy(self.original);a['release']='LIVE';self.fails(a)

if __name__=='__main__':unittest.main()

# One independent discovered unittest method per observed contributor article and
# mutation class, rather than subTest-only inflation of the test counter.
def _make_per_article_case(index, mode):
    def test(self):
        a=copy.deepcopy(self.original)
        rec=a['drifts'][index]
        if mode == 'source_id_injection':
            rec['added_source_ids']=['nchfp-jerky', 'nchfp-jerky']
        elif mode == 'forged_approval':
            rec['publication_approved']=True
        elif mode == 'invalid_object_sha':
            rec['baseline_blob']='0'*39
        elif mode == 'unsafe_slug':
            rec['slug']='../../override'
        self.fails(a)
    return test
for _i, _item in enumerate(json.loads(MANIFEST.read_text())['drifts']):
    for _mode in ('source_id_injection','forged_approval','invalid_object_sha','unsafe_slug'):
        setattr(TamperTests, f'test_article_{_i:02d}_{_mode}', _make_per_article_case(_i,_mode))
