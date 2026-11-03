"""R94 synthetic/adversarial original-to-rendered reading-depth custody checks."""
from __future__ import annotations

import sys
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import r94_body_custody as target  # noqa: E402


def fixture(count=6):
    original = "\n".join(
        f'<p id="item-{i}"><strong>Instruction {i}.</strong> '
        f'Do not replace reading {i} with unsupported advice: {i * 4} units. '
        f'{{{{cite:s{i}}}}}</p>' for i in range(1, count + 1))
    rendered = "\n".join(
        f'<p id="item-{i}"><strong>Instruction {i}.</strong> '
        f'Do not replace reading {i} with unsupported advice: {i * 4} units. '
        f'<sup class="pa-cite"><a href="#src-{i}">[{i}]</a></sup></p>'
        for i in range(1, count + 1))
    return original, '<article><div class="pa-body">' + rendered + '</div></article>'


class EditorReadingDepth(unittest.TestCase):
    def setUp(self):
        self.src, self.out = fixture()
        self.root = Path(tempfile.gettempdir())

    def check(self, out=None, src=None):
        return target.audit_body("synthetic-guide", src or self.src,
                                 out if out is not None else self.out,
                                 self.root)

    def test_control_six_literal_blocks(self):
        result = self.check()
        self.assertEqual(result["original_reading_blocks"], 12)
        self.assertEqual(result["release_state"], "HOLD")
        self.assertIs(result["may_publish"], False)

    def test_fingerprint_is_deterministic(self):
        self.assertEqual(self.check(), self.check())

    def test_link_label_token_preserved(self):
        orig = '<p>Read {{link:other-guide|the complete guide}} before deciding.</p>'
        html = '<div class="pa-body"><p>Read <a href="/preparedness/water/other-guide/">the complete guide</a> before deciding.</p></div>'
        self.assertEqual(target.audit_body("synthetic-guide", orig, html, self.root)["original_reading_blocks"], 1)

    def test_link_label_changed_is_blocked(self):
        orig = '<p>Read {{link:other-guide|the complete guide}} before deciding.</p>'
        html = '<div class="pa-body"><p>Read something else before deciding.</p></div>'
        with self.assertRaises(target.CustodyGate):
            target.audit_body("synthetic-guide", orig, html, self.root)

    def test_html_entity_equivalence_is_accepted(self):
        orig = '<p>5 &times; 3 &amp; 4</p>'
        out = '<div class="pa-body"><p>5 × 3 &amp; 4</p></div>'
        self.assertEqual(target.audit_body("x", orig, out, self.root)["original_reading_blocks"], 1)

    def test_missing_body_is_blocked(self):
        with self.assertRaises(target.CustodyGate):
            target.audit_body("x", "", self.out, self.root)

    def test_incorrect_slug_is_blocked(self):
        with self.assertRaises(target.CustodyGate):
            target.audit_body("../x", self.src, self.out, self.root)

    def test_draft_outside_body_cannot_substitute_text(self):
        out = self.out.replace('Instruction 1.', 'Instruction LOST.', 1)
        out = out.replace("</article>", '<p>Instruction 1.</p></article>')
        with self.assertRaises(target.CustodyGate):
            self.check(out)

    def test_missing_body_wrapper_blocked(self):
        with self.assertRaises(target.CustodyGate):
            self.check(self.out.replace('class="pa-body"', 'class="pa-unrelated"'))

    def test_duplicate_body_wrapper_blocked(self):
        extra = '<div class="pa-body"><p>Full duplicate.</p></div>'
        with self.assertRaises(target.CustodyGate):
            self.check(self.out.replace('</article>', extra + '</article>'))

    def test_unclosed_original_tag_blocked(self):
        with self.assertRaises(target.CustodyGate):
            self.check(src='<p>Not closed')

    def test_hidden_original_prose_dropped_blocked(self):
        with self.assertRaises(target.CustodyGate):
            self.check(self.out.replace('Do not replace reading 4', 'Replace reading 4'))

    def test_reordered_source_blocks_blocked(self):
        out = self.out.replace('Instruction 1.', 'SENTINEL').replace('Instruction 2.', 'Instruction 1.').replace('SENTINEL', 'Instruction 2.')
        with self.assertRaises(target.CustodyGate):
            self.check(out)

    def test_source_no_citations_still_text_check(self):
        orig = '<h2>Historical limits</h2><p>Unknown safety outcome.</p>'
        out = '<div class="pa-body"><h2>Historical limits</h2><p>Unknown safety outcome.</p></div>'
        self.assertEqual(target.audit_body("x", orig, out, self.root)["original_reading_blocks"], 2)

    def test_inline_script_exact_hash_preserved(self):
        orig = '<p>Original notice</p><script>function x(){return 123;}</script>'
        out = '<div class="pa-body">' + orig + '</div>'
        result = target.audit_body('x', orig, out, self.root)
        self.assertEqual(result['literal_script_blocks'], 1)
        with self.assertRaises(target.CustodyGate):
            target.audit_body('x', orig, out.replace('return 123;', 'return 456;'), self.root)

    def test_inline_script_file_substitution_does_not_execute(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/'tools').mkdir()
            (root/'tools'/'sample.js').write_text('<script>const x = 123;</script>', encoding='utf-8')
            orig = '<p>Safety notice</p>{{inline-js:sample.js}}'
            out = '<div class="pa-body"><p>Safety notice</p><script>const x = 123;</script></div>'
            self.assertEqual(target.audit_body('x', orig, out, root)['literal_script_blocks'], 1)
            with self.assertRaises(target.CustodyGate):
                target.audit_body('x', orig, out.replace('123', '456'), root)

    def test_unknown_body_macro_fails_closed(self):
        with self.assertRaises(target.CustodyGate):
            target.audit_body('x', '<p>{{danger:unknown}}</p>', self.out, self.root)

    def test_safe_body_outside_markup_ignored(self):
        self.assertEqual(self.check('<h1>Site navigation</h1>' + self.out)['original_reading_blocks'], 12)


