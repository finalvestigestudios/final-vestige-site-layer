"""Synthetic-only R230 tokenizer divergence regressions, not real export approval."""
import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'tools' / 'r230_html_tokenizer_state_hold.py'
SPEC = importlib.util.spec_from_file_location('r230_tokenizer_gate', SOURCE)
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)

WARNING = '<p>Independent safety/source and QD verification pending</p>'
BODY = '<article class="pa-body" id="pa-main">Household planning <sup class="pa-cite"><a href="#src-1">[1]</a></sup></article>'
SOURCE_SECTION = '<section class="pa-sources"><ol><li id="src-1"><a href="https://www.ready.gov/plan">Official source</a></li></ol></section>'
REVIEW = '<section class="pa-review">Independent review pending</section>'
PAGE = '<main>' + WARNING + BODY + SOURCE_SECTION + REVIEW + '</main>'
MODES = ('plaintext', 'xmp', 'noembed', 'noframes', 'frameset', 'frame',
         'listing', 'isindex', 'applet')
POSITIONS = (('before_body', BODY), ('before_sources', SOURCE_SECTION),
             ('before_review', REVIEW))


class R230TokenizerModes(unittest.TestCase):
    def reject(self, candidate):
        with self.assertRaisesRegex(ValueError, 'R230 unsupported tokenizer'):
            GATE.verify_tokenizer_states(candidate)

    def test_valid_draft_remains_hold(self):
        result = GATE.verify_tokenizer_states(PAGE)
        self.assertEqual(result['state'], 'DRAFT_HARD_HOLD')
        self.assertFalse(result['release_authorized'])
        self.assertEqual(result['unsupported_count'], 0)

    def test_wordpress_wrapper_stays_hold(self):
        self.assertEqual(GATE.verify_tokenizer_states('<!-- wp:html -->' + PAGE + '<!-- /wp:html -->')['state'], 'DRAFT_HARD_HOLD')

    def test_preview_wrapper_stays_hold(self):
        html = '<!doctype html><html><head><title>Preparedness draft</title></head><body>' + PAGE + '</body></html>'
        self.assertEqual(GATE.verify_tokenizer_states(html)['state'], 'DRAFT_HARD_HOLD')

    def test_html_entity_is_text(self):
        safe = PAGE.replace(SOURCE_SECTION, '&lt;plaintext&gt;' + SOURCE_SECTION)
        self.assertEqual(GATE.verify_tokenizer_states(safe)['state'], 'DRAFT_HARD_HOLD')

    def test_numeric_entity_is_text(self):
        safe = PAGE.replace(SOURCE_SECTION, '&#60;plaintext&#62;' + SOURCE_SECTION)
        self.assertEqual(GATE.verify_tokenizer_states(safe)['state'], 'DRAFT_HARD_HOLD')

    def test_comment_is_not_element(self):
        safe = PAGE.replace(SOURCE_SECTION, '<!-- <plaintext> -->' + SOURCE_SECTION)
        self.assertEqual(GATE.verify_tokenizer_states(safe)['state'], 'DRAFT_HARD_HOLD')

    def test_attribute_string_not_element(self):
        safe = PAGE.replace(SOURCE_SECTION, '<p data-text="&lt;plaintext&gt;">Example</p>' + SOURCE_SECTION)
        self.assertEqual(GATE.verify_tokenizer_states(safe)['state'], 'DRAFT_HARD_HOLD')

    def test_script_literal_not_element(self):
        safe = PAGE.replace(SOURCE_SECTION, '<script>const raw = "<plaintext>";</script>' + SOURCE_SECTION)
        self.assertEqual(GATE.verify_tokenizer_states(safe)['state'], 'DRAFT_HARD_HOLD')

    def test_style_literal_not_element(self):
        safe = PAGE.replace(SOURCE_SECTION, '<style>p::before {content:"<plaintext>"}</style>' + SOURCE_SECTION)
        self.assertEqual(GATE.verify_tokenizer_states(safe)['state'], 'DRAFT_HARD_HOLD')

    def test_other_valid_tags(self):
        safe = PAGE.replace(SOURCE_SECTION, '<pre>print(&quot;sample&quot;)</pre><br/><svg><path d="M1,1"/></svg>' + SOURCE_SECTION)
        self.assertEqual(GATE.verify_tokenizer_states(safe)['state'], 'DRAFT_HARD_HOLD')

    def test_invalid_input_none(self):
        with self.assertRaisesRegex(ValueError, 'invalid HTML draft'):
            GATE.verify_tokenizer_states(None)

    def test_invalid_input_bytes(self):
        with self.assertRaisesRegex(ValueError, 'invalid HTML draft'):
            GATE.verify_tokenizer_states(PAGE.encode())

    def test_invalid_input_blank(self):
        with self.assertRaisesRegex(ValueError, 'invalid HTML draft'):
            GATE.verify_tokenizer_states('  \n')

    def test_deceptive_closing_plaintext(self):
        self.reject(PAGE.replace(SOURCE_SECTION, '<plaintext></plaintext>' + SOURCE_SECTION))

    def test_deceptive_xmp_with_close(self):
        self.reject(PAGE.replace(SOURCE_SECTION, '<xmp><a href="#src-1">seeming link</a></xmp>' + SOURCE_SECTION))

    def test_multi_tag_diagnostic(self):
        with self.assertRaisesRegex(ValueError, 'plaintext, xmp'):
            GATE.verify_tokenizer_states('<xmp></xmp><plaintext>')


# Nine unsafe parser-mode triggers x three independent evidence positions x
# two spellings. Each test exercises the real module (not a mocked policy).
for i, tag in enumerate(MODES):
    for position, needle in POSITIONS:
        for spelling in ('plain', 'with_attrs'):
            def reject_mutant(self, tag=tag, needle=needle, spelling=spelling):
                start = '<' + tag + (' class="illustration" ' if spelling == 'with_attrs' else '') + '>'
                mutated = PAGE.replace(needle, start + needle, 1)
                self.assertNotEqual(mutated, PAGE)
                self.reject(mutated)
            setattr(R230TokenizerModes, 'test_mode_%02d_%s_%s' % (i, position, spelling), reject_mutant)


# Explicit syntactic variants—including HTMLParser's misleading self-close.
for i, tag in enumerate(MODES):
    for suffix in ('/>', ' />', ' data-x="1"/>'):
        def reject_selfclosing(self, tag=tag, suffix=suffix):
            self.reject(PAGE.replace(SOURCE_SECTION, '<' + tag + suffix + SOURCE_SECTION, 1))
        setattr(R230TokenizerModes, 'test_solidus_%02d_%02d' % (i, ('/>', ' />', ' data-x="1"/>').index(suffix)), reject_selfclosing)

if __name__ == '__main__':
    unittest.main()
