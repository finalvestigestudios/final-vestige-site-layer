"""R470 deterministic negative mutation battery; synthetic success != human safety."""
import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import unittest

SRC = pathlib.Path(__file__).resolve().parents[1] / 'tools/r470_css_citation_exposure.py'
spec = importlib.util.spec_from_file_location('r470_css', SRC)
gate = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = gate
spec.loader.exec_module(gate)

BASE = '''.pa-body sup.pa-cite { font-size: .72em; line-height: 1; }
.pa-body sup.pa-cite a { text-decoration: none; }
.pa-sources li { margin: 0 0 1em; font-size: 15.5px; }
.pa-sources .pa-src-use { display: block; }
@media print { .pa-sources li { break-inside: avoid; } .pa-printbar { display:none; } }
@container (min-width: 700px) { .pa-shell { display:grid; } }
'''

class Baseline(unittest.TestCase):
    def test_static_contract(self):
        x=gate.audit_css(BASE)
        self.assertEqual(x['release_state'], 'DRAFT_HARD_HOLD')
        self.assertFalse(x['qualified_qd_pass'])
        self.assertFalse(x['browser_verified'])
        self.assertFalse(x['wordpress_theme_verified'])
        self.assertFalse(x['may_publish'])
        self.assertGreaterEqual(x['protected_rules'],4)
    def test_determinism(self): self.assertEqual(gate.audit_css(BASE),gate.audit_css(BASE))
    def test_missing_native_fail_closed(self):
        with tempfile.TemporaryDirectory() as t:
            run=subprocess.run([sys.executable,'-I',str(SRC),'--root',t],capture_output=True,text=True)
            self.assertEqual(run.returncode,2)
            self.assertIn('FAILURE_HARD_HOLD',run.stdout)
    def test_git_blob_immutability(self):
        raw=b'hello\n';self.assertEqual(gate.gitblob(raw),'ce013625030ba8dba906f756967f9e9ca394464a')
    def test_extract_comments(self):
        x=gate.strip_comments('/* hide */.pa-cite{content:"/* text */";}')
        self.assertIn('"/* text */"',x)
    def test_split_parens(self):
        self.assertEqual(gate.split_top(':is(.pa-cite,.pa-review), .pa-sources',','),[':is(.pa-cite,.pa-review)','.pa-sources'])
    def test_parent_selectors(self):
        self.assertTrue(gate.important_selector('.pa-body sup.pa-cite a'))
        self.assertTrue(gate.important_selector('.pa-sources .pa-src-use'))
        self.assertFalse(gate.important_selector('.pa-card[hidden]'))
    def test_no_native_primitives(self):
        self.assertFalse(gate.audit_css(BASE)['computed_css_verified'])
    def test_empty_css(self):
        with self.assertRaises(gate.CSSHold): gate.audit_css('')
    def test_no_protected_rules(self):
        with self.assertRaises(gate.CSSHold): gate.audit_css('.pa-card{display:none;}')
    def test_missing_brace(self):
        with self.assertRaises(gate.CSSHold): gate.audit_css(BASE+' .pa-cite{display:block')
    def test_at_import(self):
        with self.assertRaises(gate.CSSHold): gate.audit_css('@import url("bad.css");'+BASE)
    def test_mutated_pinned_css(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t); (root/'assets').mkdir(); (root/'assets/preparedness.css').write_text(BASE)
            with self.assertRaises(gate.CSSHold): gate.native(root)

class HiddenMutations(unittest.TestCase):
    pass

ATTACKS = {
 'display_none': ('display','none'), 'display_none_important': ('display','none!important'),
 'visibility_hidden':('visibility','hidden'), 'visibility_collapse':('visibility','collapse'),
 'content_visibility_hidden':('content-visibility','hidden'),
 'opacity_zero':('opacity','0'), 'opacity_percent':('opacity','0%'),
 'opacity_decimal':('opacity','0.0'), 'color_transparent':('color','transparent'),
 'font_zero':('font-size','0px'), 'font_zero_em':('font-size','0em'),
 'line_zero':('line-height','0'), 'height_zero':('height','0'),
 'max_height_zero':('max-height','0px'), 'width_zero':('width','0%'),
 'max_width_zero':('max-width','0rem'),
 'clip_rect':('clip','rect(0px,0px,0px,0px)'),
 'clip_path':('clip-path','inset(100%)'),
 'filter_opacity':('filter','opacity(0)'),
 'pointer_none':('pointer-events','none'), 'user_none':('user-select','none'),
 'transform_scale':('transform','scale(0)'), 'scale_zero':('scale','0'),
 'indent':('text-indent','-10000px'), 'left_offscreen':('left','-9999px'),
 'right_offscreen':('right','-2000px'), 'top_offscreen':('top','-10000px'),
 'inset_offscreen':('inset','-10000px'), 'z_index':('z-index','-9999'),
 'content_fake':('content','"[1]"'),
 'list_style':('list-style','none'), 'list_style_type':('list-style-type','none'),
 'animation':('animation','hide 2s'), 'animation_name':('animation-name','hide'),
 'mask':('mask','url(mask.svg)'), 'mask_image':('mask-image','linear-gradient(transparent,transparent)'),
 'var_display':('display','var(--hide)'), 'calc_opacity':('opacity','calc(1 - 1)'),
 'env_width':('width','env(safe-area-inset-left)'),
}
SELECTORS = ['.pa-cite', '.pa-body sup.pa-cite a', '.pa-sources li', '.pa-src-use',
             '.pa-review', '.pa-shell', '.pa-body', '.pa-sources', '.pa:not(.other)']

