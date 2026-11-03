"""Synthetic, adversarial and native R95 Preparedness DOM/attribute custody tests.

No test modifies the repository, source registry, articles or a WordPress site.
"""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import r95_dom_attribute_custody as gate  # noqa: E402

ROUTES = {"guide": "/preparedness/start-here/guide/"}


def fixture(count=8):
    """The same prose can mask link retargeting, HTML injection or hidden notes."""
    original = "".join(
        '<section data-slot="' + str(n) + '"><h2 id="heading-' + str(n) + '">' +
        'Instruction ' + str(n) + '</h2><p class="critical" title="Keep readable">' +
        'Caution ' + str(n) + ': do not follow an unverified procedure. ' +
        '<a rel="noopener" href="https://example.org/primary/' + str(n) + '">' +
        'original primary source ' + str(n) + '</a> and ' +
        '{{link:guide|the complete local guide}} before proceeding. ' +
        '{{cite:synthetic-source}}</p></section>'
        for n in range(1, count + 1)
    )
    rendered = original.replace(
        "{{link:guide|the complete local guide}}",
        '<a href="/preparedness/start-here/guide/">the complete local guide</a>'
    ).replace(
        "{{cite:synthetic-source}}",
        '<sup class="pa-cite"><a href="#src-1" aria-label="Source 1">[1]</a></sup>'
    )
    rendered = '<article><div class="pa-body">' + rendered + '</div></article>'
    return original, rendered


