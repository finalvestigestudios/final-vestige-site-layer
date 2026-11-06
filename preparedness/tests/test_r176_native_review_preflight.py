"""R176 synthetic native/executable and adversarial checks; no real safety claims."""
import copy
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import r176_native_review_preflight as gate

R174={'state':gate.HOLD,'article_count':35,'rendered_citations':2000,
      'rendered_source_uses':385,'publication_authorized':False,
      'draft_export_bytes_checked':True,'independent_qd_pass':False}
R175={'state':gate.HOLD,'articles':35,'publication_authorized':False,
      'export_compared':True,'independent_qd_pass':False}


def step(name,data='',rc=2,err=''):
    return {'step':name,'stdout':data,'stderr':err,'returncode':rc}


def make_repo(path,ntests=40):
    p=path/'preparedness'
    for f in gate.NEEDED:
        target=p/f;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('{}')
    for n in range(35):
        for ext in ('meta.json','body.html'):
            f=p/'content'/'articles'/f'example-{n}.{ext}'
            f.parent.mkdir(parents=True,exist_ok=True);f.write_text('synthetic')
    (p/'tests').mkdir(exist_ok=True)
    (p/'tests'/'test_synthetic.py').write_text(
        'import unittest\nclass T(unittest.TestCase): pass\n'+
        '\n'.join(f'setattr(T,"test_{i:02d}",lambda self: self.assertTrue(True))' for i in range(ntests)))
    (p/'tools'/'validate.py').write_text("print('0 error(s), 1 warning(s)')\n")
    (p/'tools'/'build.py').write_text(
        'from pathlib import Path\nroot=Path(__file__).resolve().parents[1]\n'
        'for area in ("wp","preview"):\n'
        '    dst=root/"build"/area\n    dst.mkdir(parents=True,exist_ok=True)\n'
        '    for n in range(35): (dst/f"example-{n}.html").write_text("DRAFT")\n')
    for name,d in (('r174_rendered_citation_gate.py',R174),('r175_link_custody_gate.py',R175)):
        (p/'tools'/name).write_text('import json,sys\nprint(json.dumps('+repr(d)+'))\nsys.exit(2)\n')
    return p

