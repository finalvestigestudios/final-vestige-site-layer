"""R98 deterministic print/offline evidence custody. In-memory tests only.

No test writes into the shared repo, calls a URL, or updates WordPress.
A green result DOES NOT certify actual CSSOM, browser print, source accuracy,
emergency safety, qualified human approval, or permission to publish.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import r98_print_source_visibility_custody as gate  # noqa: E402

PRINT_URL = '.pa a[href^="http"]::after { content: " (" attr(href) ")"; }'
MINIMAL = """
.pa { --pa-bg: #101111; color: #ffffff; }
.pa-body sup.pa-cite { line-height: 0; font-size: .72em; }
.pa .pa-skip { position: absolute; left: -9999px; }
.pa-card[hidden] { display: none; }
.pa-empty[hidden] { display: none; }
@container (min-width: 700px) { .pa-shell { display: grid; } }
@media print {
  .pa { background: #fff !important; color: #000 !important; }
  .pa *, .pa a { color: #000 !important; background: transparent !important; }
  .pa a[href^="http"]::after { content: " (" attr(href) ")"; }
  .pa-tool, .pa-toc, .pa-filter, .pa-printbar, .pa-skip,
  .pa-card h3 a::after { display: none !important; }
  .pa-sources li { break-inside: avoid; }
}
"""


def audit(css):
    return gate.audit_stylesheet(css)


class Baseline(unittest.TestCase):
    def test_minimal_fixture_is_static_hold(self):
        result = audit(MINIMAL)
        self.assertEqual(result["release_state"], "HOLD")
        self.assertIs(result["may_publish"], False)
        self.assertIs(result["browser_print_QA"] == "NOT_REVIEWED", True)
        self.assertTrue(result["print_external_source_url_annotation"])
        self.assertTrue(result["calculator_hidden_on_print_REVIEW_REQUIRED"])

    def test_actual_repository_stylesheet_audits_without_modification(self):
        css = (ROOT / "assets" / "preparedness.css").read_text(encoding="utf-8")
        report = audit(css)
        self.assertEqual(report["release_state"], "HOLD")
        self.assertGreater(report["scoped_selectors_audited"], 50)
        self.assertGreater(report["print_selectors_audited"], 10)
        self.assertEqual(report["calculator_hidden_on_print_REVIEW_REQUIRED"], True)

    def test_original_css_is_not_changed_by_audit(self):
        before = MINIMAL
        audit(before)
        self.assertEqual(before, MINIMAL)

    def test_reordered_noncritical_rules_are_permitted(self):
        css = MINIMAL + "\n.pa-crumbs { margin-top: 10px; }\n"
        self.assertTrue(audit(css)["static_css_diagnostics_only"])

    def test_print_href_annotation_does_not_prove_link_validity(self):
        report = audit(MINIMAL)
        self.assertNotIn("human_link_check_APPROVED", report)

    def test_scoped_links_remain_allowed(self):
        self.assertTrue(audit(MINIMAL + ".pa a { text-underline-offset: 3px; }")[
            "print_external_source_url_annotation"])

    def test_media_forced_colors_nested_is_supported(self):
        css = MINIMAL + "@media (forced-colors: active) { .pa-alert { border: 2px solid CanvasText; } }"
        self.assertTrue(audit(css)["static_css_diagnostics_only"])

    def test_all_visibility_decisions_remain_machine_only(self):
        result = audit(MINIMAL)
        self.assertIs(result["may_publish"], False)
        self.assertEqual(result["browser_print_QA"], "NOT_REVIEWED")


BAD_DECLARATIONS = [
    ("hide_display", "display:none"),
    ("hide_important", "display:none!important"),
    ("invisible", "visibility:hidden"),
    ("visibility_collapse", "visibility:collapse"),
    ("content_visibility", "content-visibility:hidden"),
    ("content_visibility_auto", "content-visibility:auto"),
    ("opacity_integer", "opacity:0"),
    ("opacity_fraction", "opacity:0.0"),
    ("opacity_tiny", "opacity:.0001"),
    ("opacity_soft", "opacity:0.8"),
    ("color_rgba_zero", "color:rgba(255,255,255,0)"),
    ("color_hsla_zero", "color:hsla(0,100%,50%,0)"),
    ("opacity_var", "opacity:var(--hide)"),
    ("opacity_clamp", "opacity:clamp(0,0,0)"),
    ("scale_zero", "scale:0"),
    ("zoom_zero", "zoom:0"),
    ("mask", "mask-image:linear-gradient(transparent,transparent)"),
    ("webkit_mask", "-webkit-mask-image:linear-gradient(transparent,transparent)"),
    ("clip_path", "clip-path:inset(50%)"),
    ("filter_opacity", "filter:opacity(0)"),
    ("webkit_filter", "-webkit-filter:opacity(0)"),
    ("overflow_hidden", "overflow:hidden"),
    ("overflow_clip", "overflow:clip"),
    ("overflow_x", "overflow-x:hidden"),
    ("overflow_y", "overflow-y:clip"),
    ("font_size_zero", "font-size:0"),
    ("height_zero", "height:0"),
    ("max_height_zero", "max-height:0px"),
    ("width_zero", "width:0px"),
    ("max_width_zero", "max-width:0"),
    ("block_size_zero", "block-size:0"),
    ("inline_size_zero", "inline-size:0"),
    ("lineheight_zero", "line-height:0"),
    ("color_transparent", "color:transparent"),
    ("webkit_textfill", "-webkit-text-fill-color:transparent"),
    ("transform_scale", "transform:scale(0)"),
    ("transform_translate", "transform:translate(-9999px)"),
    ("text_indent", "text-indent:-9999px"),
    ("left_offscreen", "left:-9999px"),
    ("right_offscreen", "right:-9999px"),
    ("fixed_overlay", "position:fixed"),
    ("animation", "animation:vanish 1s linear"),
    ("pointer_events", "pointer-events:none"),
]
# 13 sensitive surfaces x 39 concealment families = 500+ cases,
# bounded in-memory; unit tests are method-per-attack for clear diagnostics.
SELECTORS = [
    ".pa-sources", ".pa-review", ".pa-cite", ".pa-src-use",
    ".pa-alert", ".pa-act", ".pa-verdict", ".pa-body",
    ".pa-head", ".pa-shell", ".pa-article", ".pa *",
    ".pa-sources li",
]

class RejectedVisibilityMutations(unittest.TestCase):
    pass

for family, declaration in BAD_DECLARATIONS:
    for idx, selector in enumerate(SELECTORS):
        # The authored superscript line-height:0 is explicitly allowed by the
        # original CSS; test every other critical selector instead.
        name = "test_" + family + "_" + str(idx)
        def check(self, selector=selector, declaration=declaration):
            css = MINIMAL + "\n@media print { " + selector + " { " + declaration + "; } }"
            with self.assertRaises(gate.Hold):
                audit(css)
        setattr(RejectedVisibilityMutations, name, check)


BAD_INPUTS = [
    ("missing_href", MINIMAL.replace(PRINT_URL, "")),
    ("missing_url_content", MINIMAL.replace('attr(href)', 'attr(title)')),
    ("empty_url_content", MINIMAL.replace('" (" attr(href) ")"', '""')),
    ("duplicate_print_url", MINIMAL + "\n@media print {" + PRINT_URL + "}"),
    ("script_url", MINIMAL + '\n.pa {background-image:url(https://example.net/tracker); }'),
    ("css_import", MINIMAL + '\n@import "https://example.net/track.css";'),
    ("font_face", MINIMAL + '\n@font-face { font-family:remote; src:url(https://example.com/x); }'),
    ("unscoped_global", MINIMAL + '\nbody { display:block; }'),
    ("unscoped_html", MINIMAL + '\nhtml { opacity:1; }'),
    ("unreviewed_layer", MINIMAL + '\n@layer theme { .pa { color: #fff; } }'),
    ("unreviewed_supports", MINIMAL + '\n@supports (display: grid) { .pa { color: #fff; } }'),
    ("escaped_selector", MINIMAL + '\n.pa-\\73ources { display:none; }'),
    ("unterminated_comment", MINIMAL + '\n/*never closed'),
    ("unexpected_closing_brace", MINIMAL + '\n}'),
    ("empty_property", MINIMAL + '\n.pa-review { color:; }'),
    ("duplicate_property", MINIMAL + '\n.pa-review { color:#fff; color:#000; }'),
    ("unclosed_string", MINIMAL + '\n.pa-review { content:"unclosed; }'),
    ("bad_selector_nesting", MINIMAL + '\n.pa-review { @media print {.pa {color:red}} }'),
    ("unknown_at_rule", MINIMAL + '\n@page { size: A4; }'),
    ("print_shell_hidden", MINIMAL + '\n@media print {.pa-sources,.pa-review {display:none}}'),
    ("print_pseudo_url_hidden", MINIMAL + '\n@media print {.pa a[href^="http"]::after {display:none}}'),
    ("print_safety_badge_hidden", MINIMAL + '\n@media print {.pa-verdict-badge {display:none}}'),
    ("screen_review_hidden", MINIMAL + '\n@media screen {.pa-review {opacity:0}}'),
    ("nested_container_hidden", MINIMAL + '\n@container (min-width:400px) {.pa-sources {display:none}}'),
    ("print_hide_head", MINIMAL + '\n@media print {.pa-head {display:none}}'),
    ("print_white_on_white", MINIMAL + '\n@media print {.pa-review {color:white}}'),
    ("print_root_black_background", MINIMAL.replace("background: #fff !important", "background: #000 !important")),
    ("print_root_white_text", MINIMAL.replace("color: #000 !important", "color: #fff !important")),
    ("print_descendant_white_text", MINIMAL.replace(".pa *, .pa a { color: #000", ".pa *, .pa a { color: #fff")),
    ("wide_media_hide", MINIMAL + '\n@media (min-width:800px) {.pa-sources {visibility:hidden}}'),
    ("nonprint_root_hide", MINIMAL + '\n.pa {display:none}'),
]

class RejectedStructuralMutations(unittest.TestCase):
    pass

for label, css in BAD_INPUTS:
    def check(self, css=css):
        with self.assertRaises(gate.Hold):
            audit(css)
    setattr(RejectedStructuralMutations, "test_" + label, check)


class InvalidTypes(unittest.TestCase):
    def test_bytes_rejected(self):
        with self.assertRaises(gate.Hold):
            audit(b".pa {color:black}")
    def test_empty_rejected(self):
        with self.assertRaises(gate.Hold):
            audit("")
    def test_oversized_rejected(self):
        with self.assertRaises(gate.Hold):
            audit(MINIMAL + " " * 300001)
    def test_unsupported_at_rule_in_media_rejected(self):
        with self.assertRaises(gate.Hold):
            audit(MINIMAL + "@media print { @layer a { .pa {color:black} } }")
    def test_zero_height_superscript_is_narrowly_allowed(self):
        self.assertTrue(audit(MINIMAL)["static_css_diagnostics_only"])
    def test_full_source_links_required_in_print(self):
        with self.assertRaises(gate.Hold):
            audit(MINIMAL.replace('attr(href)', 'attr(data-url)'))
    def test_unsafe_css_cannot_turn_into_qd_pass(self):
        with self.assertRaises(gate.Hold):
            audit(MINIMAL + "@media print { .pa-review {display:none} }")



# R99 baseline regression and conservative print-eligibility gates.
# The existing CSS hides five *decoration-only* ::before flourishes; previously
# the R98 gate rejected its own original stylesheet before corpus testing.
DECORATIVE_PSEUDOS = (
    ".pa-act h2::before", ".pa-verdict-head h2::before",
    ".pa-sources h2::before", ".pa-review h2::before",
    ".pa-related h2::before",
)

class R99ActualBaseline(unittest.TestCase):
    def test_all_five_existing_decorative_exceptions_are_exact_and_reported(self):
        css = (ROOT / "assets" / "preparedness.css").read_text(encoding="utf-8")
        report = audit(css)
        self.assertEqual(
            report["screen_only_decorative_pseudo_hide_exceptions_NOT_SAFETY_APPROVAL"],
            sorted(DECORATIVE_PSEUDOS),
        )
        self.assertEqual(report["browser_print_QA"], "NOT_REVIEWED")
        self.assertIs(report["may_publish"], False)

    def test_outside_print_color_schemes_unchanged(self):
        self.assertTrue(audit(MINIMAL + "\n.pa-alert { background: #000; }")[
            "static_css_diagnostics_only"])

    def test_literal_print_annotation_is_not_qualified_source_approval(self):
        result = audit(MINIMAL)
        self.assertEqual(result["release_state"], "HOLD")
        self.assertNotIn("source_verified", result)


class R99RejectPseudoOrCondition(unittest.TestCase):
    pass

for i, selector in enumerate(DECORATIVE_PSEUDOS):
    def test_allow(self, selector=selector):
        report = audit(MINIMAL + "\n" + selector + " { display:none; }")
        self.assertFalse(report["may_publish"])
    setattr(R99ActualBaseline, "test_exact_decorative_exception_" + str(i), test_allow)

    def test_deny_print(self, selector=selector):
        with self.assertRaises(gate.Hold):
            audit(MINIMAL + "\n@media print {" + selector + "{display:none;}}")
    setattr(R99RejectPseudoOrCondition, "test_no_print_decoration_exception_" + str(i), test_deny_print)

for i, selector in enumerate((".pa-review h3::before", ".pa-sources h2",
                               ".pa-alert::before", ".pa-act h2",
                               ".pa-related h2::after", ".pa-review dt")):
    def test_deny(self, selector=selector):
        with self.assertRaises(gate.Hold):
            audit(MINIMAL + "\n" + selector + "{display:none;}")
    setattr(R99RejectPseudoOrCondition, "test_no_other_hidden_selector_" + str(i), test_deny)

for i, prefix in enumerate(("@media screen { ", "@media (max-width: 1000px) { ",
                             "@media (prefers-reduced-motion: no-preference) { ",
                             "@container (min-width: 600px) { ")):
    def test_unreachable(self, prefix=prefix):
        css = MINIMAL.replace("@media print {", prefix + "@media print {", 1) + "\n}"
        with self.assertRaises(gate.Hold):
            audit(css)
    setattr(R99RejectPseudoOrCondition, "test_conditional_print_wrapper_" + str(i), test_unreachable)

for i, selector in enumerate(("body:has(.pa)", "html:where(.pa)", ":is(.pa)",
                               "main:has(.pa-review)", "body .pa + section",
                               ".pa:has(body)", ".pa:is(body)")):
    def test_scope(self, selector=selector):
        with self.assertRaises(gate.Hold):
            audit(MINIMAL + "\n" + selector + "{color:red;}")
    setattr(R99RejectPseudoOrCondition, "test_complex_or_leaky_scope_" + str(i), test_scope)

for i, declaration in enumerate(("background:#000", "background-color:#000",
                                 "background:var(--pa-bg)",
                                 "background-color:rgba(0,0,0,1)",
                                 "background:linear-gradient(#000,#000)",
                                 "background:#123456!important")):
    def test_background(self, declaration=declaration):
        with self.assertRaises(gate.Hold):
            audit(MINIMAL + "\n@media print { .pa-review {" + declaration + ";}}")
    setattr(R99RejectPseudoOrCondition, "test_black_or_opaque_print_background_" + str(i), test_background)

for i, value in enumerate(('"VERIFIED " attr(href)', '"ref: " attr(href)',
                           'attr(href) " (official)"',
                           '" (reference) " attr(href) ")"',
                           '" (" attr(href) ") " attr(title)')):
    def test_annotation(self, value=value):
        css = MINIMAL.replace('" (" attr(href) ")"', value)
        with self.assertRaises(gate.Hold):
            audit(css)
    setattr(R99RejectPseudoOrCondition, "test_nonliteral_print_annotation_" + str(i), test_annotation)

def test_implicit_print_container_suppression(self):
    css = MINIMAL.replace(PRINT_URL, "") + (
        "\n@media print { @container (min-width: 600px) {"
        + PRINT_URL + "} }")
    with self.assertRaises(gate.Hold):
        audit(css)

setattr(R99RejectPseudoOrCondition,
        "test_print_url_under_conditional_container_not_sufficient",
        test_implicit_print_container_suppression)

if __name__ == "__main__":
    unittest.main()
