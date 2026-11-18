"""R469: synthetic mutation suite; passing tests never approve genuine advice."""
import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import unittest

SRC = pathlib.Path(__file__).resolve().parents[1] / 'tools/r469_citation_visibility_custody.py'
spec = importlib.util.spec_from_file_location('r469_visibility', SRC)
gate = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = gate
spec.loader.exec_module(gate)

BASE = '<section><h2>Contacts</h2><p>Keep a written contact list {{cite:ready-plan}}.</p><p>Ask local schools {{cite:school-policy}} before pickup.</p></section>'
IDS = ['ready-plan', 'school-policy']

class ExactBaseline(unittest.TestCase):
    def test_expected_citations(self):
        self.assertEqual(gate.audit(BASE, IDS)['citation_count'], 2)
    def test_expected_ids(self):
        self.assertEqual(gate.audit(BASE)['citation_ids'], IDS)
    def test_deterministic(self):
        self.assertEqual(gate.audit(BASE), gate.audit(BASE))
    def test_nonapproval(self):
        result = gate.audit(BASE)
        self.assertFalse(result['qualified_qd_pass'])
        self.assertFalse(result['may_publish'])
        self.assertFalse(result['computed_css_verified'])
    def test_nested_inline_markup(self):
        self.assertEqual(gate.audit('<p><em>Read {{cite:ready-plan}}</em></p>')['citation_count'], 1)
    def test_expanded_disclosure(self):
        self.assertEqual(gate.audit('<details open><summary>Sources</summary><p>Read {{cite:ready-plan}}</p></details>')['citation_count'], 1)
    def test_closed_disclosure_reported(self):
        self.assertEqual(gate.audit('<details><summary>Sources</summary><p>Read {{cite:ready-plan}}</p></details>')['closed_disclosures_review'], 1)
    def test_bare_text(self):
        self.assertEqual(gate.audit('Read {{cite:ready-plan}}')['citation_count'], 1)
    def test_void_tags(self):
        self.assertEqual(gate.audit('<p>Read<br/>{{cite:ready-plan}} <img src="safe.jpg"/></p>')['citation_count'], 1)
    def test_comment_without_citation(self):
        self.assertEqual(gate.audit('<p>Read {{cite:ready-plan}}</p><!-- end -->')['citation_count'], 1)
    def test_expected_order_mismatch(self):
        with self.assertRaises(gate.VisibilityHold):
            gate.audit(BASE, list(reversed(IDS)))
    def test_missing_file_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = subprocess.run([sys.executable, '-I', str(SRC), '--root', tmp], capture_output=True, text=True)
            self.assertEqual(p.returncode, 2)
            self.assertIn('FAILURE_HARD_HOLD', p.stdout)
    def test_invalid_non_string(self):
        with self.assertRaises(gate.VisibilityHold):
            gate.audit(None)
    def test_emtpy(self):
        with self.assertRaises(gate.VisibilityHold):
            gate.audit('  ')
    def test_missing_citation(self):
        with self.assertRaises(gate.VisibilityHold):
            gate.audit('<p>No source</p>')
    def test_preserves_distinct_shared_urls(self):
        self.assertEqual(gate.audit('<p>A {{cite:one}} B {{cite:two}}</p>')['citation_ids'], ['one', 'two'])

# Generate independently enumerated exact mutation methods; each is a separate
# unittest, rather than treating N subTests as N actual tests.
HIDDEN_WRAPPERS = {
    'hidden_boolean': '<div hidden>{}</div>',
    'hidden_false_still_boolean': '<div hidden="false">{}</div>',
    'inert_boolean': '<div inert>{}</div>',
    'aria_true': '<div aria-hidden="true">{}</div>',
    'aria_case': '<div aria-hidden="TRUE">{}</div>',
    'display_none': '<div style="display:none">{}</div>',
    'display_none_important': '<div style="display: none!important">{}</div>',
    'display_none_comment': '<div style="/* comment */display:none">{}</div>',
    'visibility_hidden': '<div style="visibility:hidden">{}</div>',
    'visibility_collapse': '<div style="visibility:collapse">{}</div>',
    'content_visibility_hidden': '<div style="content-visibility:hidden">{}</div>',
    'opacity_zero': '<div style="opacity:0">{}</div>',
    'opacity_decimal_zero': '<div style="opacity:0.0">{}</div>',
    'opacity_percent_zero': '<div style="opacity:0%">{}</div>',
    'hidden_nested': '<div hidden><p>{}</p></div>',
    'hidden_nested_inline': '<main><div aria-hidden="true"><span>{}</span></div></main>',
    'script': '<script>{}</script>',
    'style': '<style>{}</style>',
    'template': '<template>{}</template>',
    'noscript': '<noscript>{}</noscript>',
    'svg': '<svg><text>{}</text></svg>',
    'math': '<math><mtext>{}</mtext></math>',
    'iframe': '<iframe>{}</iframe>',
    'object': '<object>{}</object>',
    'canvas': '<canvas>{}</canvas>',
    'head': '<head>{}</head>',
    'title': '<title>{}</title>',
    'textarea': '<textarea>{}</textarea>',
}

