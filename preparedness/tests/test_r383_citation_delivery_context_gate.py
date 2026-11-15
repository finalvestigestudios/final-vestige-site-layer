"""R383 synthetic HTML trust-boundary and source claim delivery tests."""
from pathlib import Path
import importlib.util
import unittest

PATH=Path(__file__).resolve().parents[1]/'tools'/'r383_citation_delivery_context_gate.py'
spec=importlib.util.spec_from_file_location('r383_gate',PATH)
G=importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
CLAIM='Household guidance must preserve source context, uncertainty, and safety caveats.'
GOOD='<p>'+CLAIM+'{{cite:src-a}}</p>'
META={'status':{'publish':'draft'},'safety_review':{'state':'pending'},'source_use':{'src-a':'Direct supported source reading scope'}}

def check(html, error=None, meta=None):
    out=G.examine(html.encode(),META if meta is None else meta,{'src-a'})
    assert not out['publication_approved'] and not out['qualified_safety_approved'] and not out['verified_human_source']
    if error: assert error in out['errors'],(error,out)
    else: assert not out['errors'],out
    return out

class Invariants(unittest.TestCase):
    def test_base_stays_hard_hold(self):
        self.assertEqual(check(GOOD)['status'],'STATIC_DELIVERY_REVIEW_HARD_HOLD')
    def test_historical_label_not_qd(self):
        m={**META,'safety_review':{'state':'approved','reviewer':'founder'}}
        self.assertIn('HISTORICAL_LABEL_NOT_INDEPENDENT_QD',check(GOOD,meta=m)['warnings'])
    def test_not_required_is_not_qd(self):
        m={**META,'safety_review':{'state':'not-required'}}
        self.assertFalse(check(GOOD,meta=m)['qualified_safety_approved'])
    def test_non_utf8(self):
        self.assertIn('BODY_UTF8_INVALID',G.examine(b'\xff',META,{'src-a'})['errors'])
    def test_bad_metadata(self):
        self.assertIn('METADATA_INVALID',G.examine(GOOD.encode(),None,{'src-a'})['errors'])
    def test_publication_rejected(self):
        check(GOOD,'NOT_DRAFT',{**META,'status':{'publish':'published'}})
    def test_fake_qd_rejected(self):
        check(GOOD,'HISTORICAL_SAFETY_STATE_INVALID',{**META,'safety_review':{'state':'QD PASS'}})
    def test_source_use_missing(self):
        check(GOOD,'MISSING_SOURCE_USE:src-a',{**META,'source_use':{}})
    def test_source_use_wrong_type(self):
        check(GOOD,'SOURCE_USE_INVALID',{**META,'source_use':[]})
    def test_unknown_source(self):
        check('<p>'+CLAIM+'{{cite:bogus}}</p>','UNKNOWN_SOURCE:bogus')
    def test_duplicate_citation_is_warning(self):
        v=check('<p>'+CLAIM+'{{cite:src-a}} Additional.{{cite:src-a}}</p>')
        self.assertIn('REPEATED_SOURCE_WITHIN_CLAIM:1',v['warnings'])
    def test_missing_body_block(self):
        check(CLAIM+'{{cite:src-a}}','CITATION_OUTSIDE_CLAIM_BLOCK')
    def test_source_cited_in_button(self):
        check('<button><p>'+CLAIM+'{{cite:src-a}}</p></button>','CITATION_INTERACTIVE_CONTROL')
    def test_source_cited_in_link(self):
        check('<p><a href="https://example.com">'+CLAIM+'{{cite:src-a}}</a></p>','CITATION_LINK_TEXT_CITATION')
    def test_encoded_citation_not_exempt(self):
        check('<p>'+CLAIM+'&#123;&#123;cite:src-a&#125;&#125;</p>','ENTITY_ESCAPED_CITATION')
    def test_comment_not_claim(self):
        check('<!-- {{cite:src-a}} -->','CITATION_IN_NONCONTENT')
    def test_malformed_literal(self):
        check('<p>'+CLAIM+'{{cite:src_a}}</p>','INVALID_LITERAL_CITATION')
    def test_unsigned_manifest_hard_hold(self):
        self.assertEqual(G.audit({}, {},lambda _:b'')['status'],'INVALID_HARD_HOLD')
    def test_nonobject_manifest_hard_hold(self):
        self.assertIn('UNTRUSTED_INPUT',G.audit(None, {},lambda _:b'')['errors'])
    def test_external_css_unknown(self):
        self.assertIn('EXTERNAL_CSS_JS_BROWSER_SCREENREADER_AND_PRINT_UNVERIFIED',check(GOOD)['warnings'])

class Matrix(unittest.TestCase): pass

def case(name,html,reason=None):
    def test(self):
        out=check(html,reason)
        self.assertIn('HARD_HOLD',out['status'])
    setattr(Matrix,'test_'+name,test)

for tag in sorted(G.CONTEXT):
    case('valid_claim_'+tag,'<'+tag+'>'+CLAIM+'{{cite:src-a}}</'+tag+'>')
for tag in sorted(G.INTERACTIVE - {'input'}):
    case('interactive_'+tag,'<'+tag+'><p>'+CLAIM+'{{cite:src-a}}</p></'+tag+'>','CITATION_INTERACTIVE_CONTROL')
for tag in sorted(G.UNKNOWN_RENDER):
    case('nonreader_'+tag,'<'+tag+'><p>'+CLAIM+'{{cite:src-a}}</p></'+tag+'>','CITATION_NON_READER_REGION')
for css in ['opacity:0','opacity: 0!important','font-size:0','font-size:0px','font-size: 0em',
            'transform: scale(0)','clip-path:inset(100%)','content-visibility:hidden',
            'overflow:hidden;height:0','overflow:hidden;width:0px',
            'position:absolute;left:-9999px','display:none','visibility:collapse']:
    case('css_'+str(len(Matrix.__dict__)),'<p style="'+css+'">'+CLAIM+'{{cite:src-a}}</p>',
         'CITATION_'+G.style_risks(css)[0])
for attrib in ['hidden','inert','aria-hidden="true"']:
    case('attr_'+str(len(Matrix.__dict__)),'<p '+attrib+'>'+CLAIM+'{{cite:src-a}}</p>', 'CITATION_ATTRIBUTE_HIDDEN')
for text in ['', 'a', 'See also.', 'Source.']:
    case('thin_claim_'+str(len(Matrix.__dict__)),'<p>'+text+'{{cite:src-a}}</p>','CITATION_WITHOUT_SUBSTANTIVE_CLAIM:1')
for raw in ['<p>{{cite:</p>','<p>{{cite:UPPER}}</p>','<p>{{cite: a}}</p>','<p>{{cite:src-a}</p>']:
    case('malformed_'+str(len(Matrix.__dict__)),raw,'INVALID_LITERAL_CITATION')

if __name__=='__main__': unittest.main()