def mutant(variant, i):
    raw, rendered = fixture()
    before = f'Instruction {i}.'
    if variant == 'change_heading':
        rendered = rendered.replace(before, f'Instruction {i + 20}.', 1)
    elif variant == 'remove_negation':
        rendered = rendered.replace(f'Do not replace reading {i}', f'Do replace reading {i}', 1)
    elif variant == 'change_quantity':
        rendered = rendered.replace(f'{i*4} units.', f'{i*4+1} units.', 1)
    elif variant == 'remove_clause':
        rendered = rendered.replace(f' with unsupported advice: {i*4} units.', '', 1)
    elif variant == 'remove_emphasis':
        rendered = rendered.replace(f'<strong>{before}</strong>', before, 1)
    elif variant == 'change_phrase':
        rendered = rendered.replace(f'reading {i} with', f'reading {i} without', 1)
    elif variant == 'reassign_claim':
        rendered = rendered.replace(f'Instruction {i}.', f'Another instruction {i}.', 1)
    else:
        raise AssertionError(variant)
    return raw, rendered


for _variant in ('change_heading', 'remove_negation', 'change_quantity',
                 'remove_clause', 'remove_emphasis', 'change_phrase', 'reassign_claim'):
    for _i in range(1, 7):
        def _test(self, variant=_variant, i=_i):
            raw, changed = mutant(variant, i)
            with self.assertRaises(target.CustodyGate,
                                   msg=f'{variant} at block {i} escaped'):
                target.audit_body('synthetic-guide', raw, changed,
                                  Path(tempfile.gettempdir()))
        setattr(EditorReadingDepth, f'test_mutation_{_variant}_{_i}', _test)


class NativeCorpusTests(unittest.TestCase):
    def test_actual_wordpress_draft_corpus_without_tools_fabrication(self):
        import build
        import r93_rendered_citation_fidelity as r93
        report = target.audit_library(build.Library(), build.build_article,
                                      r93.audit_document)
        self.assertEqual(report["release_state"], "HOLD")
        self.assertIs(report["may_publish"], False)
        self.assertEqual(report["article_draft_pairs"], 35)
        self.assertEqual(report["planned_tools"], 6)
        self.assertEqual(report["real_drafts_read"],
                         35 + report["actual_tool_draft_pairs"])
        self.assertEqual(report["citations_independently_rechecked_through_R93"], 1959)
        self.assertTrue(all(row["may_publish"] is False for row in
                            report["private_editorial_body_witnesses_NOT_APPROVED"]))
        copy = dict(report)
        seal = copy.pop("sha256_seal")
        self.assertEqual(target.digest(copy), seal)


if __name__ == '__main__':
    unittest.main()
