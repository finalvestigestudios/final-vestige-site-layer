"""R168 synthetic-only browser mutation suite: never use actual household data."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

FILE=Path(__file__).resolve().parents[1]/'tools'/'r168_family_print_persistence_gate.py'
SPEC=importlib.util.spec_from_file_location('r168',FILE)
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

FIXTURE='''<div>Printable Family Reunification Card — synthetic only</div>
<form id="rc" onsubmit="return false">
<input id="rc-hhName"><input id="rc-hhPhone"><input id="rc-outName"><input id="rc-outPhone">
<input id="rc-meet1"><input id="rc-meet2"><input id="rc-school"><input id="rc-schoolPlan">
<input id="rc-pickup"><input id="rc-careName"><input id="rc-carePhone">
<input id="rc-access"><input id="rc-reviewed"><input id="rc-minimal" type="checkbox">
<select id="rc-copies"><option value="1">1</option><option value="4">4</option></select>
<button type="button" id="rc-print" hidden>print</button>
<button type="button" id="rc-reset" hidden>clear</button>
</form><div id="rc-live" hidden><div id="rc-preview"></div><div id="rc-sheet"></div></div>
<style>@media print { #rc {display:none} #rc-sheet {display:block} }</style>
<script>
const form=document.getElementById('rc'), field=(key)=>document.getElementById('rc-'+key);
function render(){
 let minimal=field('minimal').checked, copies=Number(field('copies').value)||1;
 let text=['outName','school','careName','meet2'].filter(k=>!minimal||k==='outName').map(k=>field(k).value).join(' ');
 document.getElementById('rc-preview').textContent=text;
 let sheet=document.getElementById('rc-sheet');sheet.replaceChildren();
 for(let i=0;i<copies;i++){let item=document.createElement('div');item.className='pa-foldcard';item.textContent=text;sheet.appendChild(item);}}
form.addEventListener('input',render);form.addEventListener('change',render);
field('reset').addEventListener('click',()=>{form.reset();render();});
field('print').hidden=false;field('reset').hidden=false;
document.getElementById('rc-live').hidden=false;render();
</script>'''

class Structural(unittest.TestCase):
    def test_schema(self):self.assertEqual(mod.SCHEMA,'fv-preparedness-r168-print-persistence-v1')
    def test_widths(self):self.assertEqual(mod.WIDTHS,(360,390,768,1440))
    def test_fields_13(self):self.assertEqual(len(mod.FIELDS),13)
    def test_fields_unique(self):self.assertEqual(len(set(mod.FIELDS)),13)
    def test_sensitive_7(self):self.assertEqual(len(mod.SENSITIVE),7)
    def test_markers_4(self):self.assertEqual(len(mod.MARKERS),4)
    def test_private_3(self):self.assertEqual(len(mod.PRIVATE),3)
    def test_not_real_names(self):self.assertTrue(all('SYNTHETIC' in k for k in mod.ALL))
    def test_standalone_html(self):self.assertIn('<!doctype html>',mod.document(FIXTURE))
    def test_chained_to_r167(self):self.assertIn('r167.authentic(root)',FILE.read_text())
    def test_chained_to_r165(self):self.assertIn('r165.audit(root)',FILE.read_text())
    def test_upstream_src(self):self.assertIn('expanded_sha256',FILE.read_text())
    def test_not_wordpress_approved(self):self.assertIn('real_wordpress_verified\':False',FILE.read_text())
    def test_never_release(self):self.assertIn('return 2',FILE.read_text())
    def test_minimal_print_contract(self):self.assertIn('minimal printable document exposes private fields',FILE.read_text())
    def test_pseudo(self):self.assertIn("'::before','::after'",mod.PRINT_CHECK)
    def test_shadow(self):self.assertIn('shadowRoot',mod.PRINT_CHECK)
    def test_persistence(self):self.assertIn('history.state',mod.PERSISTENCE_CHECK)
    def test_window_name(self):self.assertIn('window.name',mod.PERSISTENCE_CHECK)
    def test_history_sensor(self):self.assertIn('history.pushState',mod.SENSOR)
    def test_open_sensor(self):self.assertIn('window.open',mod.SENSOR)
    def test_no_postdata(self):self.assertNotIn('post_data',FILE.read_text())
    def test_no_credentials(self):self.assertNotIn('Authorization:',FILE.read_text())
    def test_event_sort(self):self.assertEqual(mod.safe_event_types(['window.open','popup','window.open']),['popup','window.open'])
    def test_event_empty(self):self.assertEqual(mod.safe_event_types([]),[])
    def test_main_empty_checkout(self):
        with tempfile.TemporaryDirectory() as d:
            with patch('builtins.print'):
                self.assertEqual(mod.main(['--repo',d]),2)
    def test_main_report_hard_hold(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'result.json'
            with patch('builtins.print'):
                self.assertEqual(mod.main(['--repo',d,'--report',str(p)]),2)
            result=json.loads(p.read_text())
            self.assertEqual(result['state'],'INVALID_HARD_HOLD')
            self.assertFalse(result['publication_authorized'])
            self.assertNotIn('FV-SYNTHETIC',p.read_text())

class Browser(unittest.TestCase):
    def test_all_widths_baseline(self):
        r=mod.probe(FIXTURE)
        self.assertEqual([c['width'] for c in r['checks']],[360,390,768,1440])
        self.assertEqual(r['state'],'DRAFT_HARD_HOLD')
        self.assertFalse(r['publication_authorized'])
        self.assertFalse(r['actual_print_spool_verified'])
        self.assertFalse(r['independent_qd_pass'])
        self.assertNotIn(mod.MARKERS['school'],json.dumps(r))
    def test_print_css_regression(self):
        source=FIXTURE.replace('#rc {display:none}', '#rc {display:block}')
        with self.assertRaisesRegex(ValueError,'form exposed in print'):mod.probe(source,widths=[390])
    def test_private_print_external_div(self):
        source=FIXTURE.replace('form.addEventListener(\'input\',render);',
            "form.addEventListener('input',render);form.addEventListener('input',()=>{let x=document.getElementById('bleed');x.textContent=field('school').value;});")
        source=source.replace('<style>', '<div id="bleed"></div><style>')
        with self.assertRaisesRegex(ValueError,'minimal printable document exposes private fields'):mod.probe(source,widths=[390])
    def test_private_print_pseudo(self):
        source=FIXTURE.replace('</style>',
            "@media print {body::before{content:'FV-SYNTHETIC-SCHOOL-R168';}}</style>")
        with self.assertRaisesRegex(ValueError,'minimal printable document exposes private fields'):mod.probe(source,widths=[390])
    def test_private_attribute(self):
        source=FIXTURE.replace('form.addEventListener(\'input\',render);',
            "form.addEventListener('input',render);form.addEventListener('input',()=>{document.body.setAttribute('data-sneaky',field('school').value);});")
        with self.assertRaisesRegex(ValueError,'stores private fields in attributes'):mod.probe(source,widths=[390])
    def test_history_state(self):
        source=FIXTURE.replace('form.addEventListener(\'input\',render);',
            "form.addEventListener('input',render);form.addEventListener('input',()=>{try{history.replaceState({p:field('school').value},'')}catch(e){}});")
        with self.assertRaisesRegex(ValueError,'blocked browser persistence/export API attempted'):mod.probe(source,widths=[390])
    def test_window_name(self):
        source=FIXTURE.replace('form.addEventListener(\'input\',render);',
            "form.addEventListener('input',render);form.addEventListener('input',()=>{window.name=field('school').value;});")
        with self.assertRaisesRegex(ValueError,'navigation/browser persistence'):mod.probe(source,widths=[390])
    def test_popup(self):
        source=FIXTURE.replace('form.addEventListener(\'input\',render);',
            "form.addEventListener('input',render);form.addEventListener('input',()=>{try{window.open('about:blank')}catch(e){}});")
        with self.assertRaisesRegex(ValueError,'blocked browser persistence/export API attempted'):mod.probe(source,widths=[390])
    def test_css_image_request(self):
        source=FIXTURE.replace('form.addEventListener(\'input\',render);',
            "form.addEventListener('input',render);form.addEventListener('input',()=>{let img=document.createElement('img');img.src='https://example.org/resource';document.body.append(img);});")
        with self.assertRaisesRegex(ValueError,'browser side effect during input'):mod.probe(source,widths=[390])
    def test_data_after_clear(self):
        source=FIXTURE.replace('form.reset();render();','form.reset();render();document.getElementById(\'leak\').textContent=\'FV-SYNTHETIC-SCHOOL-R168\';')
        source=source.replace('<style>','<div id="leak"></div><style>')
        with self.assertRaisesRegex(ValueError,'clear left synthetic contact data'):mod.probe(source,widths=[390])
    def test_reset_must_clear_values(self):
        source=FIXTURE.replace('form.reset();render();','render();')
        with self.assertRaisesRegex(ValueError,'clear left data'):mod.probe(source,widths=[390])
    def test_minimal_copy_count(self):
        source=FIXTURE.replace('for(let i=0;i<copies;i++)','for(let i=0;i<1;i++)')
        with self.assertRaisesRegex(ValueError,'four copies not rendered'):mod.probe(source,widths=[390])
    def test_lost_sensor(self):
        source=FIXTURE.replace("const form=document.getElementById('rc')", "delete window.__fv_r168_events; const form=document.getElementById('rc')")
        # Sensor non-configurable; tampering attempt not guaranteed to delete it, but cannot grant release.
        r=mod.probe(source,widths=[390]);self.assertFalse(r['publication_authorized'])

# Independent per-case fail-closed validation, not aliases into a single broad test.
BAD_HTML=[None,False,1,1.5,[],{},b'bytes','', 'a', ' '*500,
          '<html></html>','<form id="other"></form>'*20,
          '<p>'+'z'*250+'</p>', '<form id="rc"></form>']
for i,v in enumerate(BAD_HTML):
    def maker(x):
        def test(self):
            with self.assertRaises(ValueError):mod.document(x)
        return test
    setattr(Structural,'test_bad_html_%02d'%i,maker(v))
BAD_EVENTS=[None,123,{},'a:b','https://fake.example','f?e','f=e','f/e','a b',"a'","a\"",'<p>','\n','x\ty',
            'x'*51, 'x,y','x;y','a@b','a+b','a#b','{foo}','[x]','x\\x',True]
for i,v in enumerate(BAD_EVENTS):
    def maker(x):
        def test(self):
            with self.assertRaises(ValueError):mod.safe_event_types([x])
        return test
    setattr(Structural,'test_bad_event_%02d'%i,maker(v))
BAD_WIDTHS=[[],(),None,390,0,True,[True],[100],[2300],[360,360],[1,390],[-1,390],['390'],[None],{},[390,390,768]]
for i,v in enumerate(BAD_WIDTHS):
    def maker(x):
        def test(self):
            with self.assertRaises((ValueError,TypeError)):mod.probe(FIXTURE,widths=x)
        return test
    setattr(Structural,'test_bad_width_%02d'%i,maker(v))

if __name__=='__main__':unittest.main()
