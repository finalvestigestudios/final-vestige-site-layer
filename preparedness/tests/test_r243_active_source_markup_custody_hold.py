"""Adversarial source-only browser action and citation-safety tests for R243."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r243_active_source_markup_custody_hold as gate


class R243Markup(unittest.TestCase):
    def held(self, body):
        result = gate.check_active_markup(body)
        self.assertEqual(result['state'], 'DRAFT_HARD_HOLD')
        for flag in ('release_authorized', 'independent_qd_pass',
                     'source_review_approved', 'medical_safety_verified', 'merchant_approved'):
            self.assertIs(result[flag], False)

    def denied(self, body, why='R243'):
        with self.assertRaisesRegex(ValueError, why):
            gate.check_active_markup(body)

    def test_normal_citations_and_safe_svg(self):
        self.held('<section><p>Read here {{cite:ready-plan}}</p><svg role="img">'
                  '<path d="M0 0 L9 9"/></svg></section>')

    def test_trusted_article_link_token_not_form(self):
        self.held('{{link:ready-plan|Official guide}} {{cite:ready-plan}}')

    def test_safe_source_urls_not_proof_of_source(self):
        self.held('<a href="https://www.ready.gov/plan" target="_blank" rel="noopener noreferrer">Read</a>')
        self.held('<a href="/preparedness/start-here/">Home</a><a href="#source">Source</a>')

    def test_no_external_tracking_script_tags(self):
        self.denied('<script src="https://example.org/pixel.js"></script>')
        self.denied('<iframe src="https://example.org"></iframe>')

    def test_double_encoded_url_cannot_launder(self):
        self.denied('<a href="java&amp;#x73;cript:alert(1)">Read</a>', 'R243')

    def test_protocol_relative_and_backslash_url(self):
        self.denied('<a href="//unreviewed.example/track">Read</a>')
        self.denied('<a href="\\\\unreviewed.example">Read</a>')

    def test_unsafe_tab(self):
        self.denied('<a href="https://example.org" target="_blank">Read</a>', 'R243 unsafe new-tab')
        self.held('<a href="https://example.org" target="_blank" rel="noreferrer noopener">Read</a>')

    def test_no_raw_css_url_or_expression(self):
        self.denied('<p style="background:url(https://example.org/pixel)">Text</p>')
        self.denied('<p style="width:expression(alert(1))">Text</p>')

    def test_duplicate_active_and_url_attrs(self):
        self.denied('<a href="https://example.org" href="javascript:alert(1)">Read</a>','duplicate')
        self.denied('<p style="color:red" style="color:green">Hi</p>','duplicate')

    def test_35_corpus_receipt_is_hold_and_tampering_fails(self):
        roster=[{'n':i,'slug':f'entry-{i:02d}'} for i in range(1,36)]
        records={f'content/articles/entry-{i:02d}.body.html':
                 b'<p>Source {{cite:one-official}}</p>' for i in range(1,36)}
        def audit():
            return gate.audit_active_markup_custody(None,roster,lambda root,path: records[path])
        result=audit()
        self.assertEqual((result['article_count'],result['citation_count']),(35,35))
        self.assertFalse(result['source_review_approved'])
        records['content/articles/entry-12.body.html']=b'<img src="data:text/html,evil">'
        with self.assertRaisesRegex(ValueError,'R243 executable or unreviewed'):
            audit()

    def test_nonstring_inputs_rejected(self):
        with self.assertRaises(ValueError): gate.check_active_markup(b'<p>text</p>')
        with self.assertRaises(ValueError): gate.audit_active_markup_custody(None,[{}],lambda *_:b'')


# Each dynamic method independently checks a genuinely distinct mutation.
ACTIVE_TAG_CASES=('form','input','button','iframe','object','embed','applet','base',
                   'meta','link','portal','script','textarea','select','foreignObject',
                   'animate','animateTransform','animateMotion','set')
for i, tag in enumerate(ACTIVE_TAG_CASES):
    def test(self, tag=tag): self.denied(f'<{tag} id="unsafe-{tag}">x</{tag}>','active authored')
    setattr(R243Markup,f'test_active_tag_{i:02d}_{tag.lower()}',test)

EVENT_NAMES=('onclick','onload','onerror','onfocus','onblur','onmouseover',
             'onpointerenter','onanimationstart','onwheel','onkeyup','onsubmit',
             'ondragstart','onmouseenter','ontouchstart','v-on:click','x-on:click')
for i, name in enumerate(EVENT_NAMES):
    def test(self,name=name): self.denied(f'<p {name}="emit({len(name)})">{{{{cite:ready-plan}}}}</p>','event attribute')
    setattr(R243Markup,f'test_event_{i:02d}_{name.replace(":","_")}',test)

BAD_URLS=('javascript:alert(1)','JaVaScRiPt:alert(1)','java&#x73;cript:alert(1)',
          'java&#10;script:alert(1)','java&#13;script:alert(1)',
          'javascript&#58;alert(1)','vbscript:msgbox(1)','data:text/html,<svg>',
          'file:///etc/passwd','blob:https://example.org/x',
          'javascript%3Aalert(1)','%6aavascript:alert(1)',
          ' //tracker.example/path','\\\\tracker.example/path',
          'ftp://untrusted.example/file', 'wss://untrusted.example/ws',
          'about:blank', 'chrome://settings', 'javascript:\talert(1)',
          'https://safe.example/a\x01b')
for i, url in enumerate(BAD_URLS):
    def test(self,url=url): self.denied('<a href="'+url+'">Source</a>')
    setattr(R243Markup,f'test_bad_url_{i:02d}',test)

BEHAVIOR_ATTRS=('srcdoc','formaction','ping','autofocus','form','formmethod',
                'formenctype','formtarget','formnovalidate','srcset','imagesrcset',
                'sandbox','nonce','integrity','is')
for i, name in enumerate(BEHAVIOR_ATTRS):
    def test(self,name=name): self.denied(f'<p {name}="unsafe">Source</p>','interactive/bypass')
    setattr(R243Markup,f'test_behavior_attribute_{i:02d}',test)

if __name__ == '__main__': unittest.main()