class SyntheticDOMCustody(unittest.TestCase):
    def setUp(self):
        self.src, self.out = fixture()
        self.root = Path(tempfile.gettempdir())

    def check(self, original=None, rendered=None, routes=None):
        return gate.audit_markup(
            "synthetic-guide",
            self.src if original is None else original,
            self.out if rendered is None else rendered,
            self.root,
            ROUTES if routes is None else routes,
        )

    def test_complete_dom_and_eight_citation_skips(self):
        row = self.check()
        self.assertEqual(row["inserted_inline_citations_skipped_NOT_APPROVED"], 8)
        self.assertEqual(row["authored_anchors_preserved"], 16)
        self.assertEqual(row["release_state"], "HOLD")
        self.assertIs(row["may_publish"], False)

    def test_deterministic_complete_dom_witness(self):
        self.assertEqual(self.check(), self.check())

    def test_html_entities_are_semantically_equivalent(self):
        raw = '<p title="R &amp; D">Use 5 &times; 3 &amp; 2</p>'
        html = '<div class="pa-body"><p title="R &amp; D">Use 5 × 3 &amp; 2</p></div>'
        self.assertEqual(gate.audit_markup("x", raw, html, self.root, {})["authored_anchors_preserved"], 0)

    def test_citation_anchor_only_is_ignored(self):
        raw = "<p>One {{cite:source}} two</p>"
        html = ('<div class="pa-body"><p>One <sup class="pa-cite">'
                '<a href="#src-1" aria-label="Source 1">[1]</a></sup> two</p></div>')
        self.assertEqual(gate.audit_markup("x", raw, html, self.root, {})["inserted_inline_citations_skipped_NOT_APPROVED"], 1)

    def test_no_synthetic_citation_does_not_require_fake_source(self):
        raw = "<p>Original editorial notice.</p>"
        html = '<div class="pa-body"><p>Original editorial notice.</p></div>'
        self.assertEqual(gate.audit_markup("x", raw, html, self.root, {})["inserted_inline_citations_skipped_NOT_APPROVED"], 0)

    def test_missing_planned_target_is_unlinked_in_both(self):
        raw = '<p>Use {{link:future-guide|future guidance}} only after review.</p>'
        html = '<div class="pa-body"><p>Use future guidance only after review.</p></div>'
        self.assertEqual(gate.audit_markup("x", raw, html, self.root, {})["authored_anchors_preserved"], 0)

    def test_planned_only_target_must_not_become_live_anchor(self):
        raw = '<p>See {{link:future-guide|future guidance}}.</p>'
        html = ('<div class="pa-body"><p>See '
                '<a href="/preparedness/future/">future guidance</a>.</p></div>')
        with self.assertRaises(gate.Gate):
            gate.audit_markup("x", raw, html, self.root, {})

    def test_source_url_inside_author_body_preserved(self):
        raw = '<p><a href="https://example.org/a?x=1&amp;y=2">Original</a></p>'
        html = '<div class="pa-body"><p><a href="https://example.org/a?x=1&amp;y=2">Original</a></p></div>'
        self.assertEqual(gate.audit_markup("x", raw, html, self.root, {})["authored_anchors_preserved"], 1)

    def test_external_author_link_cannot_be_redirected(self):
        with self.assertRaises(gate.Gate):
            self.check(rendered=self.out.replace("https://example.org/primary/5",
                                                 "https://counterfeit.example/claim/5"))

    def test_internal_macro_link_cannot_be_retargeted(self):
        with self.assertRaises(gate.Gate):
            self.check(rendered=self.out.replace("/preparedness/start-here/guide/",
                                                 "/preparedness/water/unverified/"))

    def test_nochange_outside_pa_body_is_ignored(self):
        self.assertEqual(self.check(rendered='<nav><a href="/external">NAV</a></nav>' + self.out)["release_state"], "HOLD")

    def test_body_wrapper_required(self):
        with self.assertRaises(gate.Gate):
            self.check(rendered=self.out.replace('class="pa-body"', 'class="other"'))

    def test_duplicate_body_is_fatal(self):
        with self.assertRaises(gate.Gate):
            self.check(rendered=self.out.replace("</article>", '<div class="pa-body"><p>Duplicate.</p></div></article>'))

    def test_nested_body_is_fatal(self):
        with self.assertRaises(gate.Gate):
            self.check(rendered=self.out.replace('<section data-slot="2">', '<div class="pa-body"><section data-slot="2">'))

    def test_missing_original_fails_closed(self):
        with self.assertRaises(gate.Gate):
            self.check(original="")

    def test_missing_render_fails_closed(self):
        with self.assertRaises(gate.Gate):
            self.check(rendered="")

    def test_unknown_original_macro_fails_closed(self):
        with self.assertRaises(gate.Gate):
            self.check(original=self.src + "<p>{{untrusted:macro}}</p>")

    def test_malformed_editorial_markup_fails_closed(self):
        with self.assertRaises(gate.Gate):
            self.check(original="<p>Unclosed")

    def test_malformed_rendered_markup_fails_closed(self):
        with self.assertRaises(gate.Gate):
            self.check(rendered=self.out.replace('</section>', '', 1))

    def test_illegal_document_slug_fails_closed(self):
        with self.assertRaises(gate.Gate):
            gate.audit_markup("../escape", self.src, self.out, self.root, ROUTES)

    def test_invalid_intended_target_fails_closed(self):
        with self.assertRaises(gate.Gate):
            self.check(routes={"guide": "javascript:alert(1)"})

    def test_duplicate_href_attribute_fails_closed(self):
        with self.assertRaises(gate.Gate):
            self.check(rendered=self.out.replace(
                '<a href="/preparedness/start-here/guide/">',
                '<a href="/preparedness/start-here/guide/" href="https://bad.example/">', 1))

    def test_html_comment_injection_does_not_escape_custody(self):
        with self.assertRaises(gate.Gate):
            self.check(rendered=self.out.replace("<p class=", "<!--hidden--><p class=", 1))

    def test_script_content_is_custodied(self):
        raw = "<p>Notice</p><script>const warning='KEEP';</script>"
        html = '<div class="pa-body">' + raw + '</div>'
        self.assertEqual(gate.audit_markup("x", raw, html, self.root, {})["release_state"], "HOLD")
        with self.assertRaises(gate.Gate):
            gate.audit_markup("x", raw, html.replace("KEEP", "HIDE"), self.root, {})

    def test_inline_script_file_is_read_not_executed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "tools").mkdir()
            (root / "tools" / "sample.js").write_text(
                "<script>const sentinel = 'read-only';</script>", encoding="utf-8")
            raw = "<p>Notice</p>{{inline-js:sample.js}}"
            html = '<div class="pa-body"><p>Notice</p><script>const sentinel = \'read-only\';</script></div>'
            self.assertEqual(gate.audit_markup("x", raw, html, root, {})["release_state"], "HOLD")
            with self.assertRaises(gate.Gate):
                gate.audit_markup("x", raw, html.replace("read-only", "altered"), root, {})


