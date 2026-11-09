"""R242 unique HTML-tag grammar mutants; no article, CMS or QD approvals."""
import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r240_html_attribute_entity_custody_hold as gate

class R242AttributeBoundary(unittest.TestCase):
    def held(self, text):
        result = gate.check_html_attribute_entities(text)
        self.assertEqual(result['state'], 'DRAFT_HARD_HOLD')
        for field in ('release_authorized','independent_qd_pass','source_review_approved','medical_safety_verified'):
            self.assertIs(result[field], False)

    def blocked(self, text, fragment='R242'):
        with self.assertRaisesRegex(ValueError, fragment):
            gate.check_html_attribute_entities(text)

    def test_control_character_hard_hold(self):
        for c in ('\x00','\x01','\x08','\x0b','\x0e','\x1f','\x7f'):
            with self.subTest(c=ord(c)):
                self.blocked('<p title="A'+c+'B" class="visible">{{cite:x}}</p>','R242 control')

    def test_allowed_ascii_html_whitespace(self):
        for c in (' ','\t','\r','\n','\f'):
            with self.subTest(ord=ord(c)):
                self.held('<p title="legitimate"'+c+'class="visible">{{cite:x}}</p>')

    def test_quoted_less_than_is_browser_ambiguous(self):
        self.blocked('<p title="a<b" class="visible">{{cite:x}}</p>','R242 malformed')
        self.held('<p title="a&lt;b" class="visible">{{cite:x}}</p>')

    def test_actual_encoded_visibility_rejected(self):
        for field,raw in (('aria-hidden','tr&#117;e'),('style','display:&#110;one'),
                          ('class','pa-&#104;idden'),('id','&#x68;idden')):
            with self.subTest(field=field):
                self.blocked(f'<p {field}="{raw}">{{{{cite:x}}}}</p>','encoded visibility')

    def test_unrelated_quoted_attribute_entity_not_scanned(self):
        self.held('<p title="class=\'x&amp;y\'" class="visible">{{cite:x}}</p>')
        self.held('<p data-note="style=display:&#110;one" style="display:block">{{cite:x}}</p>')

    def test_no_publicity_flags_in_roster_receipt(self):
        roster=[{'n':i,'slug':f'record-{i:02d}'} for i in range(1,36)]
        body=b'<p class="visible">{{cite:source}}</p>'
        fs={f'content/articles/record-{i:02d}.body.html':body for i in range(1,36)}
        audit=lambda: gate.audit_attribute_entity_custody(None,roster,lambda root,path:fs[path])
        baseline=audit()
        self.assertEqual((baseline['article_count'],baseline['citation_count']),(35,35))
        self.assertFalse(baseline['medical_safety_verified'])
        fs['content/articles/record-27.body.html']=b'<p title="x"class="visible">{{cite:source}}</p>'
        with self.assertRaisesRegex(ValueError,'R242 missing'): audit()

    def test_attribute_value_parser_parity(self):
        self.held('<p title="A &amp; B &gt; C" data-note=sample-12 class=visible>{{cite:x}}</p>')
        self.held('<svg role="img" aria-label="A &amp; B"><path d="M0 0V9"/></svg>')

# Unlike previous cyclic generators, each case uses a unique tag, attribute
# spelling and source value, and every negative has its paired valid markup.
for i in range(44):
    tag=('p','div','section','article','aside','span','em','strong')[i%8]
    left=f'data-research-snapshot-{i:02d}'
    val=f'citation-{i:02d}-record'
    right=('class','aria-hidden','id','style')[i%4]
    rval=('pa-visible','false',f'anchor-{i:02d}','display:block')[i%4]
    glue='"' if i%2==0 else "'"
    invalid=f'<{tag} {left}={glue}{val}{glue}{right}={glue}{rval}{glue}>{{{{cite:source-{i}}}}}</{tag}>'
    valid=f'<{tag} {left}={glue}{val}{glue} {right}={glue}{rval}{glue}>{{{{cite:source-{i}}}}}</{tag}>'
    def negative(html):
        def test(self): self.blocked(html,'R242 missing HTML attribute separator')
        return test
    def positive(html):
        def test(self): self.held(html)
        return test
    setattr(R242AttributeBoundary,f'test_missing_separator_{i:02d}',negative(invalid))
    setattr(R242AttributeBoundary,f'test_separated_attributes_{i:02d}',positive(valid))

if __name__=='__main__': unittest.main()
