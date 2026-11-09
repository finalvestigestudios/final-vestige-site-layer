"""R239 deterministic synthetic fixtures; never rewrites original manuscripts."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r239_foreign_solidus_custody_hold as r239

class BrowserSolidusTests(unittest.TestCase):
    def reject(self, html, fragment='R239'):
        with self.assertRaisesRegex(ValueError, fragment):
            r239.check_solidus_html(html)

    def test_original_bypass_reproduced_and_blocked(self):
        self.reject('<div hidden/>Text {{cite:ready-plan}}', 'non-void')

    def test_void_html_still_valid(self):
        for x in ('<br/>', '<hr />', '<img alt="a > b"/>', '<meta charset="utf-8" />'):
            self.assertEqual(r239.check_solidus_html(x)['state'], 'DRAFT_HARD_HOLD')

    def test_actual_diagram_syntax_accepted(self):
        html = '<svg role="img"><title>Diagram</title><desc>Text</desc><rect x="1"/><path d="M0 0V9"/></svg>'
        self.assertEqual(r239.check_solidus_html(html)['foreign_self_closing'], 2)

    def test_foreignobject_switches_to_html(self):
        self.reject('<svg><foreignObject><div hidden/></foreignObject></svg>', 'non-void')

    def test_svg_html_breakout_rejected(self):
        self.reject('<svg><div hidden/></svg>', 'unsafe foreign')

    def test_math_html_integration_rejected(self):
        self.reject('<math><mtext><p hidden/></mtext></math>', 'non-void')

    def test_math_self_closing_accepted(self):
        self.assertEqual(r239.check_solidus_html('<math><mi/><mo/><mn/></math>')['foreign_self_closing'], 3)

    def test_hidden_in_quote_unaffected(self):
        self.assertEqual(r239.check_solidus_html('<p title="x /> y">hello</p>')['foreign_self_closing'],0)

    def test_comment_ignored(self):
        self.assertEqual(r239.check_solidus_html('<!-- <div hidden/> --><p>Okay</p>')['state'],'DRAFT_HARD_HOLD')

    def test_rawtext_ignored(self):
        self.assertEqual(r239.check_solidus_html('<script>var x="<div hidden/>";</script>')['state'],'DRAFT_HARD_HOLD')

    def test_declarations_fail_closed(self):
        self.reject('<![CDATA[ignored]]>','unsupported')

    def test_malformed_tag_fails_closed(self):
        self.reject('<p title="never ends','unterminated')

    def test_exact_roster_hold_flags(self):
        roster=[{'n':i, 'slug':f'example-{i}'} for i in range(1,36)]
        def reader(root,path): return b'<p>Source {{cite:ready-plan}}</p>'
        result=r239.audit_solidus_custody(None,roster,reader)
        self.assertEqual(result['article_count'],35)
        self.assertEqual(result['citation_count'],35)
        self.assertEqual(result['state'],'DRAFT_HARD_HOLD')
        self.assertTrue(result['human_review_required'])
        for k in ('release_authorized','independent_qd_pass','source_review_approved','medical_safety_verified'):
            self.assertIs(result[k],False)
        self.assertEqual(result,r239.audit_solidus_custody(None,roster,reader))

    def test_roster_duplicate_rejected(self):
        roster=[{'n':i, 'slug':'duplicate'} for i in range(1,36)]
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            r239.audit_solidus_custody(None,roster,lambda root,path:b'<p>Okay</p>')


def nonvoid_case(i):
    tag=('div','section','aside','p','span','details','article','figure','svg-unknown')[i % 9]
    def check(self): self.reject(f'<{tag} class="c{i}" hidden/> {{'+'{cite:ready-plan}}', 'R239')
    return check

def foreign_case(i):
    def check(self):
        s=f'<svg><foreignObject id="foreign-{i}"><div hidden/> Hidden</foreignObject></svg>'
        self.reject(s,'non-void')
    return check

def valid_svg_case(i):
    def check(self):
        html=f'<svg><rect x="{i}"/><path d="M{i} 0"/></svg><p>Ready {{'+'{cite:ready-plan}}</p>'
        self.assertEqual(r239.check_solidus_html(html)['foreign_self_closing'],2)
    return check

for i in range(1,36):
    setattr(BrowserSolidusTests,f'test_{i:02d}_nonvoid_hidden_solidus',nonvoid_case(i))
    setattr(BrowserSolidusTests,f'test_{i:02d}_html_in_svg_solidus',foreign_case(i))
    setattr(BrowserSolidusTests,f'test_{i:02d}_authored_svg_shape',valid_svg_case(i))

if __name__=='__main__': unittest.main()
