"""R29: forbid browser/HTMLParser differentials and collapsed interactive source citations.

Synthetic fixtures only. These tests do not claim real articles or claims are safe.
"""
from __future__ import annotations
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import citation_token_visibility_gate as gate


REJECT = [
    ('hidden_selfclosing_div', '<div hidden/>{{cite:s}}</div>'),
    ('inert_selfclosing_div', '<div inert/>{{cite:s}}</div>'),
    ('hidden_selfclosing_section', '<section hidden/>{{cite:s}}</section>'),
    ('hidden_selfclosing_article', '<article hidden/>{{cite:s}}</article>'),
    ('hidden_selfclosing_span', '<span hidden/>{{cite:s}}</span>'),
    ('hidden_selfclosing_p', '<p hidden/>{{cite:s}}</p>'),
    ('hidden_selfclosing_details', '<details/>{{cite:s}}</details>'),
    ('hidden_selfclosing_dialog', '<dialog/>{{cite:s}}</dialog>'),
    ('hidden_selfclosing_script', '<script/>{{cite:s}}</script>'),
    ('inert_selfclosing_style', '<style/>{{cite:s}}</style>'),
    ('selfclosing_div_without_citation', '<div/>Visible paragraph {{cite:s}}'),
    ('selfclosing_section_without_citation', '<section/>Visible {{cite:s}}'),
    ('selfclosing_custom_without_citation', '<custom-widget/>Visible {{cite:s}}'),
    ('selfclosing_summary', '<details open><summary/>{{cite:s}}</details>'),
    ('closed_details', '<details>Evidence {{cite:s}}</details>'),
    ('closed_details_summary', '<details><summary>Source {{cite:s}}</summary></details>'),
    ('closed_details_nested', '<details><p>Evidence {{cite:s}}</p></details>'),
    ('closed_details_open_false', '<details open="">{{cite:s}}</details><details>{{cite:s}}</details>'),
    ('closed_dialog', '<dialog>{{cite:s}}</dialog>'),
    ('closed_dialog_nested', '<dialog><section>{{cite:s}}</section></dialog>'),
    ('closed_dialog_then_visible', '<dialog>{{cite:s}}</dialog><p>{{cite:t}}</p>'),
    ('popover_default', '<p popover>{{cite:s}}</p>'),
    ('popover_manual', '<section popover="manual">{{cite:s}}</section>'),
    ('popover_auto', '<div popover="auto"><span>{{cite:s}}</span></div>'),
    ('popover_empty', '<article popover="">{{cite:s}}</article>'),
    ('popover_false', '<p popover="false">{{cite:s}}</p>'),
    ('hidden_nested_open_dialog', '<main hidden><dialog open>{{cite:s}}</dialog></main>'),
    ('css_escaped_display_value', r'<p style="display: n\6f ne">{{cite:s}}</p>'),
    ('css_escaped_display_name', r'<p style="dis\70 lay: none">{{cite:s}}</p>'),
    ('css_escaped_visibility_name', r'<p style="visibilit\79 : hidden">{{cite:s}}</p>'),
    ('css_escaped_visibility_value', r'<p style="visibility: h\69 dden">{{cite:s}}</p>'),
    ('css_escaped_opacity_value', r'<p style="opacity:\30 ">{{cite:s}}</p>'),
    ('css_escaped_color_value', r'<p style="color:trans\70 arent">{{cite:s}}</p>'),
    ('css_escaped_font_size', r'<p style="font-\73 ize:0px">{{cite:s}}</p>'),
    ('css_invalid_escape_null', r'<p style="display:\0 ">{{cite:s}}</p>'),
    ('css_invalid_escape_surrogate', r'<p style="display:\d800 ">{{cite:s}}</p>'),
    ('css_unknown_malformed_escape', r'<p style="display:\q\">{{cite:s}}</p>'),
    ('css_color_transparent', '<p style="color:transparent">{{cite:s}}</p>'),
    ('css_color_transparent_important', '<p style="color:TRANSPARENT!important">{{cite:s}}</p>'),
    ('css_font_size_zero_px', '<p style="font-size:0px">{{cite:s}}</p>'),
    ('css_font_size_zero_em', '<p style="font-size:0em">{{cite:s}}</p>'),
    ('css_font_size_zero_rem', '<p style="font-size:0rem">{{cite:s}}</p>'),
    ('css_font_size_zero_percent', '<p style="font-size:0%">{{cite:s}}</p>'),
    ('css_font_size_zero_decimal', '<p style="font-size:0.00rem">{{cite:s}}</p>'),
    ('css_opacity_zero_scientific', '<p style="opacity:0e0">{{cite:s}}</p>'),
    ('css_opacity_zero_negative', '<p style="opacity:-0">{{cite:s}}</p>'),
    ('css_opacity_zero_exp', '<p style="opacity:0.00e5">{{cite:s}}</p>'),
    ('css_opacity_zero_plus', '<p style="opacity:+0.0%">{{cite:s}}</p>'),
    ('css_disguised_css_comment', '<p style="dis/**/play:none">{{cite:s}}</p>'),
    ('css_hidden_ancestor', '<div style="font-size:0"><p>{{cite:s}}</p></div>'),
]

