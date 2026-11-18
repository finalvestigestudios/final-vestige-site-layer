"""Adversarial offline tests for R466. No production data or network access."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r466_independent_qa_absorption as gate

HOUSE = ("Do not switch off the main breaker as a drill. Leave on the refrigerator and freezer, "
         "smoke and carbon monoxide alarms, and all medical or safety-critical equipment.")
MED = ("Do not stop, throw away or ration a medicine you depend on. "
       "Ask your prescriber or pharmacist about each refrigerated medicine, "
       "what to do if you are already in an outage, and the replacement plan.")
TEST = '''
class PreparednessFixtureTests:
    def test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source(self):
        import tempfile, shutil
        with tempfile.TemporaryDirectory() as td:
            sandbox = Path(td) / "preparedness"
            shutil.copytree(ROOT, sandbox)
            register_path = sandbox / "sources" / "register.json"
            register_path.write_text("synthetic")
            lib = build.Library(root=sandbox)
    def test_register_fragments_cannot_duplicate_ids(self):
        import tempfile, shutil
        with tempfile.TemporaryDirectory() as td:
            sandbox = Path(td) / "preparedness"
            shutil.copytree(ROOT, sandbox)
            fragment = sandbox / "sources" / "fragments" / "_dup_test.json"
            fragment.write_text("synthetic")
            lib = build.Library(root=sandbox)
'''

def fixture():
    slate = [{'n': i+1, 'slug': 'item-'+str(i+1), 'gate': True, 'status': 'drafted-pending-safety-review'} for i in range(35)]
    for i, slug in enumerate(gate.START_HERE):
        slate[i]['slug'] = slug
    return {
        'content/articles/household-emergency-plan.body.html': HOUSE.encode(),
        'content/articles/three-day-kit.body.html': MED.encode(),
        'sources/fragments/start.json': json.dumps({'sources': [{'id':'start-redcross-older-adults','publisher':'American Red Cross','kind':'nonprofit'}]}).encode(),
        'taxonomy.json': json.dumps({'slate': slate}).encode(),
        'tests/test_preparedness.py': TEST.encode(),
    }

class BaseContract(unittest.TestCase):
    def test_synthetic_baseline(self):
        self.assertEqual([], gate.audit_payloads(fixture(), verify_pins=False))
    def test_expected_five_blobs(self):
        self.assertEqual(5, len(gate.PINS))
    def test_blob_algorithm(self):
        self.assertEqual('b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0', gate.git_blob(b'hello'))
    def test_false_blob_pin_rejected(self):
        self.assertTrue(any('blob mismatch' in e for e in gate.audit_payloads(fixture())))
    def test_no_runtime_execution(self):
        code = Path(gate.__file__).read_text()
        self.assertNotIn('subprocess.run(', code)
        self.assertNotIn('requests.get(', code)
    def test_release_always_held(self):
        result = gate.audit_native(Path('/nonexistent/r466'))
        self.assertEqual('HARD_HOLD', result['status'])
        self.assertFalse(result['release_approval'])
        self.assertFalse(result['human_safety_approved'])
    def test_missing_all_inputs(self):
        self.assertEqual(5, len(gate.audit_payloads({})))
    def test_source_duplicate_key_rejected(self):
        f = fixture()
        f['sources/fragments/start.json'] = b'{"sources":[],"sources":[]}'
        self.assertTrue(any('duplicate JSON key' in e for e in gate.audit_payloads(f,False)))
    def test_taxonomy_duplicate_key_rejected(self):
        f = fixture()
        f['taxonomy.json'] = b'{"slate":[],"slate":[]}'
        self.assertTrue(any('duplicate JSON key' in e for e in gate.audit_payloads(f,False)))
    def test_fixture_ast_injection_rejected(self):
        f = fixture()
        f['tests/test_preparedness.py'] = (TEST + '\ndef broken(:\n').encode()
        self.assertTrue(any('syntax error' in e for e in gate.audit_payloads(f,False)))


def mutate(base: dict[str, bytes], family: int, variant: int):
    f = copy.deepcopy(base)
    house_key = 'content/articles/household-emergency-plan.body.html'
    med_key = 'content/articles/three-day-kit.body.html'
    src_key = 'sources/fragments/start.json'
    tax_key = 'taxonomy.json'
    test_key = 'tests/test_preparedness.py'
    if family == 0:
        needles = ['do not switch off the main breaker', 'refrigerator and freezer',
                   'smoke and carbon monoxide alarms', 'medical or safety-critical equipment']
        needle = needles[variant % 4]
        orig = f[house_key].decode()
        pos = orig.lower().index(needle)
        f[house_key] = (orig[:pos] + '[REMOVED]' + orig[pos+len(needle):]).encode()
    elif family == 1:
        texts = ['Switch off the main power', 'switch off the main breaker for',
                 'Turn off the main breaker to', 'SWITCH OFF THE MAIN POWER']
        f[house_key] += (' ' + texts[variant % 4] + ' a realistic test.').encode()
    elif family == 2:
        needles = ['do not stop, throw away or ration', 'prescriber or pharmacist',
                   'refrigerated medicine', 'replacement', 'if you are already in an outage']
        needle = needles[variant % 5]
        orig = f[med_key].decode()
        pos = orig.lower().index(needle)
        f[med_key] = (orig[:pos] + '[REMOVED]' + orig[pos+len(needle):]).encode()
    elif family == 3:
        bad = ['discard all refrigerated medicines', 'stop taking',
               'ration your medicine', 'medicine is safe']
        f[med_key] += (' ' + bad[variant%4] + '.').encode()
    elif family == 4:
        obj = json.loads(f[src_key]); row=obj['sources'][0]
        if variant%8==0: row['kind']='regulator'
        elif variant%8==1: row['publisher']='Emergency Agency'
        elif variant%8==2: row['id']='different-id'
        elif variant%8==3: obj['sources'].append(dict(row))
        elif variant%8==4: obj.pop('sources')
        elif variant%8==5: obj['sources']='not-array'
        elif variant%8==6: obj['sources']=[]
        else: row['kind']='professional-body'
        f[src_key] = json.dumps(obj).encode()
    elif family == 5:
        obj = json.loads(f[tax_key]); a=obj['slate']
        if variant<4: a[variant]['gate']=False
        else: a[variant-4]['status']='published'
        f[tax_key]=json.dumps(obj).encode()
    elif family == 6:
        s = TEST
        moves = [
            ('shutil.copytree(ROOT, sandbox)', 'pass'),
            ('build.Library(root=sandbox)', 'build.Library()'),
            ('register_path.write_text("synthetic")','ROOT.write_text("synthetic")'),
            ('fragment.write_text("synthetic")','ROOT.unlink()'),
        ]
        old,new = moves[variant%4]
        if variant==6:
            old,new = ('fragment.write_text("synthetic")', 'ROOT.write_text("synthetic")')
        if variant>=4:
            # Replace only the second matching occurrence in the second method.
            i=s.index('    def test_register_fragments_cannot_duplicate_ids')
            s=s[:i]+s[i:].replace(old,new,1)
        else: s=s.replace(old,new,1)
        f[test_key]=s.encode()
    else:
        if variant<5:
            f.pop(list(gate.PINS)[variant])
        elif variant==5:
            obj=json.loads(f[tax_key]);obj['slate'].pop();f[tax_key]=json.dumps(obj).encode()
        elif variant==6:
            obj=json.loads(f[tax_key]);obj['slate'][-1]['slug']=obj['slate'][5]['slug'];f[tax_key]=json.dumps(obj).encode()
        else:
            f[tax_key]=b'{broken json'
    return f


def make_case(family, variant):
    def test(self):
        tampered = mutate(fixture(),family,variant)
        with self.subTest(family=family,variant=variant):
            self.assertTrue(gate.audit_payloads(tampered,False), 'mutation was silently accepted')
    return test

class MutationMatrix(unittest.TestCase):
    pass

for family in range(8):
    for variant in range(8):
        setattr(MutationMatrix,f'test_mutation_f{family:02d}_v{variant:02d}',make_case(family,variant))

if __name__ == '__main__':
    unittest.main(verbosity=2)