ATTACK_MARKUP = {
    'comment_citation': '<p>Visible {{cite:ready-plan}}</p><!-- {{cite:other}} -->',
    'attr_citation': '<p title="{{cite:ready-plan}}">Visible {{cite:ready-plan}}</p>',
    'attr_only': '<p title="{{cite:ready-plan}}">Visible only</p>',
    'attribute_aria': '<span aria-label="{{cite:ready-plan}}">Visible text</span>',
    'data_src': '<div data-source="{{cite:ready-plan}}">Text</div>',
    'duplicate_attr': '<div aria-hidden="false" aria-hidden="true">{{cite:ready-plan}}</div>',
    'duplicate_style': '<p style="display:block;display:none">{{cite:ready-plan}}</p>',
    'malformed_style': '<p style="display none">{{cite:ready-plan}}</p>',
    'bad_aria': '<p aria-hidden="maybe">{{cite:ready-plan}}</p>',
    'unclosed': '<section><p>{{cite:ready-plan}}</p>',
    'mismatch': '<div><p>{{cite:ready-plan}}</div></p>',
    'stray_close': '</p><p>{{cite:ready-plan}}</p>',
    'extra_close': '<p>{{cite:ready-plan}}</p></div>',
    'doctype': '<!DOCTYPE html><p>{{cite:ready-plan}}</p>',
    'base': '<base href="https://example.net/"><p>{{cite:ready-plan}}</p>',
    'meta': '<meta charset="utf-8"><p>{{cite:ready-plan}}</p>',
    'link': '<link rel="stylesheet" href="x"><p>{{cite:ready-plan}}</p>',
    'upper_cite': '<p>{{cite:READY-PLAN}}</p>',
    'spaced_cite': '<p>{{ cite:ready-plan }}</p>',
    'spaced_colon': '<p>{{cite :ready-plan}}</p>',
    'unknown_case': '<p>{{CITE:ready-plan}}</p>',
    'citation_in_style_css': '<style>p{content:"{{cite:ready-plan}}"}</style>',
    'split_citation': '<p>{{<strong>cite:ready-plan</strong>}}</p>',
    'noncanonical_prefix': '<p>{{  cite:ready-plan}}</p>',
    'single_citation_id_mismatch': '<p>{{cite:ready-plan}}</p>',
}

class VisibilityMutations(unittest.TestCase):
    pass

def _hidden_test(name, pattern):
    def test(self):
        with self.assertRaises(gate.VisibilityHold, msg=name):
            gate.audit(pattern.format('See {{cite:ready-plan}}'))
    return test

for name, pattern in HIDDEN_WRAPPERS.items():
    setattr(VisibilityMutations, 'test_hidden_' + name, _hidden_test(name, pattern))

class MarkupMutations(unittest.TestCase):
    pass

def _markup_test(name, body):
    def test(self):
        with self.assertRaises(gate.VisibilityHold, msg=name):
            gate.audit(body, IDS if name == 'single_citation_id_mismatch' else None)
    return test

for name, body in ATTACK_MARKUP.items():
    setattr(MarkupMutations, 'test_attack_' + name, _markup_test(name, body))

class MeaningfulAllowedCases(unittest.TestCase):
    pass

ALLOWED = {
    'aria_false': '<p aria-hidden="false">{{cite:ready-plan}}</p>',
    'display_block': '<p style="display:block">{{cite:ready-plan}}</p>',
    'visibility_visible': '<p style="visibility:visible">{{cite:ready-plan}}</p>',
    'opacity_one': '<p style="opacity:1">{{cite:ready-plan}}</p>',
    'noncite_hidden': '<div hidden>No citation</div><p>{{cite:ready-plan}}</p>',
    'noncite_script': '<script>const x=1;</script><p>{{cite:ready-plan}}</p>',
    'noncite_template': '<template>No citation</template><p>{{cite:ready-plan}}</p>',
    'noncite_svg': '<svg><title>icon</title></svg><p>{{cite:ready-plan}}</p>',
    'emphasis': '<p><em>{{cite:ready-plan}}</em></p>',
    'details': '<details><summary>View source</summary><p>{{cite:ready-plan}}</p></details>',
    'br': '<p>Line<br>{{cite:ready-plan}}</p>',
    'adjacent': '<p>{{cite:ready-plan}}{{cite:school-policy}}</p>',
}

def _allowed_test(body):
    def test(self):
        self.assertTrue(gate.audit(body)['citation_count'] >= 1)
    return test
for name, body in ALLOWED.items():
    setattr(MeaningfulAllowedCases, 'test_allowed_' + name, _allowed_test(body))

if __name__ == '__main__':
    unittest.main()