ALLOW = [
    ('visible_plain', '<p>Claim {{cite:s}}</p>', 1),
    ('open_details', '<details open><summary>Source</summary>{{cite:s}}</details>', 1),
    ('open_dialog', '<dialog open><p>{{cite:s}}</p></dialog>', 1),
    ('open_details_empty', '<details open="">{{cite:s}}</details>', 1),
    ('open_dialog_false_boolean', '<dialog open="false">{{cite:s}}</dialog>', 1),
    ('after_closed_details', '<details>Plain content</details><p>{{cite:s}}</p>', 1),
    ('after_closed_dialog', '<dialog>Plain content</dialog><p>{{cite:s}}</p>', 1),
    ('after_popover', '<p popover>No cite</p><p>{{cite:s}}</p>', 1),
    ('void_br_slash', '<p>A<br/>{{cite:s}}</p>', 1),
    ('void_hr_slash', '<p>A<hr/>{{cite:s}}</p>', 1),
    ('void_img_slash', '<p><img src="x" />{{cite:s}}</p>', 1),
    ('opacity_half', '<p style="opacity:.5">{{cite:s}}</p>', 1),
    ('css_font_positive', '<p style="font-size:12px">{{cite:s}}</p>', 1),
    ('css_color_black', '<p style="color:black">{{cite:s}}</p>', 1),
    ('css_display_flex', '<p style="display:flex">{{cite:s}}</p>', 1),
    ('css_visibility_visible', '<p style="visibility:visible">{{cite:s}}</p>', 1),
    ('visible_no_styling', '🔎<p>Evidence {{cite:s}}</p>', 1),
    ('multiple', '<p>Source {{cite:s}} and {{cite:s}}</p>', 2),
    ('mixed_citation_ids', '<h2>{{cite:first-id}}</h2><p>{{cite:second_id}}</p>', 2),
]


class RejectBrowserDifferential(unittest.TestCase):
    pass


for name, body in REJECT:
    def f(self, body=body):
        with self.assertRaises(gate.CitationPlacementHold):
            gate.verified_citations(body)
    setattr(RejectBrowserDifferential, 'test_reject_' + name, f)


class AcceptTransparentCases(unittest.TestCase):
    pass


for name, body, count in ALLOW:
    def f(self, body=body, count=count):
        matches = gate.verified_citations(body)
        self.assertEqual(len(matches), count)
        self.assertEqual([m.start() for m in matches], [body.index(m.group(0), 0 if i == 0 else matches[i-1].end()) for i,m in enumerate(matches)])
    setattr(AcceptTransparentCases, 'test_accept_' + name, f)


class ContractAndCustody(unittest.TestCase):
    def test_isolation_rejects_non_str(self):
        with self.assertRaises(gate.CitationPlacementHold):
            gate.verified_citations(b'{{cite:s}}')

    def test_unicode_offsets(self):
        body='☃🔎\n<dialog open><p>雪 {{cite:s}}</p></dialog>'
        self.assertEqual(gate.verified_citations(body)[0].start(), body.index('{{cite:s}}'))

    def test_parent_closed_child_open_does_not_override(self):
        with self.assertRaises(gate.CitationPlacementHold):
            gate.verified_citations('<details><dialog open>{{cite:s}}</dialog></details>')

    def test_escapes_are_not_raw_unmodified(self):
        self.assertEqual(gate._css_unescape(r'\6e one'), 'none')

    def test_ambiguous_css_remains_open_hold(self):
        self.assertIn('independent rendered-browser review', gate.__doc__)

    def test_no_claim_of_safety(self):
        self.assertNotIn('medical_safety_approved', gate.__doc__)


if __name__ == '__main__':
    unittest.main()
