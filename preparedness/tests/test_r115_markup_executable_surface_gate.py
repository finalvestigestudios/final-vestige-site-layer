"""R115 deterministic isolated adversarial coverage. No repository fixture writes."""
import copy
import importlib.util
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/'tools/r115_markup_executable_surface_gate.py'
spec=importlib.util.spec_from_file_location('r115',PATH)
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
BODY='<section><h2 id="act">Household planning</h2><p>Test paragraph. {{cite:s1}}</p><p>{{link:guide-two|Guide two}}</p></section>'

def fixture():
    return ({'slug':'guide-one','section':'start-here','track':'modern','_body':BODY,
            'status':{'editorial':'drafted','publish':'draft'},
            'safety_review':{'state':'pending'}},
            {'slug':'guide-one','section':'start-here','track':'modern','gate':True})

class Base(unittest.TestCase):
    def test_hold(self):
        m,t=fixture();out=g.inspect(m,t)
        self.assertFalse(out['may_publish']);self.assertEqual(out['qualified_safety_review'],'NOT_REVIEWED')
    def test_normal_markup_has_no_new_flags(self):
        self.assertEqual(g.inspect(*fixture())['flags'],[])
    def test_deterministic(self):
        self.assertEqual(g.inspect(*fixture()),g.inspect(*fixture()))
    def test_no_mutation(self):
        m,t=fixture();before=copy.deepcopy((m,t));g.inspect(m,t)
        self.assertEqual((m,t),before)
    def test_no_raw_prose_or_url(self):
        self.assertNotIn('Test paragraph',str(g.inspect(*fixture())))
    def test_no_body(self):
        m,t=fixture();del m['_body']
        with self.assertRaises(g.Blocked):g.inspect(m,t)
    def test_no_dict(self):
        with self.assertRaises(g.Blocked):g.inspect('bad',{})
    def test_no_citation(self):
        m,t=fixture();m['_body']=m['_body'].replace('{{cite:s1}}','')
        self.assertIn('NO_READING_CONTEXT_SOURCE_TOKENS',g.inspect(m,t)['flags'])

