"""R220 synthetic regressions only. Never writes to the real archive checkout."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r220_full_slate_draft_custody as gate
import r226_export_browser_custody as dom_gate
import r227_inert_context_citation_hold as inert_gate
import r230_html_tokenizer_state_hold as tokenizer_gate

HEADS = {key: 'abcdef1'[i] * 40 for i, key in enumerate(
    ('start', 'shelter', 'food', 'health', 'hist-field', 'hist-food', 'hist-home'))}


def sample_doc():
    articles = []
    for n in range(1, 36):
        cluster = list(HEADS)[(n - 1) % 7]
        slug = f'article-{n}'
        articles.append({'n': n, 'slug': slug, 'section': 'start-here',
                         'track': 'modern', 'route': f'/preparedness/start-here/{slug}/',
                         'source_cluster': cluster, 'branch_sha': HEADS[cluster],
                         'body_oid': 'd' * 40, 'meta_oid': 'e' * 40, 'body_bytes': 200,
                         'meta_bytes': 100})
    return {'schema': 'fv-preparedness-r200-seven-cluster-35-article-frozen-custody-v1',
            'state': gate.HOLD, 'issue': 136, 'conversion_issue': 820,
            'artifact_count': 35, 'export_target_count_with_six_tools': 41,
            'publication_authorized': False, 'independent_qd_pass': False,
            'human_source_approved': False, 'medical_safety_verified': False,
            'merchant_offer_verified': False, 'branch_heads': HEADS, 'articles': articles}


class RosterTests(unittest.TestCase):
    def setUp(self):
        self.doc = sample_doc()

    def test_positive_synthetic_roster(self):
        self.assertEqual(len(gate.verify_roster(self.doc)), 35)

    def test_missing_article(self):
        self.doc['articles'].pop()
        with self.assertRaises(ValueError): gate.verify_roster(self.doc)

    def test_extra_article(self):
        self.doc['articles'].append(copy.deepcopy(self.doc['articles'][-1]))
        with self.assertRaises(ValueError): gate.verify_roster(self.doc)

    def test_unauthorized_qd(self):
        self.doc['independent_qd_pass'] = True
        with self.assertRaises(ValueError): gate.verify_roster(self.doc)

    def test_unrecognized_head(self):
        self.doc['branch_heads']['extra'] = 'a' * 40
        with self.assertRaises(ValueError): gate.verify_roster(self.doc)

    def test_duplicate_json_keys(self):
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            gate.strict_object(b'{"state":"DRAFT_HARD_HOLD","state":"PASS"}')

    def test_nonfinite_json(self):
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            gate.strict_object(b'{"test":NaN}')

    def test_json_array_not_object(self):
        with self.assertRaises(ValueError): gate.strict_object(b'[]')

    def test_git_blob_known(self):
        self.assertEqual(gate.git_blob(b'hello'), 'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')


def _roster_mutation(field, n, changed):
    def check(self):
        doc = sample_doc()
        doc['articles'][n - 1][field] = changed
        with self.assertRaises(ValueError): gate.verify_roster(doc)
    return check


for _n in range(1, 36):
    setattr(RosterTests, f'test_article_{_n:02d}_route_hijack',
            _roster_mutation('route', _n, '/preparedness/hijacked/'))
    setattr(RosterTests, f'test_article_{_n:02d}_source_head_forgery',
            _roster_mutation('branch_sha', _n, '0' * 40))


class FilesystemTests(unittest.TestCase):
    def test_path_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError): gate.safe_read(Path(td), '../secret')

    def test_absolute_path(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError): gate.safe_read(Path(td), '/etc/passwd')

    def test_backslash_escape(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError): gate.safe_read(Path(td), 'a\\..\\b')

    def test_linked_file(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); (p / 'real').write_text('test'); (p / 'link').symlink_to(p / 'real')
            with self.assertRaises(ValueError): gate.safe_read(p, 'link')

    def test_linked_parent(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); (p / 'real').mkdir(); (p / 'real' / 'data').write_text('test')
            (p / 'link').symlink_to(p / 'real', target_is_directory=True)
            with self.assertRaises(ValueError): gate.safe_read(p, 'link/data')

    def test_good_read(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); (p / 'data').write_bytes(b'hello')
            self.assertEqual(gate.safe_read(p, 'data'), b'hello')


class SyntheticRenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='fv-r220-synthetic-')
        cls.root = Path(cls.tmp.name)
        cls.articles = sample_doc()['articles']
        cls.allslugs = [x['slug'] for x in cls.articles] + [f'tool-{i}' for i in range(1, 7)]
        (cls.root / 'content' / 'tools').mkdir(parents=True)
        for slug in cls.allslugs[35:]:
            (cls.root / 'content' / 'tools' / f'{slug}.meta.json').write_text('{}')
        for mode in ('wp', 'preview'):
            (cls.root / 'build' / mode).mkdir(parents=True)
            for slug in cls.allslugs:
                (cls.root / 'build' / mode / f'{slug}.html').write_text(
                    '<header>Independent safety/source and QD verification pending</header>'
                    '<div class="pa-body" id="pa-main">hello x</div>'
                    '<section class="pa-sources"><h2>Sources and verification</h2><ol></ol></section>'
                    '<section class="pa-review"><h2>Review record</h2>'
                    '<p>Independent source and safety review pending.</p></section>')
        cls.entries = {}
        for slug in cls.allslugs:
            cls.entries[slug] = {'slug': slug,
                                 'canonical': f'https://finalvestige.com/preparedness/start-here/{slug}/',
                                 'sources': [], 'words': 2}
        cls.report = {'articles': list(cls.entries.values()),
                      'release_evidence': {'wordpress_publication_performed': False,
                                           'independent_qa_verified': False}}
        class Library:
            def __init__(self, names):
                self.articles = {x: {'status': {'publish': 'draft'}, '_body': 'hello x'} for x in names}
            def url_path(self, slug):
                return f'/preparedness/start-here/{slug}/'
        class Builder:
            @staticmethod
            def resolve_tokens(library, meta):
                return meta['_body'], []
            @staticmethod
            def word_count(text):
                return len(text.split())
        cls.lib = Library(cls.allslugs)
        cls.builder = Builder

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def check(self, report=None):
        return gate.verify_render(self.root, self.articles, report or self.report,
                                  self.lib, self.builder, dom_gate, inert_gate, tokenizer_gate)

    def test_positive_synthetic_render(self):
        self.assertEqual(self.check()['channel_files_verified'], 82)

    def test_all_three_guards_execute_for_every_channel(self):
        # The old fixture did not pass either new guard, causing TypeError before
        # the 82 truncation regressions could exercise their intended assertions.
        with patch.object(dom_gate, 'verify_export', wraps=dom_gate.verify_export) as d, \
             patch.object(inert_gate, 'verify_inert_contexts',
                          wraps=inert_gate.verify_inert_contexts) as n, \
             patch.object(tokenizer_gate, 'verify_tokenizer_states',
                          wraps=tokenizer_gate.verify_tokenizer_states) as t:
            self.assertEqual(self.check()['channel_files_verified'], 82)
            self.assertEqual(d.call_count, 82)
            self.assertEqual(n.call_count, 82)
            self.assertEqual(t.call_count, 82)

    def test_rendered_source_inside_template_rejected(self):
        path = self.root / 'build' / 'wp' / 'article-1.html'
        original = path.read_text()
        try:
            page = original.replace('<section class="pa-sources">',
                                    '<template><section class="pa-sources">')
            page = page.replace('</ol></section>', '</ol></section></template>')
            path.write_text(page)
            with self.assertRaisesRegex(ValueError, 'R227 conditional DOM'):
                self.check()
        finally:
            path.write_text(original)

    def test_only_noscript_warning_rejected(self):
        path = self.root / 'build' / 'preview' / 'article-2.html'
        original = path.read_text()
        try:
            page = original.replace(
                '<header>Independent safety/source and QD verification pending</header>',
                '<noscript><header>Independent safety/source and QD verification pending</header></noscript>')
            path.write_text(page)
            with self.assertRaisesRegex(ValueError, 'R227 conditional DOM'):
                self.check()
        finally:
            path.write_text(original)

    def test_closed_details_review_rejected(self):
        path = self.root / 'build' / 'wp' / 'article-3.html'
        original = path.read_text()
        try:
            page = original.replace('<section class="pa-review">',
                                    '<details><section class="pa-review">')
            page = page.replace('</p></section>', '</p></section></details>')
            path.write_text(page)
            with self.assertRaisesRegex(ValueError, 'R227 conditional DOM'):
                self.check()
        finally:
            path.write_text(original)

    def test_missing_build_report_row(self):
        r = copy.deepcopy(self.report); r['articles'].pop()
        with self.assertRaises(ValueError): self.check(r)

    def test_extra_build_report_row(self):
        r = copy.deepcopy(self.report); r['articles'].append(dict(self.entries['article-1']))
        with self.assertRaises(ValueError): self.check(r)

    def test_unauthorized_qa(self):
        r = copy.deepcopy(self.report); r['release_evidence']['independent_qa_verified'] = True
        with self.assertRaises(ValueError): self.check(r)

    def test_unauthorized_wp_publication(self):
        r = copy.deepcopy(self.report); r['release_evidence']['wordpress_publication_performed'] = True
        with self.assertRaises(ValueError): self.check(r)

    def test_modified_canonical(self):
        r = copy.deepcopy(self.report); r['articles'][0]['canonical'] = 'https://example.invalid/foo/'
        with self.assertRaises(ValueError): self.check(r)

    def test_modified_reading_depth(self):
        r = copy.deepcopy(self.report); r['articles'][0]['words'] = 1
        with self.assertRaises(ValueError): self.check(r)

    def test_source_order_mismatch(self):
        r = copy.deepcopy(self.report); r['articles'][0]['sources'] = ['unverified']
        with self.assertRaises(ValueError): self.check(r)


def _render_mutation(slug, mode):
    def check(self):
        p = self.root / 'build' / mode / f'{slug}.html'
        original = p.read_text()
        try:
            p.write_text(original.replace('hello x', 'hello'))
            with self.assertRaises(ValueError): self.check()
        finally:
            p.write_text(original)
    return check


for _slug in [f'article-{i}' for i in range(1, 36)] + [f'tool-{i}' for i in range(1, 7)]:
    for _mode in ('wp', 'preview'):
        setattr(SyntheticRenderTests, f'test_{_mode}_{_slug.replace("-", "_")}_truncation',
                _render_mutation(_slug, _mode))


# Independently mutate one of the 82 intended WordPress/preview exports.
# Each fixture retains the intact article body and warning while introducing a
# browser plaintext-to-EOF construct just before its bibliography.
def _tokenizer_mutation(slug, mode):
    def check(self):
        p = self.root / 'build' / mode / f'{slug}.html'
        original = p.read_text()
        try:
            needle = '<section class="pa-sources">'
            self.assertIn(needle, original)
            p.write_text(original.replace(needle, '<plaintext>' + needle, 1))
            with self.assertRaisesRegex(ValueError, 'R230 unsupported tokenizer'):
                self.check()
        finally:
            p.write_text(original)
    return check


for _slug in [f'article-{i}' for i in range(1, 36)] + [f'tool-{i}' for i in range(1, 7)]:
    for _mode in ('wp', 'preview'):
        setattr(SyntheticRenderTests, f'test_{_mode}_{_slug.replace("-", "_")}_tokenizer_hold',
                _tokenizer_mutation(_slug, _mode))


class SyntheticOriginalsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='fv-r220-originals-only-')
        cls.root = Path(cls.tmp.name)
        (cls.root / 'content' / 'articles').mkdir(parents=True)
        cls.articles = sample_doc()['articles']
        for a in cls.articles:
            slug = a['slug']; n = a['n']
            body = f'<section><h2>Evidence-preserved {n}</h2><p>Original text</p></section>'.encode()
            meta = json.dumps({'n': n, 'slug': slug, 'section': a['section'],
                               'track': a['track'], 'status': {'publish': 'draft'},
                               'safety_review': {'state': 'pending'}, 'source_use': {}}).encode()
            (cls.root / 'content' / 'articles' / f'{slug}.body.html').write_bytes(body)
            (cls.root / 'content' / 'articles' / f'{slug}.meta.json').write_bytes(meta)
            a['body_oid'] = gate.git_blob(body)
            a['meta_oid'] = gate.git_blob(meta)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def check(self):
        with patch.object(gate, 'INTEGRATED_DIFFS', {}), \
             patch.object(gate, 'INTEGRATED_META_DIFFS', {}), \
             patch.object(gate, 'EXPECTED_EXCEPTIONS', {}):
            return gate.verify_originals(self.root, self.articles)

    def test_positive_complete_synthetic_originals(self):
        status, missing = self.check()
        self.assertEqual(len(status), 35)
        self.assertEqual(missing, {})


def _mutate_original(n, kind):
    def check(self):
        slug = f'article-{n}'
        ext = 'body.html' if kind == 'body' else 'meta.json'
        p = self.root / 'content' / 'articles' / f'{slug}.{ext}'
        original = p.read_bytes()
        try:
            p.write_bytes(original + b' ')
            with self.assertRaises(ValueError): self.check()
        finally:
            p.write_bytes(original)
    return check


for _n in range(1, 36):
    setattr(SyntheticOriginalsTests, f'test_article_{_n:02d}_changed_body_blocked',
            _mutate_original(_n, 'body'))
    setattr(SyntheticOriginalsTests, f'test_article_{_n:02d}_changed_metadata_blocked',
            _mutate_original(_n, 'meta'))

if __name__ == '__main__':
    unittest.main()
