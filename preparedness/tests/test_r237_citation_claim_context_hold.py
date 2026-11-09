"""Synthetic-only mutation regressions; do not edit original article/source records."""
from pathlib import Path
import json
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r237_citation_claim_context_hold as gate


class ClaimContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'content/articles').mkdir(parents=True)
        self.roster = [{'n': i, 'slug': f'case-{i}'} for i in range(1, 36)]
        for row in self.roster:
            n, slug = row['n'], row['slug']
            markers = '{{cite:general-guide}}'
            if n == 7: markers += '{{cite:cdc-find-clean-water}}{{cite:cdc-find-clean-water}}'
            if n == 20: markers += '{{cite:start-ready-plan}}'
            body = '<section class="pa-act"><p>Follow household planning guidance. ' + markers + '</p></section>'
            notes = {'general-guide': 'Original author source reading, not a source approval'}
            if n == 7: notes['cdc-find-clean-water'] = 'Source reading note remains unreviewed'
            if n == 20: notes['start-ready-plan'] = 'Source reading note remains unreviewed'
            (self.root / f'content/articles/{slug}.body.html').write_text(body)
            (self.root / f'content/articles/{slug}.meta.json').write_text(json.dumps({
                'n': n, 'slug': slug, 'source_use': notes,
                'status': {'publish': 'draft'}}))

    def tearDown(self): self.tmp.cleanup()

    def audit(self):
        return gate.audit_claim_contexts(self.root, self.roster,
                            lambda root, rel: (root / rel).read_bytes())

    def edit_body(self, n, func):
        p = self.root / f'content/articles/case-{n}.body.html'
        p.write_text(func(p.read_text()))

    def test_baseline_review_only(self):
        r = self.audit()
        self.assertEqual((r['article_count'], r['citation_count']), (35, 38))
        self.assertEqual(r['original_hold_occurrences'], 3)
        for field in ('release_authorized','independent_qd_pass',
                      'source_review_approved', 'medical_safety_verified', 'claim_evidence_adjudicated'):
            self.assertIs(r[field], False)
        self.assertEqual(len(r['articles'][6]['occurrences']), 3)

    def test_same_inputs_deterministic(self):
        self.assertEqual(self.audit()['receipt_sha256'], self.audit()['receipt_sha256'])

    def test_duplicate_metadata_key_rejected(self):
        p = self.root / 'content/articles/case-1.meta.json'
        s = json.loads(p.read_text())
        p.write_text(json.dumps(s)[:-1] + ',"source_use":{}}')
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'): self.audit()

    def test_original_holds_cannot_be_deleted(self):
        self.edit_body(7, lambda s: s.replace('{{cite:cdc-find-clean-water}}', '', 1))
        with self.assertRaisesRegex(ValueError, 'original source-review occurrence HOLD'): self.audit()

    def test_unapproved_article_status_fails(self):
        p = self.root / 'content/articles/case-1.meta.json'
        s = json.loads(p.read_text());s['status']['publish']='published';p.write_text(json.dumps(s))
        with self.assertRaisesRegex(ValueError, 'metadata/status mismatch'):self.audit()

    def test_hidden_html_comment_fails(self):
        self.edit_body(1, lambda s: s.replace('{{cite:general-guide}}', '<!-- {{cite:general-guide}} -->'))
        with self.assertRaisesRegex(ValueError, 'concealed in markup'):self.audit()

    def test_embedded_link_token_never_approves(self):
        self.edit_body(1, lambda s: s.replace('{{cite:general-guide}}',
                                              '{{link:general-guide|Read more}}{{cite:general-guide}}'))
        r=self.audit();self.assertIs(r['source_review_approved'],False)


def hide_case(n):
    def run(self):
        self.edit_body(n, lambda s: s.replace('{{cite:general-guide}}',
                                     '<template>{{cite:general-guide}}</template>'))
        with self.assertRaisesRegex(ValueError, 'concealed in markup'):self.audit()
    return run


def attr_case(n):
    def run(self):
        self.edit_body(n, lambda s: s.replace('{{cite:general-guide}}',
                                            '<span data-source="{{cite:general-guide}}">source</span>'))
        with self.assertRaisesRegex(ValueError, 'concealed in markup'):self.audit()
    return run


def drift_case(n):
    def run(self):
        base = self.audit()['receipt_sha256']
        self.edit_body(n, lambda s: s.replace('Follow household planning guidance.',
                                             'Follow household emergency planning instructions.'))
        altered = self.audit()['receipt_sha256']
        self.assertNotEqual(base, altered)
        self.assertFalse(self.audit()['source_review_approved'])
    return run


for i in range(1,36):
    setattr(ClaimContextTests, f'test_article_{i:02d}_template_citation_hidden', hide_case(i))
    setattr(ClaimContextTests, f'test_article_{i:02d}_attribute_citation_hidden', attr_case(i))
    setattr(ClaimContextTests, f'test_article_{i:02d}_context_drift_changes_receipt', drift_case(i))

if __name__ == '__main__': unittest.main()
