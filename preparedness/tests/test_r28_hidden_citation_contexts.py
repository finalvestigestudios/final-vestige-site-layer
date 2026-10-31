"""R28: tokens in semantically hidden HTML are never supporting claim evidence."""
from __future__ import annotations
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import citation_token_visibility_gate as gate


HIDDEN = [
    ('hidden_boolean', '<p hidden>{{cite:a}}</p>'),
    ('hidden_false_is_boolean', '<p hidden="false">{{cite:a}}</p>'),
    ('hidden_until_found', '<p hidden="until-found">{{cite:a}}</p>'),
    ('inert_boolean', '<section inert>{{cite:a}}</section>'),
    ('inert_false_is_boolean', '<section inert="false">{{cite:a}}</section>'),
    ('aria_true', '<span aria-hidden="true">{{cite:a}}</span>'),
    ('aria_true_caps', '<span aria-hidden="TRUE">{{cite:a}}</span>'),
    ('aria_true_spaced', '<span aria-hidden=" true ">{{cite:a}}</span>'),
    ('display_none', '<p style="display:none">{{cite:a}}</p>'),
    ('display_none_space', '<p style="display : none">{{cite:a}}</p>'),
    ('display_none_caps', '<p style="DISPLAY:NONE">{{cite:a}}</p>'),
    ('display_none_important', '<p style="display:none!important">{{cite:a}}</p>'),
    ('display_none_comment', '<p style="display:/* deliberate */none">{{cite:a}}</p>'),
    ('display_none_after_other', '<p style="color:red;display:none">{{cite:a}}</p>'),
    ('display_none_second_attr', '<p class="x" style="display:none">{{cite:a}}</p>'),
    ('visibility_hidden', '<p style="visibility:hidden">{{cite:a}}</p>'),
    ('visibility_hidden_important', '<p style="visibility: hidden !important">{{cite:a}}</p>'),
    ('visibility_collapse', '<p style="visibility:collapse">{{cite:a}}</p>'),
    ('content_visibility_hidden', '<p style="content-visibility:hidden">{{cite:a}}</p>'),
    ('opacity_zero', '<p style="opacity:0">{{cite:a}}</p>'),
    ('opacity_0_dot_0', '<p style="opacity:0.0">{{cite:a}}</p>'),
    ('opacity_dot_0', '<p style="opacity:.00">{{cite:a}}</p>'),
    ('opacity_zero_percent', '<p style="opacity:0%">{{cite:a}}</p>'),
    ('head', '<head><meta charset="utf-8">{{cite:a}}</head>'),
    ('title', '<title>{{cite:a}}</title>'),
    ('select', '<select>{{cite:a}}</select>'),
    ('option', '<select><option>{{cite:a}}</option></select>'),
    ('optgroup', '<optgroup>{{cite:a}}</optgroup>'),
    ('datalist', '<datalist>{{cite:a}}</datalist>'),
    ('button', '<button>{{cite:a}}</button>'),
    ('hidden_ancestor', '<div hidden><p><b>{{cite:a}}</b></p></div>'),
    ('inert_ancestor', '<section inert><ul><li>{{cite:a}}</li></ul></section>'),
    ('aria_ancestor_overridden_child', '<div aria-hidden="true"><p aria-hidden="false">{{cite:a}}</p></div>'),
    ('style_ancestor', '<section style="visibility:hidden"><p>{{cite:a}}</p></section>'),
    ('hidden_followed_visible_same_source', '<p>{{cite:a}}</p><p hidden>{{cite:a}}</p>'),
    ('hidden_followed_visible_different_source', '<p>{{cite:a}}</p><p inert>{{cite:b}}</p>'),
    ('nested_hidden_then_visible_after', '<div hidden><p>{{cite:a}}</p></div><p>{{cite:b}}</p>'),
    ('nested_option', '<p>{{cite:a}}</p><select><option>{{cite:b}}</option></select>'),
    ('duplicate_style_attributes', '<p style="color:red" style="display:none">{{cite:a}}</p>'),
    ('unicode_hidden', '雪<p aria-hidden="true">☀{{cite:a}}</p>🌙'),
    ('newline_hidden', '<div\nstyle="display:none">\n{{cite:a}}\n</div>'),
]

VISIBLE = [
    ('plain', '<p>Claim {{cite:a}}</p>', 1),
    ('aria_false', '<p aria-hidden="false">{{cite:a}}</p>', 1),
    ('style_block', '<p style="display:block">{{cite:a}}</p>', 1),
    ('style_inline', '<span style="display:inline">{{cite:a}}</span>', 1),
    ('style_visible', '<p style="visibility:visible">{{cite:a}}</p>', 1),
    ('style_opacity_half', '<p style="opacity:0.5">{{cite:a}}</p>', 1),
    ('style_opacity_one', '<p style="opacity:1">{{cite:a}}</p>', 1),
    ('detail_open', '<details open><summary>Sources</summary>{{cite:a}}</details>', 1),
    ('after_hidden_element', '<p hidden>No token</p><p>{{cite:a}}</p>', 1),
    ('after_aria_element', '<p aria-hidden="true">No token</p><p>{{cite:a}}</p>', 1),
    ('after_inert_element', '<p inert>No token</p><p>{{cite:a}}</p>', 1),
    ('after_nested_hidden', '<div hidden><p>No token</p></div><p>{{cite:a}}</p>', 1),
    ('duplicate', '<p>{{cite:a}} <b>{{cite:a}}</b></p>', 2),
    ('unicode_codepoints', '🔎<p>☃{{cite:a}}</p>', 1),
    ('not_source_placeholders', '<p>{{link:home|home}} {{cite:a}}</p>', 1),
    ('visible_list', '<ol><li>{{cite:a}}</li><li>{{cite:b}}</li></ol>', 2),
    ('visible_table', '<table><tr><td>{{cite:a}}</td></tr></table>', 1),
    ('visible_heading', '<h2>{{cite:a}}</h2>', 1),
]

class HiddenContextTests(unittest.TestCase):
    pass

for name, body in HIDDEN:
    def check(self, body=body):
        with self.assertRaises(gate.CitationPlacementHold):
            gate.verified_citations(body)
    setattr(HiddenContextTests, 'test_reject_'+name, check)

class VisibleContextTests(unittest.TestCase):
    pass

for name, body, count in VISIBLE:
    def check(self, body=body, count=count):
        matches = gate.verified_citations(body)
        self.assertEqual(len(matches), count)
        self.assertEqual([m.start() for m in matches], sorted(m.start() for m in matches))
    setattr(VisibleContextTests, 'test_allow_'+name, check)

class BoundaryTests(unittest.TestCase):
    def test_no_browser_computed_style_claim(self):
        self.assertIn('External CSS', gate.__doc__)

    def test_raw_type_only(self):
        with self.assertRaises(gate.CitationPlacementHold):
            gate.verified_citations(b'{{cite:a}}')

    def test_hidden_attributes_is_conservative(self):
        self.assertFalse(gate._hidden_attributes([('class', 'display-none')]))

    def test_no_mutation(self):
        body='<p style="display:block">Claim {{cite:a}}</p>'
        self.assertEqual(gate.verified_citations(body)[0].start(),body.index('{{cite:a}}'))
        self.assertEqual(body,'<p style="display:block">Claim {{cite:a}}</p>')

if __name__=='__main__':
    unittest.main()
