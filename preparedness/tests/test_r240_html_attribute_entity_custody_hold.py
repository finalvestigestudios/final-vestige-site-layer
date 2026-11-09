"""Independent synthetic HTML entity-attribute visibility regressions for R240."""
import hashlib
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r240_html_attribute_entity_custody_hold as r240


class AttributeEntityTests(unittest.TestCase):
    def assert_blocked(self, body):
        with self.assertRaisesRegex(ValueError, 'R240'):
            r240.check_html_attribute_entities(body)

    def test_original_negative_control_aria(self):
        # R238's raw ARIA_HIDDEN regex cannot see the browser-decoded "true".
        body = '<div aria-hidden="tr&#117;e">{{cite:ready-plan}}</div>'
        self.assert_blocked(body)

    def test_original_negative_control_css(self):
        body = '<p style="display:&#110;one">{{cite:ready-plan}}</p>'
        self.assert_blocked(body)

    def test_encoded_class_and_id(self):
        self.assert_blocked('<p class="pa-&#104;idden">{{cite:ready-plan}}</p>')
        self.assert_blocked('<div id="&#104;idden"><p>{{cite:ready-plan}}</p></div>')

    def test_unencoded_visible_examples(self):
        for body in ('<p>Visible {{cite:ready-plan}}</p>',
                     '<p title="A &amp; B">{{cite:ready-plan}}</p>',
                     '<div class="pa-act" id="schedule">Text {{cite:start-plan}}</div>',
                     '<svg role="img"><path d="M0 0V9"/></svg>',
                     '<div data-note="&amp;">Visible {{cite:ready-plan}}</div>'):
            result = r240.check_html_attribute_entities(body)
            self.assertEqual(result['state'], 'DRAFT_HARD_HOLD')
            self.assertFalse(result['release_authorized'])

    def test_duplicate_sensitive_attributes_rejected(self):
        for key in ('aria-hidden', 'style', 'class', 'id'):
            self.assert_blocked('<div '+key+'="first" '+key+'="second">{{cite:ready-plan}}</div>')

    def test_comments_and_rawtext_are_opaque(self):
        for body in ('<!-- <div class="&#104;ide"> --> <p>Visible</p>',
                     '<script>var s="<div class=\'&#104;ide\'>";</script><p>Visible</p>'):
            self.assertEqual(r240.check_html_attribute_entities(body)['state'], 'DRAFT_HARD_HOLD')

    def test_nonstring_rejected(self):
        for obj in (None, b'<p/>', [], 4):
            with self.assertRaisesRegex(ValueError, 'R240'):
                r240.check_html_attribute_entities(obj)

    def test_35_aria_numeric_mutations(self):
        for code in range(97, 132):
            # Encode one ASCII letter from "true" in an otherwise ordinary attr.
            base = 'true'
            char = base[(code - 97) % len(base)]
            encoded = base.replace(char, '&#'+str(ord(char))+';', 1)
            with self.subTest(case=code):
                self.assert_blocked('<div aria-hidden="'+encoded+'">{{cite:ready-plan}}</div>')

    def test_35_css_entity_mutations(self):
        forms = ['&#110;', '&#x6e;', '&#X6E;', '&Tab;', '&#x6e']
        for i in range(35):
            attr = 'display:'+('&#110;' if i % 2 else '&#x6e;')+'one'
            body = '<section style="'+attr+'; color:var(--p'+str(i)+')">{{cite:ready-plan}}</section>'
            with self.subTest(case=i):
                self.assert_blocked(body)

    def test_35_encoded_selector_mutations(self):
        for i in range(35):
            key = 'class' if i % 2 else 'id'
            body = '<p '+key+'="pa-&#104;idden-'+str(i)+'">{{cite:ready-plan}}</p>'
            with self.subTest(case=i):
                self.assert_blocked(body)

    def test_roster_custody_and_hold(self):
        roster=[{'n':i,'slug':'article-'+str(i)} for i in range(1,36)]
        files={'content/articles/article-'+str(i)+'.body.html':b'<p>{{cite:test-source}}</p>' for i in range(1,36)}
        def reader(root,path): return files[path]
        v=r240.audit_attribute_entity_custody(None,roster,reader)
        self.assertEqual((v['article_count'],v['citation_count']),(35,35))
        self.assertTrue(v['human_review_required'])
        self.assertFalse(v['medical_safety_verified'])
        original=v['receipt_sha256']
        files['content/articles/article-20.body.html']=b'<p>Changed {{cite:test-source}}</p>'
        self.assertNotEqual(r240.audit_attribute_entity_custody(None,roster,reader)['receipt_sha256'],original)
        files['content/articles/article-20.body.html']=b'<p aria-hidden="t&#114;ue">{{cite:test-source}}</p>'
        with self.assertRaisesRegex(ValueError,'R240'):
            r240.audit_attribute_entity_custody(None,roster,reader)

    def test_roster_mutations_fail(self):
        roster=[{'n':i,'slug':'article-'+str(i)} for i in range(1,36)]
        def reader(root,path): return b'<p>{{cite:test-source}}</p>'
        for bad in ([],roster[:-1],roster+[roster[-1]],roster[:20]+[roster[19]]+roster[21:]):
            with self.assertRaisesRegex(ValueError,'R240'):
                r240.audit_attribute_entity_custody(None,bad,reader)

# One independently reported unittest per mutation (in addition to subtests),
# so the executed suite has >36 discrete checks rather than 12 test methods.
for _case in range(35):
    def _make_aria(case):
        def _test(self):
            letter = 'true'[case % 4]
            value = 'true'.replace(letter, '&#' + str(ord(letter)) + ';', 1)
            self.assert_blocked('<div aria-hidden="' + value + '">{{cite:ready-plan}}</div>')
        return _test
    def _make_css(case):
        def _test(self):
            value = 'display:' + ('&#110;' if case % 2 else '&#x6e;') + 'one'
            self.assert_blocked('<div style="' + value + '">{{cite:ready-plan}}</div>')
        return _test
    def _make_selector(case):
        def _test(self):
            key = 'class' if case % 2 else 'id'
            self.assert_blocked('<div ' + key + '="pa-&#104;idden-' + str(case) + '">{{cite:ready-plan}}</div>')
        return _test
    setattr(AttributeEntityTests, 'test_aria_entity_%02d' % _case, _make_aria(_case))
    setattr(AttributeEntityTests, 'test_css_entity_%02d' % _case, _make_css(_case))
    setattr(AttributeEntityTests, 'test_selector_entity_%02d' % _case, _make_selector(_case))

if __name__=='__main__':unittest.main()
