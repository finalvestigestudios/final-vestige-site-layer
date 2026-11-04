"""R110 isolated, synthetic adversarial evidence tests; no repository/source writes."""
import importlib.util
import json
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / 'tools' / 'r110_uncited_caveat_custody.py'
spec = importlib.util.spec_from_file_location('r110_uncited_caveat_custody', path)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

def b(s): return s.encode('utf-8')

BASE = '<article><h2>Water warning</h2><p>Read local advice before using.</p><p>Boiling might help {{cite:agency-water}}.</p><p>It does not remove every chemical.</p></article>'

class AdjacencyGateTests(unittest.TestCase):
    def test_same_content_does_not_claim_approval(self):
        r = g.compare(b(BASE), b(BASE))
        self.assertEqual(r['same_source_id_adjacent_uncited_context_changed_NOT_APPROVED'], [])
        self.assertFalse(r['may_publish'])
        self.assertFalse(r['qualified_safety_review_approved'])

    def test_previous_uncited_caveat_changed(self):
        x = BASE.replace('Read local advice before using.', 'Ignore local alerts.')
        r = g.compare(b(BASE), b(x))
        self.assertEqual(r['same_source_id_adjacent_uncited_context_changed_NOT_APPROVED'], ['agency-water'])
        self.assertEqual(r['visible_citations_before'], r['visible_citations_after'])

    def test_next_uncited_caveat_changed(self):
        x = BASE.replace('It does not remove every chemical.', 'It removes every chemical.')
        self.assertEqual(g.compare(b(BASE), b(x))['same_source_id_adjacent_uncited_context_changed_NOT_APPROVED'], ['agency-water'])

    def test_deleted_uncited_caveat(self):
        x = BASE.replace('<p>It does not remove every chemical.</p>', '')
        self.assertIn('agency-water', g.compare(b(BASE), b(x))['same_source_id_adjacent_uncited_context_changed_NOT_APPROVED'])

    def test_inserted_uncited_caveat(self):
        x = BASE.replace('<p>Boiling might', '<p>Handle with care.</p><p>Boiling might')
        self.assertIn('agency-water', g.compare(b(BASE), b(x))['same_source_id_adjacent_uncited_context_changed_NOT_APPROVED'])

    def test_uncited_distant_paragraph_ignored(self):
        s = '<p>A</p><p>B</p><p>C</p><p>Claim {{cite:x}}</p><p>D</p><p>E</p><p>F</p>'
        self.assertEqual(g.compare(b(s), b(s.replace('<p>A</p>','<p>ZZZ</p>')))['same_source_id_adjacent_uncited_context_changed_NOT_APPROVED'], [])

    def test_heading_boundary_blocks_previous_paragraph(self):
        s = '<p>Old context</p><h2>New section</h2><p>Cited {{cite:x}}</p>'
        self.assertEqual(g.compare(b(s), b(s.replace('Old context','New context')))['same_source_id_adjacent_uncited_context_changed_NOT_APPROVED'], [])

    def test_heading_itself_changes(self):
        s = '<h2>Use care</h2><p>Recommendation {{cite:x}}</p>'
        self.assertIn('x', g.compare(b(s), b(s.replace('Use care','Ignore all warnings')))['same_source_id_adjacent_uncited_context_changed_NOT_APPROVED'])

    def test_moved_neighborhood_detected(self):
        s = '<p>Caveat</p><p>Advice {{cite:x}}</p><p>Qualification</p>'
        z = '<p>Qualification</p><p>Advice {{cite:x}}</p><p>Caveat</p>'
        self.assertIn('x', g.compare(b(s), b(z))['same_source_id_adjacent_uncited_context_changed_NOT_APPROVED'])

    def test_warning_class_removal(self):
        s = '<div class="pa-warning"><p>Never.</p></div><p>Advice {{cite:x}}</p>'
        z = s.replace('pa-warning','pa-note')
        r = g.compare(b(s), b(z))
        self.assertIn('x', r['source_ids_with_adjacent_warning_presence_or_span_changed_NOT_APPROVED'])
        self.assertIn('x', r['same_source_id_adjacent_uncited_context_changed_NOT_APPROVED'])

    def test_new_warning_class(self):
        s = '<p>Precaution</p><p>Advice {{cite:x}}</p>'
        z = s.replace('<p>Precaution</p>','<p class="pa-warning">Precaution</p>')
        self.assertIn('x', g.compare(b(s), b(z))['source_ids_with_adjacent_warning_presence_or_span_changed_NOT_APPROVED'])

    def test_warning_role(self):
        s = '<p role="alert">Precaution</p><p>Advice {{cite:x}}</p>'
        z = s.replace(' role="alert"','')
        self.assertIn('x', g.compare(b(s), b(z))['source_ids_with_adjacent_warning_presence_or_span_changed_NOT_APPROVED'])

    def test_hidden_adjacent_warning_removal(self):
        s = '<p>Care</p><p>Advice {{cite:x}}</p>'
        z = s.replace('<p>Care</p>','<p hidden>Care</p>')
        self.assertIn('x', g.compare(b(s), b(z))['same_source_id_adjacent_uncited_context_changed_NOT_APPROVED'])

    def test_citation_in_html_comment_is_not_visible(self):
        r = g.inspect(b('<!-- {{cite:fake}} --><p>Advice {{cite:real}}</p>'))
        self.assertEqual(r['source_ids'], ['real'])
        self.assertEqual(r['comment_citations'], 1)

    def test_citation_in_attribute_not_visible(self):
        r = g.inspect(b('<p title="{{cite:fake}}">Advice {{cite:real}}</p>'))
        self.assertEqual(r['source_ids'], ['real'])
        self.assertEqual(r['attribute_citations'], 1)

    def test_suppressed_citation_not_visible(self):
        r = g.inspect(b('<script>{{cite:fake}}</script><p>Advice {{cite:real}}</p>'))
        self.assertEqual(r['source_ids'], ['real'])
        self.assertEqual(r['invisible_citations'], 1)

    def test_orphan_citation_flags_ambiguity(self):
        self.assertTrue(g.compare(b('{{cite:x}}'), b('{{cite:x}}'))['text_model_ambiguity_or_nontext_citations'])

    def test_malformed_marker_flags_ambiguity(self):
        self.assertTrue(g.compare(b('<p>{{cite:UPPER}}</p>'), b('<p>{{cite:UPPER}}</p>'))['text_model_ambiguity_or_nontext_citations'])

    def test_bad_html_flags_ambiguity(self):
        self.assertTrue(g.compare(b('<p>Advice {{cite:x}}'), b('<p>Advice {{cite:x}}'))['text_model_ambiguity_or_nontext_citations'])

    def test_cited_block_prevents_looking_past(self):
        x = '<p>Caveat</p><p>Other {{cite:y}}</p><p>Advice {{cite:x}}</p>'
        self.assertNotIn('x', g.compare(b(x), b(x.replace('Caveat','Revision')))['same_source_id_adjacent_uncited_context_changed_NOT_APPROVED'])

    def test_two_citations_same_block(self):
        x = '<p>Caveat</p><p>Advice {{cite:x}} and {{cite:y}}</p>'
        self.assertEqual(g.compare(b(x), b(x.replace('Caveat','Changed')))['same_source_id_adjacent_uncited_context_changed_NOT_APPROVED'], ['x','y'])

    def test_added_and_removed_source_ids(self):
        r = g.compare(b('<p>Claim {{cite:x}}</p>'),b('<p>Claim {{cite:y}}</p>'))
        self.assertEqual(r['source_ids_added'], ['y'])
        self.assertEqual(r['source_ids_removed'], ['x'])

    def test_no_source_not_approved(self):
        r = g.compare(b('<p>No cite</p>'),b('<p>changed</p>'))
        self.assertEqual(r['source_ids_in_both'], [])
        self.assertFalse(r['may_publish'])

    def test_unicode_change_caveat(self):
        x = '<p>Água advice.</p><p>Claim {{cite:x}}</p>'
        self.assertIn('x',g.compare(b(x),b(x.replace('Água','Agua')))['same_source_id_adjacent_uncited_context_changed_NOT_APPROVED'])

    def test_safe_content_is_never_exported(self):
        unique = 'VERY_SECRET_PRIVATE_HUMAN_NOTE'
        x = '<p>'+unique+'</p><p>Claim {{cite:x}}</p>'
        r = g.compare(b(x), b(x.replace(unique,'X')))
        self.assertNotIn(unique,json.dumps(r))
        self.assertNotIn('Claim',json.dumps(r))

    def test_not_bytes_raises(self):
        with self.assertRaises(g.Hold): g.inspect('not bytes')

    def test_oversized_raises(self):
        with self.assertRaises(g.Hold): g.inspect(b'x' * (g.MAX_BYTES+1))

    def test_non_utf8_raises(self):
        with self.assertRaises(g.Hold): g.inspect(b'\xff')

    def test_duplicate_citations_preserve_occurrences(self):
        r = g.inspect(b('<p>Care</p><p>X {{cite:x}} {{cite:x}}</p>'))
        self.assertEqual(len(r['source_adjacency']['x']),2)

    def test_whitespace_unchanged(self):
        x = '<p>Read warnings now</p><p>Advice {{cite:x}}</p>'
        self.assertEqual(g.compare(b(x),b(x.replace('Read warnings now','Read   warnings\nnow')))['same_source_id_adjacent_uncited_context_changed_NOT_APPROVED'],[])

    def test_entity_normalized(self):
        x = '<p>Fire &amp; smoke</p><p>Claim {{cite:x}}</p>'
        self.assertEqual(g.compare(b(x),b(x.replace('&amp;','&')))['same_source_id_adjacent_uncited_context_changed_NOT_APPROVED'],[])

    def test_no_extra_site_permissions(self):
        self.assertFalse(g.compare(b(BASE),b(BASE))['independent_QD_PASS'])

    def test_invalid_marker_in_attribute(self):
        self.assertTrue(g.inspect(b('<p title="{{cite:BAD}}">Actual {{cite:x}}</p>'))['malformed_markers'])

    def test_style_hidden_adjacent_still_hold(self):
        s = '<p class="pa-warning">Stop</p><p>Claim {{cite:x}}</p>'
        self.assertIn('x',g.compare(b(s),b(s.replace(' class="pa-warning"',' style="display:none"')))['same_source_id_adjacent_uncited_context_changed_NOT_APPROVED'])

