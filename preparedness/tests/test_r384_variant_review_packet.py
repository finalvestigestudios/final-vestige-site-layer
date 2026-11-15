"""R384 immutable source / manuscript fork custody tests (all synthetic)."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

P = Path(__file__).resolve().parents[1] / 'tools' / 'r384_variant_review_packet.py'
S = importlib.util.spec_from_file_location('r384_variant', P)
G = importlib.util.module_from_spec(S)
S.loader.exec_module(G)
BRANCHES = ['claude/prep-start-bbfeb8', 'claude/prep-food-ccdc55', 'claude/prep-health-837444',
            'claude/prep-hist-field-9db767', 'claude/prep-hist-food-b81f19', 'claude/prep-hist-home-0e0e38',
            'claude/prep-shelter-5e1e0e', 'claude/prep-shelter-continuation', 'claude/prep-shelter-followup-evidence']


def fixture():
    blobs = {}
    objects = []
    def store(data):
        if isinstance(data, str): data = data.encode('utf-8')
        sha = G.blob_sha(data)
        blobs[sha] = data
        return sha, len(data)
    def make(path, content, branches):
        variants = []
        for branch, data in zip(branches, content):
            sha, size = store(data)
            variants.append({'branch': branch, 'sha': sha, 'size': size})
        objects.append({'path': path, 'variants': variants, 'decision': 'REVIEW_REQUIRED' if len(set(v['sha'] for v in variants)) > 1 else 'IDENTICAL_OR_SINGLE', 'selected_sha': None})
    for i in range(35):
        slug = 'article-%02d' % i
        branches = BRANCHES[6:9] if i < 4 else [BRANCHES[i % 6]]
        bodies, metas = [], []
        for j, _ in enumerate(branches):
            extra = '<p>Revision %s records an additional editorial clarification.{{cite:scope-b}}</p>' % j if j else ''
            bodies.append('<article><h2>Household evidence</h2><p>Original evidence remains readable for a family seeking current guidance.{{cite:scope-a}}</p>' + extra + '</article>')
            meta = {'n': i+1, 'slug': slug, 'status': {'publish': 'draft'},
                    'safety_review': {'state': 'pending'},
                    'source_use': {'scope-a': 'Relevant supporting evidence'} | ({'scope-b': 'Specific changed scope'} if j else {})}
            metas.append(json.dumps(meta, sort_keys=True))
        make('preparedness/content/articles/' + slug + '.body.html', bodies, branches)
        make('preparedness/content/articles/' + slug + '.meta.json', metas, branches)
    for i in range(7):
        branches = BRANCHES[6:9] if i == 0 else [BRANCHES[i % 6]]
        content = [json.dumps({'sources':[{'id': 'src-' + str(i), 'supports': 'Version ' + str(j)}]}) for j in range(len(branches))]
        make('preparedness/sources/fragments/frag-%d.json' % i, content, branches)
    assert len(objects) == 77 and sum(len({v['sha'] for v in o['variants']}) > 1 for o in objects) == 9
    manifest = {'release_state': 'DRAFT_HARD_HOLD', 'article_count': 35, 'conflict_count': 9,
                'branch_pins': [{'branch': b, 'sha': ('%x' % (i+1))*40} for i,b in enumerate(BRANCHES)],
                'objects': objects}
    return manifest, blobs


def analyze(m=None, blobs=None):
    if m is None: m, blobs = fixture()
    return G.build_packet(m, lambda sha: blobs[sha])


class PacketTests(unittest.TestCase):
    def test_valid_preserves_all_variants(self):
        out = analyze()
        self.assertEqual(out['status'], 'REVIEW_PACKET_HARD_HOLD')
        self.assertEqual(len(out['articles']), 35)
        self.assertEqual(len(out['unselected_conflicts']), 9)
        self.assertEqual(len(out['review_deltas']), 12)
        self.assertFalse(out['publication_approved'])
        self.assertFalse(out['qualified_safety_approved'])
    def test_no_selection_on_valid_input(self):
        m, blobs = fixture()
        before = json.dumps(m, sort_keys=True)
        analyze(m, blobs)
        self.assertEqual(json.dumps(m, sort_keys=True), before)
    def test_removed_claim_block_custody(self):
        a = {'branch':'a','blocks':[{'full_sha256':'x','prose_sha256':'p','citations':['a']}], 'source_use':{'a':'scope'},'safety_state':'pending','words':100,'body_sha':'b','meta_sha':'m'}
        b = {**a, 'branch':'b', 'blocks':[], 'words':20, 'body_sha':'c'}
        d = G.pair_delta(a,b)
        self.assertEqual(d['removed_exact_blocks'], 1)
        self.assertEqual(d['word_delta'], -80)
        self.assertEqual(d['removed_citation_occurrences'], {'a':1})
    def test_same_prose_new_evidence_is_reviewed(self):
        block = {'full_sha256':'x','prose_sha256':'same','citations':['a']}
        a = {'branch':'a','blocks':[block], 'source_use':{'a':'scope'},'safety_state':'pending','words':3,'body_sha':'b','meta_sha':'m'}
        b = {**a, 'branch':'b', 'blocks':[{'full_sha256':'y','prose_sha256':'same','citations':['b']}], 'body_sha':'c'}
        self.assertEqual(G.pair_delta(a,b)['changed_support_prose_sha256'], ['same'])
    def test_changed_source_reading_scope_retained(self):
        a = {'branch':'a','blocks':[], 'source_use':{'a':'old'},'safety_state':'pending','words':0,'body_sha':'b','meta_sha':'m'}
        b = {**a, 'branch':'b', 'source_use':{'a':'new'}, 'meta_sha':'n'}
        self.assertEqual(G.pair_delta(a,b)['source_use_text_changed'], ['a'])
    def test_historical_approved_is_not_qd(self):
        m, blobs = fixture()
        row = next(o for o in m['objects'] if o['path'].endswith('article-12.meta.json'))['variants'][0]
        d = json.loads(blobs[row['sha']]); d['safety_review']['state'] = 'approved'
        replace_blob(row, d, blobs)
        out = analyze(m, blobs)
        self.assertEqual(out['status'], 'REVIEW_PACKET_HARD_HOLD')
        self.assertFalse(out['qualified_safety_approved'])
        self.assertEqual(out['articles'][12]['variants'][0]['safety_state'], 'approved')
    def test_bad_manifest_fails_closed(self):
        out = analyze({'release_state':'DRAFT_HARD_HOLD'}, {})
        self.assertIn('MANIFEST_INVARIANT_MISMATCH', out['errors'])
        self.assertFalse(out['publication_approved'])
    def test_body_parse_preserves_inline_citations(self):
        b = G.paragraphs(b'<p>Text <em>with</em> citation {{cite:source-a}} and another.</p>')
        self.assertEqual(b[0]['citations'], ['source-a'])
        self.assertIn('Text with citation', b[0]['text'])
    def test_script_data_not_in_claim(self):
        b = G.paragraphs(b'<p>Visible guidance.</p><script>fake words {{cite:evil}}</script>')
        self.assertEqual(len(b), 1)
        self.assertNotIn('evil', b[0]['citations'])
    def test_cli_never_exit_zero(self):
        import subprocess
        r = subprocess.run(['python','-I',str(P),'--repo','/nonexistent'],capture_output=True,text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn('INVALID_HARD_HOLD', r.stdout)


def replace_blob(row, data, blobs):
    new = data if isinstance(data,bytes) else json.dumps(data,sort_keys=True).encode()
    row['sha'] = G.blob_sha(new)
    row['size'] = len(new)
    blobs[row['sha']] = new


class MutationTests(unittest.TestCase): pass


def mutate_case(name, mod, expect):
    def run(self):
        m, blobs = fixture()
        mod(m, blobs)
        out = analyze(m, blobs)
        self.assertEqual(out['status'], 'INVALID_HARD_HOLD', out)
        self.assertTrue(any(expect in e for e in out['errors']), out['errors'])
        self.assertFalse(out['publication_approved'])
    setattr(MutationTests, 'test_' + name, run)

for key, val, reason in [('release_state','PUBLIC','MANIFEST_INVARIANT'),
                         ('article_count',34,'MANIFEST_INVARIANT'),
                         ('conflict_count',8,'MANIFEST_INVARIANT')]:
    mutate_case('bad_'+key,lambda m,b,k=key,v=val:m.__setitem__(k,v),reason)
for n in range(35):
    def mod(m, blobs, n=n):
        row=next(o for o in m['objects'] if o['path'].endswith('article-%02d.meta.json' % n))['variants'][0]
        data=json.loads(blobs[row['sha']]); data['slug']='wrong-slug'
        replace_blob(row,data,blobs)
    mutate_case('wrong_slug_%02d'%n,mod,'VARIANT_PARSE_FAILED')
for n in range(9):
    mutate_case('pin_changed_%d'%n,lambda m,b,n=n:m['branch_pins'][n].__setitem__('sha','not-a-sha'),'INVALID_BRANCH_PINS')
for n in range(9):
    def mod(m,b,n=n):
        m['objects'][n]['variants'][0]['sha']='f'*40
    mutate_case('blob_tamper_%d'%n,mod,'ORIGINAL_OBJECT_READ_FAILED')
for n in range(4):
    def mod(m, blobs, n=n):
        target='article-%02d.meta.json'%n
        row=next(o for o in m['objects'] if o['path'].endswith(target))['variants'][-1]
        d=json.loads(blobs[row['sha']]); d['status']['publish']='published'
        replace_blob(row,d,blobs)
    mutate_case('published_%d'%n,mod,'VARIANT_PARSE_FAILED')
for n in range(4):
    def mod(m, blobs, n=n):
        row=next(o for o in m['objects'] if o['path'].endswith('article-%02d.meta.json'%n))['variants'][0]
        d=json.loads(blobs[row['sha']]); d['safety_review']['state']='QD PASS'
        replace_blob(row,d,blobs)
    mutate_case('fake_qd_%d'%n,mod,'VARIANT_PARSE_FAILED')

if __name__ == '__main__': unittest.main()
