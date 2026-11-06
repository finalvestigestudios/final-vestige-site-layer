"""R177 negative/mutation tests: synthetic fixtures only, never assert safety approval."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
spec = importlib.util.spec_from_file_location('r177_safety_wording_gate', PROJECT / 'tools/r177_safety_wording_gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

HOUSE = '''<article><h2>Practice</h2><ul><li><strong>The simulated-outage evening.</strong> Pretend the power is out for a few hours: switch off nonessential lights, the television and other devices. Leave on everything that keeps people safe, including the refrigerator, smoke and carbon monoxide alarms, and all medical or safety-critical equipment. Do not switch off the main breaker as a drill.</li></ul></article>'''
KIT = '''<article><div class="pa-alert pa-alert--stop"><p class="pa-alert-title">Medicines that need refrigeration: ask your prescriber or pharmacist</p><p>This page cannot tell you what to do with any particular medicine. Whether a medicine can stay warm depends on the medicine, the product label and your health. Ask your prescriber or pharmacist before an outage. If you are already in an outage, call your doctor or pharmacist.</p></div><div class="pa-alert"><p>Two FEMA documents, two wordings</p><p>FEMA's 2020 guide differs from the newer December 2023 fact sheet: call your doctor or pharmacist. Whether this passage needs rewording is a question for the human safety reviewer. This page gives no instruction of its own about any medicine.</p></div></article>'''

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory(prefix='fv-r177-synthetic-')
        self.addCleanup(self.t.cleanup)
        self.root = Path(self.t.name)
        d = self.root / 'preparedness/review/r177'
        d.mkdir(parents=True)
        shutil.copyfile(PROJECT/'review/r177/safety_contract.json', d/'safety_contract.json')
        self.sources = self.root/'preparedness/content/articles'
        self.sources.mkdir(parents=True)
        self.exports = self.root/'preparedness/build/wp'
        self.exports.mkdir(parents=True)
        for slug, text in [('household-emergency-plan', HOUSE), ('three-day-kit', KIT)]:
            (self.sources/(slug+'.body.html')).write_text(text,encoding='utf-8')
            (self.exports/(slug+'.html')).write_text(text,encoding='utf-8')

    def read_manifest(self):
        return json.loads((self.root / gate.MANIFEST).read_text())

    def write_manifest(self, obj):
        (self.root / gate.MANIFEST).write_text(json.dumps(obj))

    def mutate(self,slug,old,new,export=False):
        p = ((self.exports/(slug+'.html')) if export else
             (self.sources/(slug+'.body.html')))
        content=p.read_text(encoding='utf-8')
        self.assertIn(old,content)
        p.write_text(content.replace(old,new),encoding='utf-8')

    def test_baseline_source_hold(self):
        x=gate.inspect(self.root)
        self.assertEqual(x['state'],gate.HOLD)
        self.assertEqual(x['errors_count'],0)
        self.assertEqual(len(x['files']),2)
        self.assertFalse(x['publication_authorized'])

    def test_baseline_source_and_export_hold(self):
        x=gate.inspect(self.root,check_export=True)
        self.assertEqual(x['state'],gate.HOLD)
        self.assertEqual(len(x['files']),4)
        self.assertFalse(x['independent_qd_pass'])

    def test_gate_cli_never_zero(self):
        out=subprocess.run([sys.executable,str(PROJECT/'tools/r177_safety_wording_gate.py'),
                            '--repo',str(self.root),'--check-export'],capture_output=True,text=True)
        self.assertEqual(out.returncode,2)
        self.assertEqual(json.loads(out.stdout)['state'],gate.HOLD)

    def test_html_comment_cannot_satisfy_anchor(self):
        self.mutate('household-emergency-plan', '<li>', '<!--<li>')
        self.mutate('household-emergency-plan', '</li>', '</li>-->')
        self.assertEqual(gate.inspect(self.root)['state'],gate.INVALID)

    def test_hidden_fragment_cannot_satisfy_anchor(self):
        self.mutate('household-emergency-plan', '<li>', '<li hidden>')
        self.assertEqual(gate.inspect(self.root)['state'],gate.INVALID)

    def test_aria_hidden_cannot_satisfy_anchor(self):
        self.mutate('household-emergency-plan', '<li>', '<li aria-hidden="true">')
        self.assertEqual(gate.inspect(self.root)['state'],gate.INVALID)

    def test_css_inline_hidden_cannot_satisfy_anchor(self):
        self.mutate('household-emergency-plan', '<li>', '<li style="display:none">')
        self.assertEqual(gate.inspect(self.root)['state'],gate.INVALID)

    def test_outage_unsafe_instruction_rejected_even_with_required_good_text(self):
        self.mutate('household-emergency-plan','</article>',
                    '<p>Switch off the main power for an evening</p></article>')
        self.assertEqual(gate.inspect(self.root)['state'],gate.INVALID)

    def test_refrigerated_medicine_disposal_shortcut_rejected(self):
        self.mutate('three-day-kit','</article>',
                    '<p>Discard all refrigerated medicines immediately</p></article>')
        self.assertEqual(gate.inspect(self.root)['state'],gate.INVALID)

    def test_export_missing_fails_only_export_check(self):
        (self.exports/'three-day-kit.html').unlink()
        self.assertEqual(gate.inspect(self.root)['state'],gate.HOLD)
        self.assertEqual(gate.inspect(self.root,check_export=True)['state'],gate.INVALID)

    def test_source_missing_fails(self):
        (self.sources/'three-day-kit.body.html').unlink()
        self.assertEqual(gate.inspect(self.root)['state'],gate.INVALID)

    def test_manifest_scope_shortening_fails(self):
        m=self.read_manifest();m['articles'].pop();self.write_manifest(m)
        self.assertEqual(gate.inspect(self.root)['state'],gate.INVALID)

    def test_duplicate_scope_fails(self):
        m=self.read_manifest();m['articles'][1]['slug']='household-emergency-plan';self.write_manifest(m)
        self.assertEqual(gate.inspect(self.root)['state'],gate.INVALID)

    def test_manifest_schema_fails(self):
        m=self.read_manifest();m['schema']='fake';self.write_manifest(m)
        self.assertEqual(gate.inspect(self.root)['state'],gate.INVALID)

    def test_export_passages_cannot_be_only_in_html_comments(self):
        self.mutate('three-day-kit','<article>','<article><!--',export=True)
        self.mutate('three-day-kit','</article>','--></article>',export=True)
        self.assertEqual(gate.inspect(self.root,check_export=True)['state'],gate.INVALID)

    def test_original_source_export_can_differ_in_markup(self):
        self.mutate('household-emergency-plan','<strong>','<span class="safe">',export=True)
        self.mutate('household-emergency-plan','</strong>','</span>',export=True)
        self.assertEqual(gate.inspect(self.root,check_export=True)['state'],gate.HOLD)

    def test_does_not_mutate_source_files(self):
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        gate.inspect(self.root,check_export=True)
        self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()})


def add_cases():
    m=json.loads((PROJECT/'review/r177/safety_contract.json').read_text())
    # Every required fragment, both stages, must be an independent blocking condition.
    for rule in m['articles']:
        slug=rule['slug']
        for section in rule['sections']:
            for i,fragment in enumerate(section['required']):
                for export in (False,True):
                    name=f'test_mutation_{slug.replace("-","_")}_{section["id"]}_{i}_{"export" if export else "source"}'
                    def check(self,slug=slug,fragment=fragment,export=export):
                        self.mutate(slug,fragment,'TEXT WITHHELD FROM READER',export=export)
                        report=gate.inspect(self.root,check_export=export)
                        self.assertEqual(report['state'],gate.INVALID)
                        self.assertGreater(report['errors_count'],0)
                    setattr(ContractTests,name,check)
    # Explicit false release claims must be rejected even if article passages are intact.
    for flag in ('publication_authorized','independent_qd_pass','qualified_source_review',
                 'medical_safety_approved','food_safety_approved'):
        def check(self, flag=flag):
            m=self.read_manifest();m[flag]=True;self.write_manifest(m)
            self.assertEqual(gate.inspect(self.root)['state'],gate.INVALID)
        setattr(ContractTests,'test_no_false_'+flag,check)
    # Repeated anchor is not acceptable; a duplicated warning can mask a missing one.
    for slug, text in [('household-emergency-plan',HOUSE),('three-day-kit',KIT)]:
        def check(self,slug=slug,text=text):
            path=self.sources/(slug+'.body.html')
            path.write_text(text+text,encoding='utf-8')
            self.assertEqual(gate.inspect(self.root)['state'],gate.INVALID)
        setattr(ContractTests,'test_duplicate_passage_'+slug.replace('-','_'),check)

add_cases()

if __name__=='__main__':
    unittest.main(verbosity=2)
