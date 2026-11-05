"""R152 adversarial custody tests; no network and no live or CMS writes."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'tools' / 'r152_jerky_alias_gate.py'
spec = importlib.util.spec_from_file_location('r152_jerky_alias_gate', SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def originals(n=7, total=46):
    # Mixed citations, unmodified text, exact number of source-occurrence slots.
    assert n <= total
    a = ''.join(f'<li>Historical caution {i}. {{{{cite:{m.OLD}}}}}</li>\n' for i in range(n))
    a += ''.join(f'<li>Other reading {i}. {{{{cite:hist-food-fsis-jerky}}}}</li>\n' for i in range(total-n))
    return a.encode(), a.replace('{{cite:' + m.OLD + '}}', '{{cite:' + m.NEW + '}}').encode()


def sources():
    url = 'https://nchfp.uga.edu/how/dry/recipes/jerky'
    return {
        'preparedness/sources/register.json': json.dumps({'sources': [
            {'id': m.NEW, 'url': url, 'title': 'Jerky safety',
             'publisher': 'NCHFP', 'human_link_check': False}]}).encode(),
        'preparedness/sources/fragments/food.json': json.dumps({'sources': [
            {'id': m.NEW, 'url': url, 'title': 'Jerky', 'publisher': 'NCHFP',
             'supports': 'Drying meat guidance with specific instructions.',
             'human_link_check': False, 'verified_on': '2026-10-29'}]}).encode(),
        'preparedness/sources/fragments/hist-food.json': json.dumps({'sources': [
            {'id': m.OLD, 'url': url + '/', 'title': 'Historical jerky',
             'publisher': 'NCHFP', 'supports': 'Two weeks in sealed container.',
             'human_link_check': False, 'verified_on': '2026-10-29'}]}).encode(),
    }


class ArticleChecks(unittest.TestCase):
    def test_expected_pemmican(self):
        a, b = originals()
        res = m.assess_article(a, b, 7, 46)
        self.assertEqual((res['substitutions'], res['citations'], len(res['contexts'])), (7, 46, 7))
        self.assertEqual(res['decision'], 'PENDING_HUMAN_SOURCE_REVIEW')

    def test_expected_rations(self):
        a, b = originals(1, 39)
        self.assertEqual(m.assess_article(a, b, 1, 39)['substitutions'], 1)

    def test_word_change_rejected(self):
        a, b = originals()
        with self.assertRaises(ValueError): m.assess_article(a, b.replace(b'caution', b'danger'), 7, 46)

    def test_crlf_variation_is_only_allowed_format_difference(self):
        a, b = originals(1, 39)
        new = b.replace(b"\n", b"\r\n")
        r = m.assess_article(a, new, 1, 39)
        self.assertTrue(r["eol_only_variation"])

    def test_html_change_rejected(self):
        a, b = originals()
        with self.assertRaises(ValueError): m.assess_article(a, b.replace(b'<li>', b'<p>'), 7, 46)

    def test_removed_citation_rejected(self):
        a, b = originals()
        with self.assertRaises(ValueError): m.assess_article(a, b.replace(b'{{cite:nchfp-jerky}}', b'', 1), 7, 46)

    def test_new_wrong_citation_rejected(self):
        a, b = originals()
        with self.assertRaises(ValueError): m.assess_article(a, b.replace(b'hist-food-fsis-jerky', b'other-source', 1), 7, 46)

    def test_reordered_citations_rejected(self):
        a, b = originals()
        b = b.replace(b'{{cite:nchfp-jerky}}', b'{{cite:hist-food-fsis-jerky}}', 1)
        with self.assertRaises(ValueError): m.assess_article(a, b, 7, 46)

    def test_partial_alias_migration_rejected(self):
        a, b = originals()
        with self.assertRaises(ValueError): m.assess_article(a, b.replace(b'{{cite:nchfp-jerky}}', b'{{cite:hist-food-nchfp-jerky}}', 1), 7, 46)

    def test_other_alias_rejected(self):
        a, b = originals()
        with self.assertRaises(ValueError): m.assess_article(a, b.replace(b'nchfp-jerky', b'nchfp-jerky-v2'), 7, 46)

    def test_mismatched_totals_rejected(self):
        a, b = originals()
        with self.assertRaises(ValueError): m.assess_article(a, b, 7, 47)

    def test_mismatched_count_rejected(self):
        a, b = originals()
        with self.assertRaises(ValueError): m.assess_article(a, b, 6, 46)

    def test_extra_markup_rejected(self):
        a, b = originals()
        with self.assertRaises(ValueError): m.assess_article(a, b + b'<script>alert(1)</script>', 7, 46)

    def test_unicode_decode_rejected(self):
        a, b = originals()
        with self.assertRaises(UnicodeError): m.assess_article(a, b'\xff' + b, 7, 46)

    def test_unclosed_citation_rejected(self):
        a, b = originals()
        with self.assertRaises(ValueError): m.assess_article(a, b.replace(b'{{cite:nchfp-jerky}}', b'{{cite:nchfp-jerky}', 1), 7, 46)

    def test_malformed_pinned_rejected(self):
        a, b = originals()
        with self.assertRaises(ValueError): m.assess_article(a.replace(b'{{cite:', b'{{CITE:', 1), b, 7, 46)

    def test_reading_context_has_line(self):
        a, _ = originals()
        details = m.review_contexts(a)
        self.assertEqual(details[0]['line'], 1)
        self.assertEqual(details[-1]['line'], 7)
        self.assertEqual(len(details), 7)

    def test_html_is_stripped_from_excerpt(self):
        details = m.review_contexts(b'<li>Meat <b>limits</b>{{cite:hist-food-nchfp-jerky}}</li>')
        self.assertNotIn('<li>', details[0]['excerpt'])

    def test_git_blob_matches_real_sha(self):
        self.assertEqual(m.git_blob(b'hello\n'), 'ce013625030ba8dba906f756967f9e9ca394464a')

    def test_git_ref_validation(self):
        with self.assertRaises(ValueError): m.read_git('.', 'main', 'preparedness/anything')

    def test_git_path_escape_rejected(self):
        with self.assertRaises(ValueError): m.read_git('.', m.CANDIDATE, 'preparedness/../config')

    def test_git_path_other_tree_rejected(self):
        with self.assertRaises(ValueError): m.read_git('.', m.CANDIDATE, 'website/config')


class SourceChecks(unittest.TestCase):
    def test_authentic_variant_shape(self):
        r = m.review_sources(sources())
        self.assertTrue(r['same_url_is_not_same_evidence'])
        self.assertEqual(len(r['origins']), 3)
        self.assertEqual(r['review'], 'PENDING_INDEPENDENT_HUMAN_SOURCE_AND_FOOD_SAFETY_REVIEW')

    def test_missing_doc_rejected(self):
        x = sources(); x.pop('preparedness/sources/register.json')
        with self.assertRaises(ValueError): m.review_sources(x)

    def test_duplicate_id_rejected(self):
        x = sources(); p = 'preparedness/sources/register.json'; d = json.loads(x[p]); d['sources'].append(d['sources'][0]); x[p] = json.dumps(d).encode()
        with self.assertRaises(ValueError): m.review_sources(x)

    def test_no_human_claim_true(self):
        x = sources(); p = 'preparedness/sources/fragments/food.json'; d = json.loads(x[p]); d['sources'][0]['human_link_check'] = True; x[p] = json.dumps(d).encode()
        with self.assertRaises(ValueError): m.review_sources(x)

    def test_no_human_claim_missing(self):
        x = sources(); p = 'preparedness/sources/fragments/food.json'; d = json.loads(x[p]); d['sources'][0].pop('human_link_check'); x[p] = json.dumps(d).encode()
        with self.assertRaises(ValueError): m.review_sources(x)

    def test_missing_explanation_rejected(self):
        x = sources(); p = 'preparedness/sources/fragments/food.json'; d = json.loads(x[p]); d['sources'][0].pop('supports'); x[p] = json.dumps(d).encode()
        with self.assertRaises(ValueError): m.review_sources(x)

    def test_missing_historical_explanation_rejected(self):
        x = sources(); p = 'preparedness/sources/fragments/hist-food.json'; d = json.loads(x[p]); d['sources'][0].pop('supports'); x[p] = json.dumps(d).encode()
        with self.assertRaises(ValueError): m.review_sources(x)

    def test_unapproved_base_reading_rejected(self):
        x = sources(); p = 'preparedness/sources/register.json'; d = json.loads(x[p]); d['sources'][0]['supports'] = 'new unreviewed'; x[p] = json.dumps(d).encode()
        with self.assertRaises(ValueError): m.review_sources(x)

    def test_missing_id_rejected(self):
        x = sources(); p = 'preparedness/sources/fragments/hist-food.json'; d = json.loads(x[p]); d['sources'][0]['id'] = m.NEW; x[p] = json.dumps(d).encode()
        with self.assertRaises(ValueError): m.review_sources(x)

    def test_invalid_json_rejected(self):
        x = sources(); x['preparedness/sources/register.json'] = b'{invalid'
        with self.assertRaises(json.JSONDecodeError): m.review_sources(x)

    def test_missing_array_rejected(self):
        x = sources(); x['preparedness/sources/register.json'] = b'{}'
        with self.assertRaises(ValueError): m.review_sources(x)

    def test_url_trailing_slash_grouping_only(self):
        self.assertEqual(m.canon_for_grouping('https://nchfp.uga.edu/how/dry/recipes/jerky/'),
                         m.canon_for_grouping('https://nchfp.uga.edu/how/dry/recipes/jerky'))

    def test_url_wrong_domain_rejected(self):
        with self.assertRaises(ValueError): m.canon_for_grouping('https://evil.example/how/dry/recipes/jerky')

    def test_url_wrong_path_rejected(self):
        with self.assertRaises(ValueError): m.canon_for_grouping('https://nchfp.uga.edu/how/dry/recipes/other')

    def test_url_query_rejected(self):
        with self.assertRaises(ValueError): m.canon_for_grouping('https://nchfp.uga.edu/how/dry/recipes/jerky?x=1')

    def test_url_non_https_rejected(self):
        with self.assertRaises(ValueError): m.canon_for_grouping('http://nchfp.uga.edu/how/dry/recipes/jerky')

    def test_url_non_string_rejected(self):
        with self.assertRaises(ValueError): m.canon_for_grouping(None)

    def test_alias_record_similarities_remain_unapproved(self):
        x = sources(); p = 'preparedness/sources/fragments/food.json'; d = json.loads(x[p]); d['sources'][0].update(json.loads(x['preparedness/sources/register.json'])['sources'][0]); x[p] = json.dumps(d).encode()
        self.assertEqual(m.review_sources(x)['review'],
                         'PENDING_INDEPENDENT_HUMAN_SOURCE_AND_FOOD_SAFETY_REVIEW')


class RunnerChecks(unittest.TestCase):
    def test_main_fails_closed_without_checkout(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(m.main(['--repo', td]), 2)

    def test_git_source_identities_are_full_40_sha(self):
        for sha in list(m.SOURCES.values()) + list(sum((list(x) for x in m.BLOBS.values()), [])):
            self.assertTrue(m.SHA.fullmatch(sha))

    def test_source_count_exacts(self):
        self.assertEqual(sum(x[0] for x in m.BODIES.values()), 8)

    def test_no_automatic_approval_api(self):
        self.assertFalse(any(n.startswith('approve') for n in dir(m)))

    def test_report_never_created_unrequested(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(m.main(['--repo', td]), 2)
            self.assertEqual(list(Path(td).iterdir()), [])


# Expand the source mutation matrix into independent named tests, rather than
# one broad loop that can conceal incomplete execution.
for origin, path in [('base', 'preparedness/sources/register.json'),
                     ('food', 'preparedness/sources/fragments/food.json'),
                     ('hist_food', 'preparedness/sources/fragments/hist-food.json')]:
    for field, bad in [('url', 'https://example.com/no'),
                       ('human_link_check', True),
                       ('id', 'unverified-alias')]:
        def make_test(file_path=path, field_name=field, bad_value=bad):
            def test(self):
                x = sources(); j = json.loads(x[file_path]); j['sources'][0][field_name] = bad_value
                x[file_path] = json.dumps(j).encode()
                with self.assertRaises(ValueError): m.review_sources(x)
            return test
        setattr(SourceChecks, f'test_matrix_{origin}_{field}', make_test())


if __name__ == '__main__':
    unittest.main()