def make_attack(selector, property_name, value, env=''):
    css = f'{selector} {{{property_name}:{value};}}'
    if env: css = env+'{'+css+'}'
    return BASE+'\n'+css

def mutation_case(selector, prop, value, env=''):
    def test(self):
        with self.assertRaises(gate.CSSHold):
            gate.audit_css(make_attack(selector,prop,value,env))
    return test

for name, pair in ATTACKS.items():
    setattr(HiddenMutations,'test_hidden_'+name,mutation_case('.pa-sources',*pair))
for i, selector in enumerate(SELECTORS):
    setattr(HiddenMutations,'test_critical_selector_'+str(i),mutation_case(selector,'display','none'))
for i, env in enumerate(['@media print','@media (max-width: 420px)',
                         '@container (min-width: 700px)','@supports (display:grid)',
                         '@layer preparedness','@media (prefers-color-scheme:dark)']):
    setattr(HiddenMutations,'test_conditional_'+str(i),mutation_case('.pa-cite','opacity','0',env))

class AttackGrammar(unittest.TestCase):
    pass
GRAMMAR = {
    'unbalanced_curly':BASE+'}',
    'unclosed_quote':BASE+'.pa-cite{color:"red}',
    'unclosed_comment':BASE+'/* stop',
    'unexpected_keyframe':BASE+'@keyframes blink{from{opacity:1}to{opacity:0}}',
    'unexpected_fontface':BASE+'@font-face{font-family:X;src:url(x)}',
    'empty_css_rule':'.pa-cite{}',
    'orphan_css_decl':BASE+'display:none;',
    'dup_critical_prop':BASE+'.pa-cite{display:block;display:flex;}',
    'missing_colon':BASE+'.pa-cite{display none;}',
    'blank_value':BASE+'.pa-cite{display:;}',
    'invalid_selector_paren':BASE+'.pa-cite:not(.x{display:none}',
    'invalid_selector_bracket':BASE+'.pa-cite[data-evil{display:none}',
    'inline_script':BASE+'<script>alert(1)</script>',
    'empty_rule_body':'.pa-cite{}',
    'unverified_css_at_rule':BASE+'@property --x {syntax:"*";inherits:false;initial-value:0}',
}
def make_grammar_bad(raw):
    def test(self):
        with self.assertRaises(gate.CSSHold): gate.audit_css(raw)
    return test
for name,css in GRAMMAR.items():
    setattr(AttackGrammar,'test_bad_'+name,make_grammar_bad(css))

class AllowedChanges(unittest.TestCase):
    pass
ALLOWED = {
 'display_flex':'.pa-shell{display:flex;}',
 'display_block':'.pa-sources li{display:block;}',
 'print_ornament':'@media print{.pa-printbar{display:none;}}',
 'source_wrapping':'.pa-sources li{overflow-wrap:anywhere;}',
 'source_link':'.pa-cite a{text-decoration:underline;}',
 'color_opaque':'.pa-review{color:#111111;}',
 'opacity_one':'.pa-cite{opacity:1;}',
 'font_size':'.pa-body sup.pa-cite{font-size:.72em;}',
 'visible':'.pa-sources{visibility:visible;}',
 'normal_animation':'.pa-review{animation:none;}',
 'nested_container':'@container (min-width: 700px){.pa-sources ol{padding-left:1.2em;}}',
 'css_quoted_comment':'.pa-card{content:"/* not comment */";}',
 'noncritical_card':'.pa-card[hidden]{display:none;}',
}
def make_allowed(raw):
    def test(self): self.assertGreater(gate.audit_css(BASE+'\n'+raw)['protected_rules'],0)
    return test
for name, css in ALLOWED.items():
    setattr(AllowedChanges,'test_allowed_'+name,make_allowed(css))

if __name__=='__main__': unittest.main()
