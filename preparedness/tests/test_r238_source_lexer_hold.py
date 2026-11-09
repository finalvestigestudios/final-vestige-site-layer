"""Synthetic only: isolated citation lexing adversarial regressions (no original edits)."""
import hashlib
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r238_source_lexer_hold as gate

class LexerTests(unittest.TestCase):
    def check_reject(self, s, msg='R238'):
        with self.assertRaisesRegex(ValueError, msg): gate.visible_citations(s)

    def test_good_visible(self):
        self.assertEqual(gate.visible_citations('<p>Household plan. {{cite:start-ready-plan}}</p>'),
                         [(19, 'start-ready-plan')])

    def test_determinism_and_hard_hold(self):
        class Root: pass
        rows=[{'n':i,'slug':f'example-{i}'} for i in range(1,36)]
        result=gate.audit_source_visibility(Root(),rows,lambda root,path:b'<p>Plan. {{cite:ready-plan}}</p>')
        self.assertEqual((result['article_count'],result['citation_count']),(35,35))
        self.assertEqual(result['state'],'DRAFT_HARD_HOLD')
        self.assertTrue(result['human_review_required'])
        for k in ['source_approved','medical_safety_verified','independent_qd_pass','release_authorized']:
            self.assertIs(result[k],False)
        self.assertEqual(result['receipt_sha256'],gate.audit_source_visibility(Root(),rows,lambda root,path:b'<p>Plan. {{cite:ready-plan}}</p>')['receipt_sha256'])

    def test_quote_tag_ends_correctly(self):
        self.assertEqual(gate.tag_end('<p title="x > y">Hi',0),16)

    def test_broken_token(self): self.check_reject('<p>Plan {{cite:ready-plan</p>')
    def test_raw_script(self): self.check_reject('<script>" > {{cite:ready-plan}}"</script>')
    def test_comment(self): self.check_reject('<!-- X > {{cite:ready-plan}} -->')
    def test_unclosed_comment(self): self.check_reject('<!-- > {{cite:ready-plan}}', 'unterminated comment')
    def test_unclosed_script(self): self.check_reject('<script>" > {{cite:ready-plan}}', 'unterminated nonreader')
    def test_plaintext(self): self.check_reject('<plaintext> {{cite:ready-plan}}', 'plaintext')
    def test_unquoted(self): self.check_reject('<p title=" > {{cite:ready-plan}} >', 'unterminated')
    def test_hidden(self): self.check_reject('<div hidden><p>Use {{cite:ready-plan}}</p></div>')
    def test_visible_after_hidden(self):
        self.assertEqual(len(gate.visible_citations('<div hidden>No links</div><p>Plan {{cite:ready-plan}}</p>')),1)
    def test_aria(self): self.check_reject('<span aria-hidden="true">Hidden {{cite:ready-plan}}</span>')
    def test_display_none(self): self.check_reject('<div style="display: none">Hidden {{cite:ready-plan}}</div>')
    def test_visibility_hidden(self): self.check_reject('<p style="visibility:hidden">Invisible {{cite:ready-plan}}</p>')
    def test_inert(self): self.check_reject('<section inert>Hidden {{cite:ready-plan}}</section>')
    def test_template(self): self.check_reject('<template>Hidden {{cite:ready-plan}}</template>')
    def test_nested_template_bypass(self): self.check_reject('<template><template>x</template>{{cite:ready-plan}}</template>', 'nested template')
    def test_nested_template_without_citation_still_requires_review(self): self.check_reject('<template><template>x</template>y</template>', 'nested template')
    def test_svg_quote(self): self.check_reject('<svg title="x > {{cite:ready-plan}}">hi</svg>')
    def test_malformed_doctype(self): self.check_reject('<![CDATA[ > {{cite:ready-plan}}]]>')
    def test_nested_hidden(self): self.check_reject('<div hidden><p><b>Invisible {{cite:ready-plan}}</b></p></div>')


def case_html_attr(i):
    def test(self):
        text=f'<p data-source="test {i} > {{'+'{cite:ready-plan}}'+f'" >source</p>'
        self.check_reject(text, 'citation in HTML tag')
    return test

def case_comment(i):
    def test(self): self.check_reject(f'<!-- note {i} > '+'{{cite:ready-plan}}'+' -->','citation in HTML comment')
    return test

def case_opaque(i):
    def test(self): self.check_reject(f'<div aria-hidden="true"><p>Hidden {i}: '+'{{cite:ready-plan}}'+'</p></div>')
    return test

def case_valid(i):
    def test(self):
        prefix=f'<section><p title="extra > {i}">Plan {i}. '
        body=prefix+'{{cite:ready-plan}}</p></section>'
        self.assertEqual(gate.visible_citations(body),[(len(prefix),'ready-plan')])
    return test

for n in range(1,36):
    setattr(LexerTests,f'test_{n:02d}_attr_with_gt',case_html_attr(n))
    setattr(LexerTests,f'test_{n:02d}_comment_with_gt',case_comment(n))
    setattr(LexerTests,f'test_{n:02d}_hidden_container',case_opaque(n))
    setattr(LexerTests,f'test_{n:02d}_valid_quote_gt',case_valid(n))

if __name__=='__main__':unittest.main()
