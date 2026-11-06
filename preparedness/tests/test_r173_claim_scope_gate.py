"""R173 adversarial synthetic-only tests; no genuine source or safety PASS."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import copy
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r173_claim_scope_gate as g


def synthetic():
    metas = {}
    bodies = {}
    for slug in g.BODY_SHAS:
        metas[slug] = {'slug': slug,
           'section': 'food' if slug == 'safe-jerky-dehydration' else 'lost-ways',
           'status': {'publish': 'draft'},
           'safety_review': {'state': 'pending', 'reviewer': None, 'date': None},
           'source_use': {}}
        bodies[slug] = '<h2>Original synthetic draft only</h2>\n'
    for slug, label, anchor, ids in g.CLAIMS:
        for sid in ids:
            metas[slug]['source_use'][sid] = 'Separate source-scope reading by reviewer.'
        qualifier = ''
        if label == 'not-a-recipe':
            qualifier = ' no method and no storage times are supplied.'
        if label == 'published-method-conflict':
            qualifier = ' after drying bacteria become more heat resistant.'
        if label == 'agencies-disagree':
            qualifier = ' before drying and after drying differ.'
        bodies[slug] += '<p>' + anchor + qualifier + ''.join(
            '{{cite:' + sid + '}}' for sid in ids) + '</p>\n'
    return bodies, metas


class TestR173(unittest.TestCase):
    def test_synthetic_hold_even_with_complete_claims(self):
        r = g.evaluate(*synthetic(), strict=False)
        self.assertEqual(r['state'], g.HOLD)
        self.assertEqual(len(r['claims_flagged_for_human_review']), 10)
        self.assertEqual(r['affected_articles'], 3)
        for name in ('source_scope_review_completed', 'medically_or_food_safe',
                     'qualified_reviewer_approved', 'independent_qd_pass',
                     'publication_authorized', 'paid_preparedness_product_verified'):
            self.assertIs(r[name], False)

    def test_deterministic_evidence_receipt(self):
        a = g.evaluate(*synthetic(), strict=False)
        b, m = synthetic()
        c = g.evaluate(dict(reversed(list(b.items()))),
                       dict(reversed(list(m.items()))), strict=False)
        self.assertEqual(a['review_receipt_sha256'], c['review_receipt_sha256'])

    def test_source_ids_all_attributed_to_metadata(self):
        r = g.evaluate(*synthetic(), strict=False)
        self.assertEqual(set().union(*(set(x['source_ids']) for x in r['claims_flagged_for_human_review'])),
                         {'food-fsis-jerky-qa', 'nchfp-jerky', 'food-fsis-jerky',
                          'food-ksu-jerky', 'hist-food-fsis-jerky',
                          'hist-food-nchfp-jerky', 'hist-food-marcy-prairie-traveler-text'})

    def test_missing_checkout_exits_nonzero_hard_hold(self):
        with tempfile.TemporaryDirectory() as directory:
            with redirect_stdout(StringIO()) as capture:
                status = g.main(['--repo', directory])
            self.assertEqual(status, 2)
            self.assertEqual(json.loads(capture.getvalue())['state'], 'INVALID_HARD_HOLD')

    def test_symlink_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'value.json'
            path.symlink_to('/etc/passwd')
            with self.assertRaises(ValueError):
                g.pinned(Path(directory), 'value.json', '0' * 40)

    def test_git_blob_actual_object_hash(self):
        data = b'abc\n'
        self.assertEqual(g.git_blob(data), '8baef1b4abc478178b004d62031cf7fe6db6f903')

    def test_invalid_original_blob_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'x.json'
            path.write_text('{}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'identity drift'):
                g.pinned(Path(directory), 'x.json', '0' * 40)

    def test_unfinished_html_rejected(self):
        b, m = synthetic()
        slug = 'pemmican-and-dried-meats'
        b[slug] += '<p>unclosed'
        with self.assertRaises(ValueError): g.evaluate(b, m, strict=False)

    def test_wrong_html_type_rejected(self):
        b, m = synthetic()
        b['safe-jerky-dehydration'] = None
        with self.assertRaises(ValueError): g.evaluate(b, m, strict=False)

    def test_extra_article_unapproved(self):
        b, m = synthetic()
        b['new-page'] = '<p>new content</p>'
        with self.assertRaises(ValueError): g.evaluate(b, m, strict=False)

    def test_missing_article_unapproved(self):
        b, m = synthetic()
        del m['pioneer-travel-rations']
        with self.assertRaises(ValueError): g.evaluate(b, m, strict=False)

    def test_html_parser_does_not_promote_citation_from_neighbour(self):
        b, m = synthetic()
        slug, _, anchor, ids = g.CLAIMS[0]
        b[slug] = b[slug].replace(anchor + ''.join('{{cite:' + x + '}}' for x in ids),
          anchor + '</p><p>' + ''.join('{{cite:' + x + '}}' for x in ids), 1)
        with self.assertRaisesRegex(ValueError, 'same-block source'):
            g.evaluate(b, m, strict=False)

    def test_wrong_section_rejected(self):
        b, m = synthetic()
        m['pioneer-travel-rations']['section'] = 'food'
        with self.assertRaises(ValueError): g.evaluate(b, m, strict=False)

    def test_block_parser_preserves_text_and_source_tokens(self):
        r = g.BlockReader()
        r.feed('<li>explanation <em>before</em> {{cite:source-id}}</li>')
        r.close()
        self.assertEqual(r.blocks, ['explanation before {{cite:source-id}}'])


def generate_mutation_tests():
    for index, (slug, label, anchor, ids) in enumerate(g.CLAIMS):
        def remove_anchor(self, slug=slug, anchor=anchor):
            b, m = synthetic()
            b[slug] = b[slug].replace(anchor, 'irrelevant deleted original claim', 1)
            with self.assertRaisesRegex(ValueError, 'claim anchor'):
                g.evaluate(b, m, strict=False)
        setattr(TestR173, f'test_{index:02}_claim_anchor_deletion', remove_anchor)

        def duplicate_anchor(self, slug=slug, anchor=anchor):
            b, m = synthetic()
            b[slug] += '<p>' + anchor + '</p>'
            with self.assertRaisesRegex(ValueError, 'ambiguous claim anchor'):
                g.evaluate(b, m, strict=False)
        setattr(TestR173, f'test_{index:02}_claim_anchor_duplicated', duplicate_anchor)

        def published(self, slug=slug):
            b, m = synthetic()
            m[slug]['status']['publish'] = 'published'
            with self.assertRaisesRegex(ValueError, 'authority changed'):
                g.evaluate(b, m, strict=False)
        setattr(TestR173, f'test_{index:02}_no_article_publication', published)

        def reviewer_claim(self, slug=slug):
            b, m = synthetic()
            m[slug]['safety_review']['reviewer'] = 'fabricated reviewer'
            with self.assertRaisesRegex(ValueError, 'authority changed'):
                g.evaluate(b, m, strict=False)
        setattr(TestR173, f'test_{index:02}_no_fabricated_reviewer', reviewer_claim)

        def source_removed(self, slug=slug, anchor=anchor, ids=ids):
            if not ids:
                self.skipTest('No citation required for explicitly non-instructional history label')
            b, m = synthetic()
            b[slug] = b[slug].replace('{{cite:' + ids[0] + '}}', '', 1)
            with self.assertRaisesRegex(ValueError, 'same-block source'):
                g.evaluate(b, m, strict=False)
        setattr(TestR173, f'test_{index:02}_source_removed', source_removed)

        def source_use_removed(self, slug=slug, ids=ids):
            if not ids:
                self.skipTest('No citation attached to historical no-recipe label')
            b, m = synthetic()
            del m[slug]['source_use'][ids[0]]
            with self.assertRaisesRegex(ValueError, 'article-level source-use'):
                g.evaluate(b, m, strict=False)
        setattr(TestR173, f'test_{index:02}_source_use_missing', source_use_removed)

    for label, needle in (
        ('historical_no_recipe', ' no method and no storage times are supplied.'),
        ('official_conflict', ' after drying bacteria become more heat resistant.'),
        ('pioneer_disagreement', ' before drying and after drying differ.'),
    ):
        def strip_qualifier(self, needle=needle):
            b, m = synthetic()
            for key in b: b[key] = b[key].replace(needle, '')
            with self.assertRaises(ValueError): g.evaluate(b, m, strict=False)
        setattr(TestR173, f'test_required_scope_{label}', strip_qualifier)


generate_mutation_tests()

if __name__ == '__main__':
    unittest.main()