class PreflightTests(unittest.TestCase):
    def test_fake_checkout_executes_all_five_real_subprocess_steps(self):
        with tempfile.TemporaryDirectory() as t:
            p=make_repo(Path(t))
            before=gate.inventory(p)
            result=gate.preflight(Path(t),timeout=30)
            self.assertEqual(result['state'],gate.HOLD,result)
            self.assertEqual([x['status'] for x in result['checks']],
                             ['CHECKED','CHECKED','CHECKED','STRUCTURAL_HOLD','STRUCTURAL_HOLD'])
            self.assertEqual(result['checks'][2]['tests_reported'],40)
            self.assertEqual(gate.inventory(p),before)
            self.assertFalse(result['publication_authorized'])

    def test_35_tests_invalid(self):
        with tempfile.TemporaryDirectory() as t:
            make_repo(Path(t),35)
            self.assertEqual(gate.preflight(Path(t),timeout=30)['state'],gate.INVALID)

    def test_missing_repo_invalid(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(gate.preflight(Path(t))['state'],gate.INVALID)

    def test_source_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=make_repo(Path(t));f=p/'sources'/'register.json';f.unlink()
            f.symlink_to(p/'sources'/'crosswalk.json')
            with self.assertRaisesRegex(ValueError,'symlink'): gate.inventory(p)

    def test_missing_article_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=make_repo(Path(t));(p/'content/articles/example-3.body.html').unlink()
            with self.assertRaisesRegex(ValueError,'35-article'): gate.inventory(p)

    def test_extra_article_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=make_repo(Path(t))
            for ext in ('meta.json','body.html'):
                (p/f'content/articles/example-35.{ext}').write_text('{}')
            with self.assertRaisesRegex(ValueError,'35-article'): gate.inventory(p)

    def test_unpaired_slug_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=make_repo(Path(t))
            (p/'content/articles/example-3.body.html').rename(p/'content/articles/wrong.body.html')
            with self.assertRaisesRegex(ValueError,'unpaired'): gate.inventory(p)

    def test_build_outputs_not_input_manifest(self):
        with tempfile.TemporaryDirectory() as t:
            p=make_repo(Path(t));before=gate.inventory(p)
            (p/'build/wp').mkdir(parents=True)
            (p/'build/wp/test.html').write_text('test')
            self.assertEqual(before,gate.inventory(p))

    def test_original_source_change_detected(self):
        with tempfile.TemporaryDirectory() as t:
            p=make_repo(Path(t));before=gate.inventory(p)
            (p/'sources/register.json').write_text('tampered')
            self.assertNotEqual(before,gate.inventory(p))

    def test_timeout_guard(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(gate.preflight(Path(t),timeout=0)['state'],gate.INVALID)
            self.assertEqual(gate.preflight(Path(t),timeout=9999)['state'],gate.INVALID)

    def test_cli_missing_repo_always_exit_two(self):
        with tempfile.TemporaryDirectory() as t, redirect_stdout(StringIO()) as output:
            self.assertEqual(gate.main(['--repo',t]),2)
            self.assertFalse(json.loads(output.getvalue())['publication_authorized'])

    def test_valid_synthetic_gate_exit_two(self):
        with tempfile.TemporaryDirectory() as t:
            for name,d in (('r174_citations',R174),('r175_links',R175)):
                self.assertEqual(gate.assess(step(name,json.dumps(d)),Path(t))['status'],'STRUCTURAL_HOLD')

    def test_green_gate_exit_zero_is_not_approved(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(gate.assess(step('r174_citations',json.dumps(R174),0),Path(t))['status'],'FAIL')

    def test_failed_test_count(self):
        with tempfile.TemporaryDirectory() as t:
            for count in (0,1,35):
                s=step('unit_tests','',0,f'Ran {count} tests in 0.100s\nOK')
                self.assertEqual(gate.assess(s,Path(t))['status'],'FAIL')

    def test_skips_cannot_fake_36_executed(self):
        with tempfile.TemporaryDirectory() as t:
            s=step('unit_tests','',0,'Ran 36 tests in 0.100s\nOK (skipped=1)')
            self.assertEqual(gate.assess(s,Path(t))['status'],'FAIL')

    def test_invalid_json_gate_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(gate.assess(step('r174_citations','{bad'),Path(t))['status'],'FAIL')

    def test_raw_log_content_not_exposed(self):
        with tempfile.TemporaryDirectory() as t:
            report=gate.assess(step('validate','SYNTHETIC SECRET',1),Path(t))
            self.assertNotIn('SYNTHETIC SECRET',json.dumps(report))
            self.assertEqual(len(report['stdout_sha256']),64)


def generate_controls():
    mutants={
        'r174_citations': {'state':[gate.INVALID,'PASS','PUBLISHED',None],
          'article_count':[0,34,36,None,'35'],
          'rendered_citations':[0,1999,2001,None,'2000'],
          'rendered_source_uses':[0,384,386,None,'385'],
          'draft_export_bytes_checked':[False,None,'true'],
          'publication_authorized':[True,None,'false'],
          'independent_qd_pass':[True], 'qualified_source_review':[True],
          'food_safety_approved':[True], 'commercial_offer_verified':[True]},
        'r175_links': {'state':[gate.INVALID,'PASS','PUBLISHED',None],
          'articles':[0,34,36,None,'35'],
          'export_compared':[False,None,'true'],
          'publication_authorized':[True,None,'false'],
          'independent_qd_pass':[True], 'independent_source_review':[True],
          'medical_food_safety_approved':[True], 'commercial_offer_verified':[True]}}
    idx=0
    for name,fields in mutants.items():
        for key,vals in fields.items():
            for val in vals:
                idx+=1
                def check(self,n=name,k=key,v=val):
                    doc=copy.deepcopy(R174 if n=='r174_citations' else R175)
                    doc[k]=v
                    with tempfile.TemporaryDirectory() as t:
                        r=gate.assess(step(n,json.dumps(doc)),Path(t))
                        self.assertEqual(r['status'],'FAIL',(n,k,v))
                setattr(PreflightTests,f'test_mutation_{idx:03d}',check)

generate_controls()
