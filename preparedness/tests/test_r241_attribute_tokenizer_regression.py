"""R241 exact-attribute lexical regressions, release-hard-hold custody."""
import hashlib
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r240_html_attribute_entity_custody_hold as gate


class ScopedEntityTests(unittest.TestCase):
    def block(self, value):
        with self.assertRaisesRegex(ValueError, 'R241'):
            gate.check_html_attribute_entities(value)

    def pass_held(self, value):
        receipt=gate.check_html_attribute_entities(value)
        self.assertEqual(receipt['state'], 'DRAFT_HARD_HOLD')
        self.assertFalse(receipt['release_authorized'])
        self.assertFalse(receipt['independent_qd_pass'])
        self.assertFalse(receipt['source_review_approved'])
        self.assertFalse(receipt['medical_safety_verified'])

    def test_original_false_positive_reproduced_corrected(self):
        self.pass_held('<div title="class=\'x&amp;y\'" class="visible">{{cite:sample}}</div>')
        self.pass_held('<div title="aria-hidden=\'tr&#117;e\'" aria-hidden="false">{{cite:sample}}</div>')
        self.pass_held('<p data-case="style=display:&#110;one" style="display:block">{{cite:sample}}</p>')

    def test_original_true_hiding_bypasses_blocked(self):
        for html in ('<p aria-hidden="tr&#117;e">{{cite:a}}</p>',
                     '<p STYLE="display:&#110;one">{{cite:a}}</p>',
                     "<p class='pa-&#104;idden'>{{cite:a}}</p>",
                     '<div id=&#104;idden>{{cite:a}}</div>'):
            with self.subTest(html=html): self.block(html)

    def test_quote_aware_gt_and_svg(self):
        self.pass_held('<div title="class=\'a&gt;b\'" class="pa-visible">{{cite:a}}</div>')
        self.pass_held('<svg role="img" aria-label="A &amp; B"><path d="M0 0V9"/></svg>')
        self.block('<div title="a > b" aria-hidden="tr&#117;e">{{cite:a}}</div>')

    def test_sensitive_duplicates(self):
        for key in ('style','id','class','aria-hidden'):
            with self.subTest(key=key): self.block('<p '+key+'="one" '+key.upper()+'="two">{{cite:x}}</p>')

    def test_malformed_quoted_inputs(self):
        for html in ('<p data-note="good" class="bad"x="1">{{cite:a}}</p>',
                     '<p class= "pa-&#104;idden"/>{{cite:a}}',
                     '<p data-note="class=\'x&amp;y\'" style="display:&#110;one">{{cite:a}}</p>'):
            if '&#104;' in html or '&#110;' in html:
                self.block(html)
            else:
                try:
                    gate.check_html_attribute_entities(html)
                except ValueError as e:
                    self.assertIn('R241', str(e))

    def test_source_custody(self):
        roster=[{'n':i, 'slug':f'article-{i}'} for i in range(1, 36)]
        files={f'content/articles/article-{i}.body.html':b'<p>{{cite:a}}</p>' for i in range(1,36)}
        audit=lambda:gate.audit_attribute_entity_custody(None, roster, lambda root,path: files[path])
        original=audit()
        self.assertEqual((original['article_count'],original['citation_count']),(35,35))
        files['content/articles/article-20.body.html']=b'<div title="class=\'x&amp;y\'" class="visible">{{cite:a}}</div>'
        self.assertNotEqual(audit()['receipt_sha256'],original['receipt_sha256'])
        files['content/articles/article-20.body.html']=b'<p aria-hidden="tr&#117;e">{{cite:a}}</p>'
        self.block(files['content/articles/article-20.body.html'].decode())
        with self.assertRaisesRegex(ValueError,'R241'):audit()

# Individual unittest case for each mutation; unlike nested subTests, each
# is counted independently and can be tracked in CI when eventually available.
for case in range(55):
    def make_benign(i):
        def test(self):
            fake=('class', 'id', 'style', 'aria-hidden')[i % 4]
            marker=('&amp;', '&#104;', '&#x6e;', '&Tab;', '&#116;')[i % 5]
            # These spellings are within unrelated quoted attribute values.
            html='<div title="%s=\'text%s\'" data-note="x > y" class="pa-visible">{{cite:a}}</div>'%(fake,marker)
            self.pass_held(html)
        return test
    def make_block(i):
        def test(self):
            target=('class','id','style','aria-hidden')[i % 4]
            marker=('&amp;','&#104;','&#x6e;','&Tab;','&#116;')[i % 5]
            html='<div data-note="%s=\'plain\'" %s="pa-%s-hidden">{{cite:a}}</div>'%(target,target,marker)
            self.block(html)
        return test
    setattr(ScopedEntityTests,f'test_unrelated_quoted_entity_{case:02d}',make_benign(case))
    setattr(ScopedEntityTests,f'test_real_encoded_sensitive_{case:02d}',make_block(case))

if __name__=='__main__': unittest.main()
