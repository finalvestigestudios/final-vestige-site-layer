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


if __name__ == "__main__":
    unittest.main()
