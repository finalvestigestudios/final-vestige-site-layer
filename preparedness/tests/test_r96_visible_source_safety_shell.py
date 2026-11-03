"""R96 private visible-source/safety-shell synthetic and adversarial gates.

Entirely in memory; no fixture writes to source fragments, articles or CMS.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import r96_visible_source_safety_shell as gate  # noqa: E402

URL = "https://example.org/primary-original"
TITLE = "Primary Original Source"
LABEL = "Source 1: " + TITLE
SCOPE = "The exact contributor-reviewed passage."
REF = {
    "id": "original-source", "url": URL, "title": TITLE, "human_link_check": False,
    "_origin": "start",
}
META = {
    "slug": "example-guide", "_body": "<p>Do not extrapolate. {{cite:original-source}}</p>",
    "source_use": {"original-source": SCOPE},
    "status": {"publish": "draft"},
    "safety_review": {"state": "pending"},
}


def fixture():
    return (
        '<div class="pa pa-article" data-slug="example-guide">'
        '<a class="pa-skip" href="#pa-main">Skip to the guide</a>'
        '<header class="pa-head"><h1>Guide</h1>'
        '<ul><li><span>Draft: not public</span></li>'
        '<li><span>Safety review pending</span></li></ul>'
        '<div class="pa-printbar"><button type="button" class="pa-btn pa-btn--ghost" '
        'onclick="window.print()">Print this guide</button></div></header>'
        '<div class="pa-body" id="pa-main"><p>Do not extrapolate. '
        '<sup class="pa-cite"><a href="#src-1" aria-label="' + LABEL + '">[1]</a></sup>'
        '</p></div>'
        '<section class="pa-sources" aria-labelledby="sources-h">'
        '<h2 id="sources-h">Sources and verification</h2>'
        '<p>The date below records a researcher\'s machine-assisted source check. '
        'A machine check is not independent human link verification.</p>'
        '<ol><li id="src-1"><a href="' + URL + '" rel="noopener">' + TITLE + '</a>. '
        '<span>Human source-link check pending</span>'
        '<span>Used for: ' + SCOPE + '</span></li></ol></section>'
        '<section class="pa-review" aria-labelledby="review-h"><h2 id="review-h">Review record</h2>'
        '<dl><dt>Editorial status</dt><dd>Drafted; editor read-through pending</dd>'
        '<dt>Safety review</dt><dd>A human safety review is required before this page can be published.</dd>'
        '<dt>Last source check</dt><dd>October 29, 2026</dd>'
        '<dt>Recheck when</dt><dd>When advice changes.</dd></dl></section>'
        '<script type="application/ld+json">{"@type":"Article"}</script></div>'
    )


class CleanCases(unittest.TestCase):
    def test_complete_hold_and_source_custody(self):
        x = gate.audit_shell(META, fixture(), [REF])
        self.assertEqual(x["rendered_citations"], 1)
        self.assertEqual(x["rendered_sources"], 1)
        self.assertEqual(x["source_link_anchors"], 1)
        self.assertEqual(x["release_state"], "HOLD")
        self.assertIs(x["may_publish"], False)
        self.assertEqual(x["human_source_claim_review"], "NOT_REVIEWED")

    def test_deterministic_report(self):
        self.assertEqual(gate.audit_shell(META, fixture(), [REF]),
                         gate.audit_shell(META, fixture(), [REF]))

    def test_valid_print_button_has_exact_contract(self):
        self.assertTrue(gate.audit_shell(META, fixture(), [REF])["visible_draft_notice"])

    def test_source_text_can_contain_html_character_references(self):
        src = {**REF, "title": "AT&T & R"}
        meta = {**META}
        html = fixture().replace(TITLE, "AT&amp;T &amp; R")
        self.assertEqual(gate.audit_shell(meta, html, [src])["rendered_sources"], 1)

    def test_metadata_still_never_certifies_safety(self):
        meta = {**META, "safety_review": {"state": "approved"}}
        html = fixture().replace("Safety review pending", "Safety review complete").replace(
            "A human safety review is required before this page can be published.",
            "Approved by a recorded reviewer on October 29, 2026")
        out = gate.audit_shell(meta, html, [REF])
        self.assertIs(out["may_publish"], False)
        self.assertEqual(out["qualified_safety_review"], "NOT_REVIEWED")

    def test_not_required_metadata_remains_not_human_approved(self):
        meta = {**META, "safety_review": {"state": "not-required"}}
        html = fixture().replace("Safety review pending", "No review required").replace(
            "A human safety review is required before this page can be published.",
            "Not required for this topic.")
        out = gate.audit_shell(meta, html, [REF])
        self.assertIs(out["may_publish"], False)
        self.assertEqual(out["independent_QD"], "NOT_REVIEWED")

    def test_html_entities_in_source_scope_decode(self):
        meta = {**META, "source_use": {"original-source": "Salt & heat."}}
        html = fixture().replace(SCOPE, "Salt &amp; heat.")
        self.assertEqual(gate.audit_shell(meta, html, [REF])["rendered_sources"], 1)

    def test_compact_canonical_seal_is_stable(self):
        payload = {"state": "HOLD", "count": 1}
        self.assertEqual(gate.seal(payload), gate.seal({"count": 1, "state": "HOLD"}))


class InvalidMetadata(unittest.TestCase):
    def check_rejected(self, meta, sources=None, html=None):
        with self.assertRaises(gate.Gate):
            gate.audit_shell(meta, fixture() if html is None else html,
                             [REF] if sources is None else sources)

    def test_published_state(self):
        self.check_rejected({**META, "status": {"publish": "published"}})

    def test_missing_status(self):
        self.check_rejected({**META, "status": {}})

    def test_unknown_safety_state(self):
        self.check_rejected({**META, "safety_review": {"state": "magically-safe"}})

    def test_empty_body(self):
        self.check_rejected({**META, "_body": None})

    def test_missing_original_citation(self):
        self.check_rejected({**META, "_body": "<p>No cite</p>"})

    def test_unlisted_literal_source(self):
        self.check_rejected({**META, "_body": "{{cite:different-source}}"})

    def test_source_order_swapped(self):
        self.check_rejected(META, [{**REF, "id": "different-source"}])

    def test_source_id_mismatch(self):
        self.check_rejected(META, [])

    def test_unsafe_source_scheme(self):
        self.check_rejected(META, [{**REF, "url": "http://example.org/primary-original"}])

    def test_missing_source_use(self):
        self.check_rejected({**META, "source_use": {}})

    def test_blank_source_use(self):
        self.check_rejected({**META, "source_use": {"original-source": ""}})

    def test_wrong_slug_no_implicit_reconciliation(self):
        self.check_rejected({**META, "slug": "other-guide"},
                            html=fixture().replace("example-guide", "other-guide").replace(
                                'class="pa-head"', 'class="pa-head" hidden'))


# Each case below becomes an independent unittest method, giving the CI runner
# a substantial, countable mutation battery instead of a single for-loop test.
CASES = {
    "source_section_hidden": ('class="pa-sources"', 'class="pa-sources" hidden'),
    "source_section_aria_hidden": ('class="pa-sources"', 'class="pa-sources" aria-hidden="true"'),
    "source_section_inert": ('class="pa-sources"', 'class="pa-sources" inert'),
    "source_section_display_none": ('class="pa-sources"', 'class="pa-sources" style="display:none"'),
    "source_section_visibility_hidden": ('class="pa-sources"', 'class="pa-sources" style="visibility:hidden"'),
    "source_section_content_hidden": ('class="pa-sources"', 'class="pa-sources" style="content-visibility:hidden"'),
    "source_section_opacity_zero": ('class="pa-sources"', 'class="pa-sources" style="opacity:0"'),
    "source_section_font_zero": ('class="pa-sources"', 'class="pa-sources" style="font-size:0"'),
    "source_link_hidden": ('href="' + URL + '"', 'hidden href="' + URL + '"'),
    "source_link_aria_hidden": ('href="' + URL + '"', 'aria-hidden="true" href="' + URL + '"'),
    "source_row_hidden": ('<li id="src-1">', '<li id="src-1" hidden>'),
    "source_row_inert": ('<li id="src-1">', '<li id="src-1" inert>'),
    "source_scope_hidden": ('<span>Used for:', '<span style="display:none">Used for:'),
    "source_scope_aria_hidden": ('<span>Used for:', '<span aria-hidden="true">Used for:'),
    "source_check_hidden": ('<span>Human source-link', '<span hidden>Human source-link'),
    "source_check_inert": ('<span>Human source-link', '<span inert>Human source-link'),
    "head_hidden": ('class="pa-head"', 'class="pa-head" hidden'),
    "head_inert": ('class="pa-head"', 'class="pa-head" inert'),
    "head_aria_hidden": ('class="pa-head"', 'class="pa-head" aria-hidden="true"'),
    "head_opacity_zero": ('class="pa-head"', 'class="pa-head" style="opacity:0"'),
    "draft_notice_hidden": ('<span>Draft: not public', '<span hidden>Draft: not public'),
    "draft_notice_aria_hidden": ('<span>Draft: not public', '<span aria-hidden="true">Draft: not public'),
    "review_hidden": ('class="pa-review"', 'class="pa-review" hidden'),
    "review_aria_hidden": ('class="pa-review"', 'class="pa-review" aria-hidden="true"'),
    "review_inert": ('class="pa-review"', 'class="pa-review" inert'),
    "review_display_none": ('class="pa-review"', 'class="pa-review" style="display: none"'),
    "review_qualifier_hidden": ('<dd>A human safety review', '<dd hidden>A human safety review'),
    "review_role_presentation": ('class="pa-review"', 'class="pa-review" role="presentation"'),
    "source_role_none": ('class="pa-sources"', 'class="pa-sources" role="none"'),
    "body_hidden": ('class="pa-body"', 'class="pa-body" hidden'),
    "body_aria_hidden": ('class="pa-body"', 'class="pa-body" aria-hidden="true"'),
    "root_hidden": ('data-slug="example-guide"', 'data-slug="example-guide" hidden'),
    "cite_hidden": ('class="pa-cite"', 'class="pa-cite" hidden'),
    "cite_aria_hidden": ('class="pa-cite"', 'class="pa-cite" aria-hidden="true"'),
    "cite_inert": ('class="pa-cite"', 'class="pa-cite" inert'),
    "cite_event": ('class="pa-cite"', 'class="pa-cite" onclick="alert(1)"'),
    "cite_wrong_href": ('href="#src-1"', 'href="#src-900"'),
    "cite_wrong_label": (LABEL, "Source 1: Counterfeit"),
    "cite_wrong_number": ('>[1]</a></sup>', '>[2]</a></sup>'),
    "cite_duplicate_href": ('href="#src-1"', 'href="#src-1" href="#src-1"'),
    "cite_anchor_hidden": ('href="#src-1"', 'href="#src-1" hidden'),
    "cite_anchor_event": ('href="#src-1"', 'href="#src-1" onclick="alert(1)"'),
    "cite_anchor_download": ('href="#src-1"', 'href="#src-1" download'),
    "cite_anchor_insert_span": ('>[1]</a></sup>', '><span>[1]</span></a></sup>'),
    "cite_anchor_insert_image": ('>[1]</a></sup>', '><img src="https://example.org/a">[1]</a></sup>'),
    "cite_insert_script": ('>[1]</a></sup>', '><script>alert(1)</script>[1]</a></sup>'),
    "cite_extra_text": ('</a></sup>', '</a>changed interpretation</sup>'),
    "cite_extra_anchor": ('</a></sup>', '</a><a href="#src-1">again</a></sup>'),
    "cite_retarget_title": (TITLE + '</a>', 'Bogus title</a>'),
    "source_retarget_href": ('href="' + URL + '"', 'href="https://fake.example/primary"'),
    "source_drop_rel": (' rel="noopener"', ''),
    "source_add_target": (' rel="noopener"', ' rel="noopener" target="_blank"'),
    "source_add_ping": (' rel="noopener"', ' rel="noopener" ping="https://tracker.example/"'),
    "source_add_onclick": (' rel="noopener"', ' rel="noopener" onclick="alert(1)"'),
    "source_duplicate_href": ('href="' + URL + '"', 'href="' + URL + '" href="' + URL + '"'),
    "source_wrong_id": ('<li id="src-1">', '<li id="src-99">'),
    "source_wrong_title": ('>' + TITLE + '</a>', '>Counterfeit</a>'),
    "source_wrong_scope": ('Used for: ' + SCOPE, 'Used for: Broad unsupported claim.'),
    "source_wrong_check": ('Human source-link check pending', 'Human source-link check complete'),
    "source_add_anchor": ('</span></li></ol>', '</span><a href="https://extra.example">Extra</a></li></ol>'),
    "source_add_form": ('<ol><li id="src-1">', '<form action="/collect"></form><ol><li id="src-1">'),
    "source_add_script": ('<ol><li id="src-1">', '<script>alert(1)</script><ol><li id="src-1">'),
    "source_add_iframe": ('<ol><li id="src-1">', '<iframe src="https://bad.example"></iframe><ol><li id="src-1">'),
    "source_add_comment": ('<ol><li id="src-1">', '<!-- hidden verification --><ol><li id="src-1">'),
    "review_add_script": ('<dl><dt>Editorial status', '<script>alert(1)</script><dl><dt>Editorial status'),
    "review_add_button": ('<dl><dt>Editorial status', '<button type="button">approve</button><dl><dt>Editorial status'),
    "review_missing_caution": ('A human safety review is required before this page can be published.', 'Safety is approved.'),
    "review_missing_status": ('<dt>Editorial status</dt>', '<dt>Something else</dt>'),
    "head_missing_draft": ('Draft: not public', 'Public and approved'),
    "head_missing_safety": ('Safety review pending', 'Safety reviewed'),
    "head_unsafe_print_onclick": ('onclick="window.print()"', 'onclick="alert(1)"'),
    "head_print_extra_event": ('onclick="window.print()"', 'onclick="window.print()" onpointerup="alert(1)"'),
    "head_print_extra_attr": ('onclick="window.print()"', 'onclick="window.print()" data-approved="true"'),
    "wrong_source_section_kind": ('<section class="pa-sources"', '<div class="pa-sources"'),
    "wrong_review_section_kind": ('<section class="pa-review"', '<article class="pa-review"'),
    "wrong_head_kind": ('<header class="pa-head"', '<div class="pa-head"'),
    "wrong_body_kind": ('<div class="pa-body"', '<section class="pa-body"'),
    "duplicate_source_section": ('</section><section class="pa-review"',
                                 '</section><section class="pa-sources"></section><section class="pa-review"'),
    "duplicate_review_section": ('</dl></section>', '</dl></section><section class="pa-review"></section>'),
    "duplicate_head": ('</header>', '</header><header class="pa-head"></header>'),
    "duplicate_article_root": ('</div>', '</div><div class="pa pa-article"></div>'),
    "cite_duplicate_class": ('class="pa-cite"', 'class="pa-cite" class="pa-cite"'),
}


class AttackCases(unittest.TestCase):
    """Each method is a separate negative test; no shared repository mutation."""


def make_attack(name, pair):
    def check(self):
        old, new = pair
        html = fixture()
        self.assertIn(old, html, "bad synthetic mutation fixture: " + name)
        changed = html.replace(old, new, 1)
        self.assertNotEqual(changed, html)
        with self.assertRaises(gate.Gate, msg=name):
            gate.audit_shell(META, changed, [REF])
    check.__name__ = "test_reject_" + name
    return check


for _name, _pair in sorted(CASES.items()):
    setattr(AttackCases, "test_reject_" + _name, make_attack(_name, _pair))




class AncestorVisibility(unittest.TestCase):
    def test_safe_outer_container_remains_allowed(self):
        html = '<div class="offline-preview">' + fixture() + '</div>'
        self.assertEqual(gate.audit_shell(META, html, [REF])["rendered_sources"], 1)

    def test_hidden_outer_container_fails(self):
        with self.assertRaises(gate.Gate):
            gate.audit_shell(META, '<div hidden>' + fixture() + '</div>', [REF])

    def test_aria_hidden_outer_container_fails(self):
        with self.assertRaises(gate.Gate):
            gate.audit_shell(META, '<div aria-hidden="true">' + fixture() + '</div>', [REF])

    def test_inert_outer_container_fails(self):
        with self.assertRaises(gate.Gate):
            gate.audit_shell(META, '<div inert>' + fixture() + '</div>', [REF])

    def test_hidden_pa_shell_ancestor_fails(self):
        html = fixture().replace(
            '<div class="pa-body" id="pa-main">',
            '<div class="pa-shell" hidden><div class="pa-body" id="pa-main">'
        ).replace('</p></div><section class="pa-sources"',
                  '</p></div></div><section class="pa-sources"')
        with self.assertRaisesRegex(gate.Gate, "hidden, inert or aria-hidden"):
            gate.audit_shell(META, html, [REF])

    def test_inert_pa_shell_ancestor_fails(self):
        html = fixture().replace(
            '<div class="pa-body" id="pa-main">',
            '<div class="pa-shell" inert><div class="pa-body" id="pa-main">'
        ).replace('</p></div><section class="pa-sources"',
                  '</p></div></div><section class="pa-sources"')
        with self.assertRaisesRegex(gate.Gate, "hidden, inert or aria-hidden"):
            gate.audit_shell(META, html, [REF])


if __name__ == "__main__":
    unittest.main()