MUTATIONS = (
    ("swap_primary_link", 'https://example.org/primary/{i}', 'https://example.org/changed/{i}'),
    ("remove_internal_link", '<a href="/preparedness/start-here/guide/">the complete local guide</a>', 'the complete local guide'),
    ("add_ping", '<a rel="noopener" href="https://example.org/primary/{i}">', '<a rel="noopener" href="https://example.org/primary/{i}" ping="https://bad.example/track">'),
    ("add_event_handler", '<a rel="noopener" href="https://example.org/primary/{i}">', '<a rel="noopener" href="https://example.org/primary/{i}" onclick="alert(1)">'),
    ("hide_warning", '<p class="critical" title="Keep readable">', '<p class="critical" title="Keep readable" style="display:none">'),
    ("remove_warning_class", '<p class="critical" title="Keep readable">', '<p title="Keep readable">'),
    ("change_claim_scope", 'Caution {i}: do not follow', 'Caution {i}: always follow'),
    ("change_anchor_attachment", '<a rel="noopener" href="https://example.org/primary/{i}">original primary source {i}</a>', 'original <a rel="noopener" href="https://example.org/primary/{i}">primary source {i}</a>'),
    ("insert_invisible_iframe", '<section data-slot="{i}">', '<section data-slot="{i}"><iframe src="https://bad.example/"></iframe>'),
    ("insert_hidden_form", '<section data-slot="{i}">', '<section data-slot="{i}"><form action="https://bad.example/"></form>'),
    ("change_heading_attribute", '<h2 id="heading-{i}">', '<h2 id="wrong-{i}">'),
    ("change_source_publisher", 'original primary source {i}', 'different primary source {i}'),
)

for _kind, _old, _new in MUTATIONS:
    for _i in range(1, 9):
        def _case(self, kind=_kind, old=_old, new=_new, i=_i):
            needle = old.format(i=i)
            replacement = new.format(i=i)
            self.assertIn(needle, self.out, (kind, i))
            changed = self.out.replace(needle, replacement, 1)
            with self.assertRaises(gate.Gate,
                                   msg="DOM/attribute mutation escaped: " + kind + " " + str(i)):
                self.check(rendered=changed)
        setattr(SyntheticDOMCustody, "test_mutant_" + _kind + "_" + str(_i), _case)


class NativeReadOnlyArchive(unittest.TestCase):
    def test_exact_real_draft_inventory_and_rendering(self):
        import build
        import r93_rendered_citation_fidelity as r93
        import r94_body_custody as r94

        report = gate.audit_library(build.Library(), build.build_article,
                                    r93.audit_document, r94.audit_body)
        self.assertEqual(report["release_state"], "HOLD")
        self.assertIs(report["may_publish"], False)
        self.assertEqual(report["slated_articles"], 35)
        self.assertEqual(report["planned_tools"], 6)
        self.assertEqual(report["real_article_drafts"], 35)
        self.assertEqual(report["real_tool_drafts"], 1)
        self.assertEqual(len(report["missing_tool_drafts_NOT_IMPORTABLE"]), 5)
        self.assertEqual(report["distinct_private_draft_urls"], 36)
        self.assertEqual(report["rendered_citation_occurrences_rechecked_R93"], 1959)
        self.assertEqual(report["original_reading_blocks_rechecked_R94"], 4032)
        self.assertTrue(report["original_dom_events_preserved"] > 4032)
        self.assertTrue(all(row["may_publish"] is False for row in
                            report["per_draft_dom_custody_NOT_APPROVED"]))
        seal = report["sha256_seal"]
        copy = {k: v for k, v in report.items() if k != "sha256_seal"}
        self.assertEqual(gate.digest(copy), seal)


if __name__ == "__main__":
    unittest.main()
