"""R245 independent syntactic-custody mutants; no article, QD, CMS or release approval."""
import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r240_html_attribute_entity_custody_hold as gate

HOLD_FLAGS = ('release_authorized', 'independent_qd_pass',
              'source_review_approved', 'medical_safety_verified')


class R245ValuelessAttributeCustody(unittest.TestCase):
    def accepts_held(self, markup):
        result = gate.check_html_attribute_entities(markup)
        self.assertEqual(result['state'], 'DRAFT_HARD_HOLD')
        for flag in HOLD_FLAGS:
            self.assertIs(result[flag], False)
        return result

    def rejects(self, markup, text):
        with self.assertRaisesRegex(ValueError, text):
            gate.check_html_attribute_entities(markup)

    def test_direct_reproduction_of_repaired_false_rejection(self):
        result = self.accepts_held('<p data-reviewed class="visible">{{cite:source}}</p>')
        self.assertEqual(result['visibility_attribute_occurrences'], 1)

    def test_valueless_first_middle_last_and_without_neighbor(self):
        for markup in (
            '<p data-reviewed class="visible" data-final>{{cite:source}}</p>',
            '<p class="visible" data-reviewed>{{cite:source}}</p>',
            '<p data-reviewed>{{cite:source}}</p>',
            '<p data-one data-two data-three class="visible">{{cite:source}}</p>',
            '<svg role="img" data-reviewed aria-label="example"><path d="M0 0V9"/></svg>',
        ):
            with self.subTest(markup=markup):
                self.accepts_held(markup)

    def test_all_standard_whitespace_separators(self):
        for spacing in (' ', '\t', '\n', '\r', '\f', '\t \n'):
            with self.subTest(spacing=repr(spacing)):
                self.accepts_held('<div data-ready'+spacing+'class="visible">{{cite:source}}</div>')

    def test_strict_separator_after_quoted_attribute_still_required(self):
        self.rejects('<div data-ready title="ordinary"class="visible">{{cite:source}}</div>',
                     'R242 missing HTML attribute separator')

    def test_encoded_visibility_remains_prohibited_after_valueless(self):
        self.rejects('<p data-ready aria-hidden="tr&#117;e">{{cite:source}}</p>',
                     'encoded visibility-sensitive')

    def test_ambiguous_duplicate_visibility_remains_rejected(self):
        self.rejects('<p data-ready class="a" class="b">{{cite:source}}</p>',
                     'ambiguous duplicate')

    def test_quoted_description_is_not_a_new_attribute(self):
        self.accepts_held('<p data-ready title="style=display:&#110;one" class="visible">{{cite:source}}</p>')

    def test_disallowed_controls_and_unclosed_quote_remain_blocked(self):
        self.rejects('<div data-ready\x00 class="visible">x</div>', 'R242 control')
        self.rejects('<div data-ready title="oops class="visible">x</div>', 'R242 missing')

    def test_full_35_article_roster_with_valueless_attributes(self):
        roster=[{'n':i,'slug':f'record-{i:02d}'} for i in range(1,36)]
        body=b'<p data-verified class="visible">{{cite:source}}</p>'
        files={f'content/articles/record-{i:02d}.body.html':body for i in range(1,36)}
        audit=lambda:gate.audit_attribute_entity_custody(None,roster,lambda root,path:files[path])
        first=audit()
        self.assertEqual(first['article_count'],35)
        self.assertEqual(first['citation_count'],35)
        for flag in HOLD_FLAGS:
            self.assertIs(first[flag],False)
        self.assertEqual(len(first['receipt_sha256']),64)
        files['content/articles/record-17.body.html']=b'<p data-verified class="vis&#105;ble">{{cite:source}}</p>'
        with self.assertRaisesRegex(ValueError,'encoded visibility-sensitive'):
            audit()

    def test_auditor_rejects_duplicate_slug(self):
        roster=[{'n':i,'slug':f'record-{i:02d}'} for i in range(1,36)]
        roster[18]['slug']=roster[17]['slug']
        with self.assertRaisesRegex(ValueError,'duplicate'):
            gate.audit_attribute_entity_custody(None,roster,lambda root,path:b'<p data-ready>x</p>')


# Independently distinct tag/attribute/whitespace combinations, each with a
# paired negative boundary and encoded visibility mutant. Not a publication QA.
TAGS=('p','div','section','article','span','aside','table','svg')
SPACING=(' ','\t','\n','\r','\f','\t \n')
for i in range(48):
    tag=TAGS[i%8]
    spacer=SPACING[i//8]
    label=f'data-reviewed-{i:02d}'
    sample=f'{{{{cite:source-{i}}}}}'
    good=f'<{tag} {label}{spacer}class="visible">{sample}</{tag}>'
    bad=f'<{tag} {label}{spacer}title="ordinary"class="visible">{sample}</{tag}>'
    def valid(markup):
        def run(self): self.accepts_held(markup)
        return run
    def invalid(markup):
        def run(self): self.rejects(markup,'R242 missing HTML attribute separator')
        return run
    setattr(R245ValuelessAttributeCustody,f'test_valueless_valid_{i:02d}',valid(good))
    setattr(R245ValuelessAttributeCustody,f'test_adjacent_quoted_negative_{i:02d}',invalid(bad))

for i in range(24):
    tag=TAGS[i%8]
    key=('class','id','style','aria-hidden')[i%4]
    encoded=('vis&#105;ble','rec&#111;rd','display:&#110;one','tr&#117;e')[i%4]
    sample=f'<{tag} data-reviewed-{i:02d} {key}="{encoded}">{{{{cite:source-{i}}}}}</{tag}>'
    def invalid(markup):
        def run(self): self.rejects(markup,'encoded visibility-sensitive')
        return run
    setattr(R245ValuelessAttributeCustody,f'test_encoded_sensitive_after_valueless_{i:02d}',invalid(sample))

if __name__ == '__main__':
    unittest.main()
