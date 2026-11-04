"""Self-contained synthetic/adversarial R109 tests, no repository writes."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('r109_citation_context_custody', Path(__file__).resolve().parents[1] / 'tools' / 'r109_citation_context_custody.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def b(s):
    return s.encode('utf-8')


BASE = '<article><p>Boiling may reduce microbes {{cite:cdc-water}}.</p><p>Follow local alerts.</p></article>'


class ContextReviewTests(unittest.TestCase):
    def test_stable_html(self):
        r=g.compare(b(BASE),b(BASE))
        self.assertEqual(r['unchanged_citation_id_changed_claim_neighborhood_NOT_APPROVED'],[])
        self.assertFalse(r['may_publish'])

    def test_changed_claim_with_same_source_id(self):
        r=g.compare(b(BASE),b(BASE.replace('may reduce microbes','removes every chemical')))
        self.assertEqual(r['unchanged_id_same_count_changed_context_NOT_APPROVED'],['cdc-water'])
        self.assertTrue(r['all_revision_claims_need_human_review'])

    def test_changed_unrelated_paragraph_not_misattributed(self):
        r=g.compare(b(BASE),b(BASE.replace('Follow local alerts.','Store supplies.')))
        self.assertEqual(r['unchanged_citation_id_changed_claim_neighborhood_NOT_APPROVED'],[])

    def test_changed_source_marker(self):
        r=g.compare(b(BASE),b(BASE.replace('cdc-water','cdc-new')))
        self.assertEqual(r['citation_ids_added'],['cdc-new'])
        self.assertEqual(r['citation_ids_removed'],['cdc-water'])

    def test_same_count_changed_safety_warning(self):
        a='<div class="pa-alert"><p>Do not drink it {{cite:cdc-water}}.</p></div>'
        z=a.replace('Do not drink it','Drink it immediately')
        r=g.compare(b(a),b(z))
        self.assertTrue(r['warning_text_changed_requires_review'])
        self.assertIn('cdc-water',r['unchanged_id_same_count_changed_context_NOT_APPROVED'])

    def test_comment_citation_not_visible(self):
        s='<!-- {{cite:fake}} --><p>Actually {{cite:real}}</p>'
        r=g.inspect(b(s))
        self.assertEqual(r['comment_citations'],{'fake':1})
        self.assertEqual(set(r['citation_context_sha256']),{'real'})

    def test_attribute_citation_not_visible(self):
        s='<p title="{{cite:fake}}">See {{cite:real}}</p>'
        r=g.inspect(b(s))
        self.assertEqual(r['attribute_citations'],{'fake':1})
        self.assertEqual(set(r['citation_context_sha256']),{'real'})

    def test_script_citation_not_visible(self):
        s='<script>const fake="{{cite:fake}}";</script><p>{{cite:real}}</p>'
        r=g.inspect(b(s))
        self.assertEqual(r['suppressed_citations'],{'fake':1})
        self.assertEqual(set(r['citation_context_sha256']),{'real'})

    def test_hidden_text_not_visible(self):
        s='<p aria-hidden="true">{{cite:fake}}</p><p>{{cite:real}}</p>'
        r=g.inspect(b(s))
        self.assertEqual(r['suppressed_citations'],{'fake':1})
        self.assertEqual(set(r['citation_context_sha256']),{'real'})

    def test_style_hidden_text_not_visible(self):
        s='<p style="display:none">{{cite:fake}}</p><p>{{cite:real}}</p>'
        r=g.inspect(b(s))
        self.assertEqual(r['suppressed_citations'],{'fake':1})

    def test_marker_split_by_inline_tags_is_reconstructed(self):
        s='<p>{{ci<strong>te:cdc-water}}</strong></p>'
        r=g.inspect(b(s))
        self.assertIn('cdc-water',r['citation_context_sha256'])

    def test_malformed_marker_sets_ambiguity(self):
        r=g.inspect(b('<p>{{cite:BAD}}</p>'))
        self.assertGreater(r['malformed_tokens'],0)

    def test_broken_html_sets_ambiguity(self):
        r=g.inspect(b('<p>Hi {{cite:good}}</section>'))
        self.assertGreater(r['html_structure_ambiguities'],0)

    def test_article_content_never_in_result(self):
        r=g.compare(b(BASE),b(BASE.replace('may reduce microbes','UNIQUE_PRIVATE_SECRET')))
        self.assertNotIn('UNIQUE_PRIVATE_SECRET',json.dumps(r))
        self.assertNotIn('Boiling',json.dumps(r))

    def test_bad_utf8_is_hold(self):
        with self.assertRaises(g.Hold): g.inspect(b'\xff')

    def test_non_bytes_rejected(self):
        with self.assertRaises(g.Hold): g.inspect('abc')

    def test_too_long_rejected(self):
        with self.assertRaises(g.Hold): g.inspect(b'x'*(g.MAX_BYTES+1))

    def test_zero_citation_still_hold(self):
        r=g.compare(b('<p>Clean</p>'),b('<p>changed</p>'))
        self.assertEqual(r['citation_ids_added'],[])
        self.assertFalse(r['may_publish'])

    def test_root_context_unwrapped_citation(self):
        r=g.inspect(b('Warning {{cite:source-1}}'))
        self.assertIn('source-1',r['citation_context_sha256'])

    def test_alternative_link_not_citation(self):
        r=g.inspect(b('<p><a href="https://example.org/">Read</a></p>'))
        self.assertEqual(r['visible_token_count_text_model'],0)

    def test_unicode_text_drift(self):
        x='<p>à — water {{cite:a}}</p>'
        y='<p>á — water {{cite:a}}</p>'
        self.assertIn('a',g.compare(b(x),b(y))['unchanged_id_same_count_changed_context_NOT_APPROVED'])

    def test_text_is_not_safety_approval(self):
        r=g.compare(b(BASE),b(BASE))
        self.assertTrue(r['evidence_is_not_a_safety_verdict'])

    def test_duplicate_source_id_instances(self):
        x='<p>A {{cite:a}} and B {{cite:a}}</p>'
        r=g.inspect(b(x))
        self.assertEqual(len(r['citation_context_sha256']['a']),2)

    def test_context_ends_at_paragraph(self):
        a='<p>Claim {{cite:a}}</p><p>Other</p>'
        z=a.replace('Other','Unrelated')
        self.assertFalse(g.compare(b(a),b(z))['unchanged_id_same_count_changed_context_NOT_APPROVED'])

    def test_change_same_id_in_second_paragraph(self):
        a='<p>First {{cite:a}}</p><p>Second {{cite:a}}</p>'
        z=a.replace('Second','Third')
        self.assertEqual(g.compare(b(a),b(z))['unchanged_id_same_count_changed_context_NOT_APPROVED'],['a'])

    def test_warning_nested_div(self):
        a='<div class="pa-warning"><p>Never try it {{cite:a}}</p></div>'
        z=a.replace('Never','Always')
        self.assertTrue(g.compare(b(a),b(z))['warning_text_changed_requires_review'])

    def test_no_html_structure_mismatch(self):
        self.assertEqual(g.inspect(b(BASE))['html_structure_ambiguities'],0)

    def test_html_entity_normalized(self):
        x='<p>Water &amp; ice {{cite:a}}</p>'
        z='<p>Water & ice {{cite:a}}</p>'
        self.assertEqual(g.compare(b(x),b(z))['unchanged_id_same_count_changed_context_NOT_APPROVED'],[])

    def test_whitespace_robustness(self):
        x='<p>Water   microbes {{cite:a}}</p>'
        z='<p>Water\n microbes {{cite:a}}</p>'
        self.assertEqual(g.compare(b(x),b(z))['unchanged_id_same_count_changed_context_NOT_APPROVED'],[])

    def test_comment_in_same_paragraph_ignored(self):
        x='<p>Water <!-- one --> is safe {{cite:a}}</p>'
        z='<p>Water <!-- two --> is safe {{cite:a}}</p>'
        self.assertEqual(g.compare(b(x),b(z))['unchanged_id_same_count_changed_context_NOT_APPROVED'],[])

    def test_citation_ordinal_count_drift(self):
        x='<p>One {{cite:a}}</p>'
        z='<p>One {{cite:a}} {{cite:a}}</p>'
        self.assertEqual(g.compare(b(x),b(z))['same_id_citation_occurrence_count_changed'],['a'])

    def test_missing_marker(self):
        x='<p>One {{cite:a}}</p>'
        z='<p>One</p>'
        self.assertEqual(g.compare(b(x),b(z))['citation_ids_removed'],['a'])

    def test_ignored_hidden_citation_requires_attention(self):
        x='<p>One {{cite:a}}</p>'
        z='<p hidden>One {{cite:a}}</p>'
        r=g.compare(b(x),b(z))
        self.assertIn('a',r['citation_ids_removed'])
        self.assertEqual(r['hidden_or_nontext_citations_after']['suppressed_citations'],{'a':1})

    def test_empty_data(self):
        self.assertEqual(g.inspect(b'')['visible_token_count_text_model'],0)

    def test_structural_missing_tag_in_diff(self):
        x='<p>Claim {{cite:a}}</p>'
        y='<p>Claim {{cite:a}}'
        self.assertTrue(g.compare(b(x),b(y))['structural_ambiguity_or_malformed_token'])

    def test_safety_tag_marker_only_not_approval(self):
        x='<span class="pa-tag--unc">Not validated</span>'
        r=g.inspect(b(x))
        self.assertEqual(len(r['warning_text_sha256']),1)


# Distinct, named adversarial tests: every mutation keeps the source ID and
# citation count but changes the associated claim, which R108 counts miss.
_MUTATIONS = [
    'All chemicals are removed', 'Even gasoline is safe', 'Ignore alerts',
    'Always drink floodwater', 'No testing is necessary', 'Use any bleach',
    'Never call emergency services', 'Smoke is harmless', 'Water is sterile',
    'Do not boil water', 'Boiling removes radiation', 'Every source is interchangeable',
    'Use a generator indoors', 'Discard the regulator warning', 'Cure meat overnight',
    'Ignore prescription directions', 'Try untested mixtures', 'Never filter',
    'Skip the boil advisory', 'Cold smoking makes it safe', 'Use contaminated storage',
    'All saltwater is potable', 'Improvised canning is enough', 'Ignore official guidance',
    'Guess an iodine dose', 'Ignore the baby formula warning', 'Smoke indoors',
    'Freeze all medicines', 'Use expired household bleach', 'Drinking rainwater is always safe',
    'Contaminated soil is safe', 'Store food in heat indefinitely', 'No extension validation needed',
    'Do not use local alerts', 'Share medical devices freely', 'Pesticides are removable by boiling',
    'No carbon monoxide hazard', 'Plastic containers need no cleaning', 'Chemicals vanish after boiling',
    'Water-bath can meat', 'Always trust historic food recipes', 'Safety review is completed',
    'No water calculations are needed', 'Pickle any food without testing',
]


def _make_claim_test(phrase):
    def test(self):
        updated=BASE.replace('Boiling may reduce microbes',phrase)
        d=g.compare(b(BASE),b(updated))
        self.assertEqual(d['unchanged_id_same_count_changed_context_NOT_APPROVED'],['cdc-water'])
        self.assertFalse(d['may_publish'])
        self.assertEqual(d['visible_citations_before_text_model'],d['visible_citations_after_text_model'])
        self.assertNotIn(phrase,json.dumps(d))
    return test

for index, phrase in enumerate(_MUTATIONS):
    setattr(ContextReviewTests, f'test_same_id_changed_claim_{index:02d}', _make_claim_test(phrase))

if __name__=='__main__':
    unittest.main()