# Forty-eight independent synthetic uncited-caveat edits with identical cited
# paragraph and exact same citation ID/count. No source or CMS fixtures touched.
_MUTATIONS = [
    'Ignore local water advisories', 'Boil-water alerts never matter',
    'Use indoor generators', 'Carbon monoxide is harmless',
    'Take extra medicine without advice', 'Treat floodwater as potable',
    'Never rotate stored food', 'No medical backup plan needed',
    'Skip sterile infant formula instructions', 'Use unsafe water for wound care',
    'Treat radioactive water by boiling', 'Use any household chemical',
    'Remove all protective equipment', 'No filtration standards apply',
    'Leave pets outside', 'Disable alarms during drills',
    'Discard prescription stock', 'Heat medicines without instructions',
    'Never heed evacuation orders', 'Drive through moving floodwater',
    'Eat food after unsafe storage', 'Improvise pressure canning',
    'Use raw meat without refrigeration', 'Historic recipes are always safe',
    'Share medication freely', 'Use a charcoal filter for pesticides',
    'Ignore boil/do-not-use distinction', 'Treat rainwater as sterile',
    'Drink seawater', 'Assume plastic is clean',
    'Never check local hazard map', 'Ignore flood contamination',
    'Remove your smoke detectors', 'Disable medical refrigeration',
    'Bathe in chemically contaminated water', 'Undercook preserved food',
    'Assume all sources agree', 'Skip certified processes',
    'Ignore emergency broadcasts', 'Do not use protective gloves',
    'All warnings are obsolete', 'Drink water of unknown origin',
    'Heat the home with an oven', 'Use a charcoal grill indoors',
    'Skip container sanitation', 'Ignore water quality tests',
    'No need to call a pharmacist', 'Do not consult local agencies',
]

def make_test(phrase):
    def test(self):
        revised = BASE.replace('Read local advice before using.', phrase)
        r = g.compare(b(BASE), b(revised))
        self.assertEqual(r['same_source_id_adjacent_uncited_context_changed_NOT_APPROVED'],['agency-water'])
        self.assertEqual(r['visible_citations_before'],r['visible_citations_after'])
        self.assertNotIn(phrase,json.dumps(r))
        self.assertFalse(r['may_publish'])
    return test

for index, phrase in enumerate(_MUTATIONS):
    setattr(AdjacencyGateTests, f'test_adversarial_uncited_caveat_{index:02d}', make_test(phrase))

if __name__ == '__main__':
    unittest.main()