ATTACKS = [
('onclick','<div onclick="alert(1)">X</div>','EVENT_HANDLER_ATTRIBUTE'),
('onload','<img onload="evil()">','EVENT_HANDLER_ATTRIBUTE'),
('onerror','<img src="x" onerror="go()">','EVENT_HANDLER_ATTRIBUTE'),
('onfocus','<a onfocus="go()">Go</a>','EVENT_HANDLER_ATTRIBUTE'),
('onmouseover','<a onmouseover="go()">Go</a>','EVENT_HANDLER_ATTRIBUTE'),
('ontouchstart','<p ontouchstart="go()">Hi</p>','EVENT_HANDLER_ATTRIBUTE'),
('onkeydown','<div onkeydown="go()">Go</div>','EVENT_HANDLER_ATTRIBUTE'),
('duplicate_attr','<a href="/ok" href="javascript:bad">Go</a>','REPEATED_HTML_ATTRIBUTE'),
('javascript','<a href="javascript:evil()">Go</a>','UNSAFE_LINK_SCHEME'),
('vbscript','<a href="vbscript:evil()">Go</a>','UNSAFE_LINK_SCHEME'),
('data','<a href="data:text/html,hi">Go</a>','UNSAFE_LINK_SCHEME'),
('blob','<img src="blob:abc">','UNSAFE_LINK_SCHEME'),
('file','<a href="file:///etc/passwd">Go</a>','UNSAFE_LINK_SCHEME'),
('customscheme','<a href="foo:bar">Go</a>','UNAPPROVED_LINK_SCHEME'),
('ftp','<a href="ftp://x">Go</a>','UNAPPROVED_LINK_SCHEME'),
('srcdoc','<iframe srcdoc="X"></iframe>','HIGH_RISK_HTML_ATTRIBUTE'),
('formaction','<button formaction="/x">Submit</button>','HIGH_RISK_HTML_ATTRIBUTE'),
('httpequiv','<p http-equiv="refresh">Test</p>','HIGH_RISK_HTML_ATTRIBUTE'),
('autofocus','<button autofocus>Test</button>','HIGH_RISK_HTML_ATTRIBUTE'),
('cssurl','<p style="background:url(https://x)">Go</p>','ACTIVE_INLINE_STYLE'),
('cssexpression','<p style="width:expression(alert(1))">Go</p>','ACTIVE_INLINE_STYLE'),
('cssimport','<p style="@import url(x)">Go</p>','ACTIVE_INLINE_STYLE'),
('cssmoz','<p style="-moz-binding:url(x)">Go</p>','ACTIVE_INLINE_STYLE'),
('script','<script>evil()</script>','EXECUTABLE_OR_EMBEDDED_ELEMENT'),
('form','<form action="/x"><p>Hi</p></form>','EXECUTABLE_OR_EMBEDDED_ELEMENT'),
('iframe','<iframe src="https://x"></iframe>','EXECUTABLE_OR_EMBEDDED_ELEMENT'),
('object','<object data="/x"></object>','EXECUTABLE_OR_EMBEDDED_ELEMENT'),
('embed','<embed src="/x">','EXECUTABLE_OR_EMBEDDED_ELEMENT'),
('svg','<svg><text>Hi</text></svg>','EXECUTABLE_OR_EMBEDDED_ELEMENT'),
('math','<math><mi>x</mi></math>','EXECUTABLE_OR_EMBEDDED_ELEMENT'),
('link','<link rel="stylesheet" href="/x">','EXECUTABLE_OR_EMBEDDED_ELEMENT'),
('meta','<meta http-equiv="refresh" content="0">','EXECUTABLE_OR_EMBEDDED_ELEMENT'),
('base','<base href="/">','EXECUTABLE_OR_EMBEDDED_ELEMENT'),
('title','<title>{{cite:s1}}</title>','SOURCE_TOKEN_IN_NONREADING_CONTEXT'),
('textarea','<textarea>{{cite:s1}}</textarea>','SOURCE_TOKEN_IN_NONREADING_CONTEXT'),
('option','<select><option>{{cite:s1}}</option></select>','SOURCE_TOKEN_IN_NONREADING_CONTEXT'),
('select','<select>{{link:guide-two|Guide}}</select>','SOURCE_TOKEN_IN_NONREADING_CONTEXT'),
('head','<head>{{cite:s1}}</head>','SOURCE_TOKEN_IN_NONREADING_CONTEXT'),
('canvas','<canvas>{{cite:s1}}</canvas>','SOURCE_TOKEN_IN_NONREADING_CONTEXT'),
('picture','<picture>{{cite:s1}}</picture>','SOURCE_TOKEN_IN_NONREADING_CONTEXT'),
('data_attr','<div data-source="{{cite:s1}}">Go</div>','SOURCE_TOKEN_IN_ATTRIBUTE'),
('title_attr','<p title="{{cite:s1}}">Go</p>','SOURCE_TOKEN_IN_ATTRIBUTE'),
('style_attr','<p style="{{cite:s1}}">Go</p>','SOURCE_TOKEN_IN_ATTRIBUTE'),
('hidden','<p hidden>{{cite:s1}}</p>','SOURCE_TOKEN_IN_NONREADING_CONTEXT'),
('inert','<p inert>{{cite:s1}}</p>','SOURCE_TOKEN_IN_NONREADING_CONTEXT'),
('ariahidden','<p aria-hidden="true">{{cite:s1}}</p>','SOURCE_TOKEN_IN_NONREADING_CONTEXT'),
('srclass','<p class="sr-only">{{cite:s1}}</p>','SOURCE_TOKEN_IN_NONREADING_CONTEXT'),
('hiddenancestor','<div hidden><p>{{cite:s1}}</p></div>','SOURCE_TOKEN_IN_NONREADING_CONTEXT'),
('style_hidden','<p style="display:none">{{cite:s1}}</p>','SOURCE_TOKEN_IN_NONREADING_CONTEXT'),
('comment','<!-- {{cite:s1}} -->','SOURCE_TOKEN_IN_COMMENT'),
('comment_link','<!-- {{link:guide-two|Guide}} -->','SOURCE_TOKEN_IN_COMMENT'),
('nested_anchor','<a href="/a"><a href="/b">x</a></a>','NESTED_ANCHOR'),
('link_in_anchor','<a href="/a">{{link:guide-two|More}}</a>','SOURCE_TOKEN_IN_INTERACTIVE_CONTEXT'),
('cite_in_button','<button>{{cite:s1}}</button>','SOURCE_TOKEN_IN_INTERACTIVE_CONTEXT'),
('link_in_label','<label>{{link:guide-two|More}}</label>','SOURCE_TOKEN_IN_INTERACTIVE_CONTEXT'),
('bad_cite','<p>{{cite:nope</p>','MALFORMED_CITATION_TOKEN'),
('bad_link','<p>{{link:guide-two|More</p>','MALFORMED_INTERNAL_LINK_TOKEN'),
('bad_end','</missing>','MALFORMED_HTML_NESTING'),
('unclosed','<section>','UNCLOSED_HTML'),
('duplicate_id','<h2 id="act">Again</h2>','REPEATED_HTML_ID'),
('srcprotocol','<img src="//evil.example/x">','PROTOCOL_RELATIVE_FETCH'),
('posterprotocol','<video poster="//evil.example/x"></video>','PROTOCOL_RELATIVE_FETCH'),
]
for name,tail,expected in ATTACKS:
    def make(a,e):
        def test(self):
            m,t=fixture();m['_body']+=a
            out=g.inspect(m,t)
            self.assertIn(e,out['flags'],a)
            self.assertFalse(out['may_publish'])
        return test
    setattr(Base,'test_attack_'+name,make(tail,expected))

DRIFTS=[
 ('public',lambda m,t:m['status'].update(publish='published'),'CONTENT_PUBLICATION_STATE_DRIFT'),
 ('removed_status',lambda m,t:m.pop('status'),'CONTENT_PUBLICATION_STATE_DRIFT'),
 ('wrong_editorial',lambda m,t:m['status'].update(editorial='published'),'CONTENT_PUBLICATION_STATE_DRIFT'),
 ('no_safety',lambda m,t:m.pop('safety_review'),'SAFETY_REVIEW_STATE_DRIFT'),
 ('fake_safety',lambda m,t:m['safety_review'].update(state='safe'),'SAFETY_REVIEW_STATE_DRIFT'),
 ('ungated',lambda m,t:t.update(gate=False),'TAXONOMY_GATE_NOT_TRUE'),
 ('missing_gate',lambda m,t:t.pop('gate'),'TAXONOMY_GATE_NOT_TRUE'),
 ('slug',lambda m,t:m.update(slug='different'),'SOURCE_ARTICLE_TAXONOMY_DRIFT'),
 ('section',lambda m,t:m.update(section='food'),'SOURCE_ARTICLE_TAXONOMY_DRIFT'),
 ('track',lambda m,t:m.update(track='lost-ways'),'SOURCE_TRACK_TAXONOMY_DRIFT'),
]
for name,mutation,expected in DRIFTS:
    def make(fn,e):
        def test(self):
            m,t=fixture();fn(m,t)
            self.assertIn(e,g.inspect(m,t)['flags'])
        return test
    setattr(Base,'test_state_'+name,make(mutation,expected))

if __name__=='__main__':unittest.main()
