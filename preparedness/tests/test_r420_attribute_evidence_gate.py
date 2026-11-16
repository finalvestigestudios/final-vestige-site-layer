"""R420 synthetic-only attribute / presentation custody tests; never publication QA."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tests')]
from test_r418_uncited_claim_custody_gate import fixture
import r419_unbound_evidence_gate as previous
import r420_attribute_evidence_gate as gate


def mutation(fragment, only=None):
    d,m,e,c=fixture()
    src=e['guide-0'][0]
    dst=src.replace('</article>',fragment+'</article>')
    e['guide-0']=(dst,dst) if only is None else ((dst,src) if only=='wordpress' else (src,dst))
    return d,m,e,c

class Baselines(unittest.TestCase):
    def test_35_article_fixture_baseline_passes_structurally(self):
        d,m,e,c=fixture()
        r=gate.check(d,m,e,c,test_only=True)
        self.assertTrue(r['integrity_ok'],r['errors'])
        self.assertEqual(r['draft_checks'],70)
        self.assertFalse(r['eligible'])
        self.assertFalse(r['publication_approved'])
        self.assertFalse(r['qualified_safety_approved'])
        self.assertFalse(r['merchant_offer_verified'])
        self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')

    def test_reproduced_previous_tooltip_text_bypass(self):
        d,m,e,c=mutation('<div title="Boiled seawater is safe to drink"></div>')
        self.assertTrue(previous.check(d,m,e,c,test_only=True)['integrity_ok'])
        r=gate.check(d,m,e,c,test_only=True)
        self.assertFalse(r['integrity_ok'])
        self.assertTrue(any('R420 original accessible' in er for er in r['errors']))

    def test_reproduced_previous_css_generated_content_bypass(self):
        d,m,e,c=mutation('<style>.archive-note::before{content:"Homemade jerky is guaranteed safe"}</style>')
        self.assertFalse(previous.check(d,m,e,c,test_only=True)['integrity_ok'])  # older active-CSS rule already held
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])

    def test_sole_wordpress_side_can_fail(self):
        d,m,e,c=mutation('<img alt="Unsafe advice">','wordpress')
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])

    def test_sole_private_preview_can_fail(self):
        d,m,e,c=mutation('<img alt="Unsafe advice">','preview')
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])

    def test_safe_unmodified_markup_wrapper(self):
        d,m,e,c=fixture()
        h=e['guide-0'][0].replace('<article>','<article><div class="archive-layout">').replace('</article>','</div></article>')
        e['guide-0']=(h,h)
        self.assertTrue(gate.check(d,m,e,c,test_only=True)['integrity_ok'])

    def test_altered_original_alt_rejected(self):
        s='<article><img alt="Contact the designated relative"></article>'
        r=s.replace('designated','unverified')
        got=gate.attribute_fidelity(s,r)
        self.assertEqual(got['missing_attributes'],1)
        self.assertEqual(got['new_or_changed_attributes'],1)

    def test_original_alt_preserved(self):
        s='<article><img alt="Contact the designated relative"></article>'
        self.assertEqual(gate.attribute_fidelity(s,s)['missing_attributes'],0)
        self.assertEqual(gate.attribute_fidelity(s,s)['new_or_changed_attributes'],0)

    def test_original_copies_counted(self):
        s='<article><img alt="Out-of-area contact"></article>'
        r=s.replace('</article>','<img alt="Out-of-area contact"></article>')
        self.assertEqual(gate.attribute_fidelity(s,r)['new_or_changed_attributes'],1)

    def test_attribute_decoded_entities_equal(self):
        s='<article><img alt="Emergency contact &amp; school"></article>'
        r='<article><img alt="Emergency contact &#38; school"></article>'
        self.assertEqual(gate.attribute_fidelity(s,r)['new_or_changed_attributes'],0)

    def test_whitespace_and_case_difference_normalized(self):
        s='<article><img alt="  EMERGENCY    Contact "></article>'
        r='<article><img alt="emergency contact"></article>'
        self.assertEqual(gate.attribute_fidelity(s,r)['new_or_changed_attributes'],0)

    def test_blank_decorative_alt_allowed(self):
        self.assertEqual(gate.attribute_fidelity('<article></article>', '<article><img alt=""></article>')['new_or_changed_attributes'],0)

    def test_no_private_text_in_result_json(self):
        d,m,e,c=mutation('<img alt="Private emergency home address 123 Example Street">')
        r=gate.check(d,m,e,c,test_only=True)
        self.assertNotIn('Example Street',json.dumps(r))

    def test_no_input_mutation(self):
        d,m,e,c=mutation('<img title="New instruction">')
        before=copy.deepcopy((d,m,e,c))
        gate.check(d,m,e,c,test_only=True)
        self.assertEqual((d,m,e,c),before)

    def test_normal_mode_without_real_originals_not_green(self):
        d,m,e,c=fixture()
        self.assertFalse(gate.check(d,m,e,c)['integrity_ok'])

    def test_forged_approval_flag_not_publishable(self):
        d,m,e,c=fixture();m['qualified_safety_approved']=True
        r=gate.check(d,m,e,c,test_only=True)
        self.assertFalse(r['publication_approved'])
        self.assertFalse(r['integrity_ok'])

    def test_original_blob_mutation_detected(self):
        d,m,e,c=fixture();key=next(iter(c));c[key]+=b'altered'
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])

    def test_35_article_counts_and_forks_unchanged(self):
        d,m,e,c=fixture()
        self.assertEqual(len(d['original_articles']),35)
        self.assertEqual(len(d['original_fork_disputes']),9)
        self.assertEqual(len(d['source_evidence_disputes']),5)

    def test_invalid_utf8_rejected(self):
        with self.assertRaises(UnicodeDecodeError):gate.inspect(b'\xff')

    def test_unclosed_html_rejected(self):
        with self.assertRaises(ValueError):gate.inspect('<article><img alt="x">')

    def test_duplicate_attributes_rejected(self):
        with self.assertRaises(ValueError):gate.inspect('<article><img ALT="x" alt="y"></article>')

    def test_oversize_attribute_rejected(self):
        with self.assertRaises(ValueError):gate.inspect('<article><img alt="'+('x'*9000)+'"></article>')

    def test_markdown_original_no_rendered_attribute_claim(self):
        self.assertEqual(gate.inspect('# Family contact\nA guide.',candidate=True).labels,[])

    def test_cli_missing_authentic_data_fails_closed(self):
        p=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r420_attribute_evidence_gate.py'),
            '/missing/a.json','/missing/m.json','/missing/export','/missing/originals'],
            capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertFalse(json.loads(p.stdout)['integrity_ok'])

    def test_valid_original_35_fixture_has_no_extraneous_details(self):
        d,m,e,c=fixture();r=gate.check(d,m,e,c,test_only=True)
        self.assertTrue(all(x['original_attributes']==0 for x in r['details']))


TEXT_SURFACES = ['alt','title','aria-label','aria-description','aria-valuetext',
                 'placeholder','data-tooltip','data-title','data-content',
                 'data-help','data-instruction']
STYLE_PAYLOADS = ['content:"Water is safe"','display:none','visibility:hidden',
    'opacity:0','font-size:0px','clip-path:inset(100%)',
    'text-indent:-9999px','color:transparent','-webkit-text-fill-color:transparent',
    '@import url(https://example.invalid/a.css)']
EMBED_PAYLOADS = ['<iframe src="https://example.invalid/claim"></iframe>',
    '<object data="https://example.invalid/x"></object>',
    '<embed src="https://example.invalid/x">',
    '<applet></applet>',
    '<meta http-equiv="refresh" content="0;url=https://example.invalid">',
    '<div srcdoc="<p>Fake instructions</p>"></div>',
    '<img src="demo" onerror="alert(1)">']

class NewAttributeClaims(unittest.TestCase):
    pass

for i,name in enumerate(TEXT_SURFACES):
    def make(name):
        def test(self):
            d,m,e,c=mutation('<div '+name+'="Emergency claim absent from original"></div>')
            self.assertTrue(previous.check(d,m,e,c,test_only=True)['integrity_ok'])
            r=gate.check(d,m,e,c,test_only=True)
            self.assertFalse(r['integrity_ok'],(name,r['errors']))
        return test
    setattr(NewAttributeClaims,'test_attribute_surface_'+str(i)+'_'+name.replace('-','_'),make(name))

class CSSInvisibleOrGenerated(unittest.TestCase):
    pass

for i,payload in enumerate(STYLE_PAYLOADS):
    def make(payload):
        def test(self):
            data='<article><div style="'+payload.replace('"','&quot;')+'">Example</div></article>'
            risk=gate.inspect(data).risks
            self.assertTrue(risk,payload)
            if payload.startswith('content:') or payload.startswith('@import'):
                css='<article><style>.tip::before{'+payload+'}</style></article>'
                self.assertTrue(gate.inspect(css).risks)
        return test
    setattr(CSSInvisibleOrGenerated,'test_risky_css_'+str(i),make(payload))

class UnsafeEmbeddedContent(unittest.TestCase):
    pass

for i,payload in enumerate(EMBED_PAYLOADS):
    def make(payload):
        def test(self):
            r=gate.inspect('<article>'+payload+'</article>')
            self.assertGreater(len(r.risks),0)
        return test
    setattr(UnsafeEmbeddedContent,'test_embed_or_execution_'+str(i),make(payload))

class InputAndValueControls(unittest.TestCase):
    def test_submit_button_value_is_accessible_copy(self):
        s='<article><input type="submit" value="Buy today"></article>'
        self.assertEqual(gate.attribute_fidelity('<article></article>',s)['new_or_changed_attributes'],1)

    def test_hidden_input_tracking_id_not_presented_as_copy(self):
        s='<article><input type="hidden" value="123abc"></article>'
        self.assertEqual(gate.attribute_fidelity('<article></article>',s)['new_or_changed_attributes'],0)

    def test_password_input_value_not_held_as_article_claim(self):
        s='<article><input type="password" value="dont-copy"></article>'
        self.assertEqual(gate.attribute_fidelity('<article></article>',s)['new_or_changed_attributes'],0)

    def test_option_value_requires_review(self):
        s='<article><select><option value="Unsafe-new-assurance">Old</option></select></article>'
        self.assertEqual(gate.attribute_fidelity('<article></article>',s)['new_or_changed_attributes'],1)

    def test_button_value_requires_review(self):
        s='<article><button value="Approved-by-FV">Open</button></article>'
        self.assertEqual(gate.attribute_fidelity('<article></article>',s)['new_or_changed_attributes'],1)

if __name__=='__main__':unittest.main()
