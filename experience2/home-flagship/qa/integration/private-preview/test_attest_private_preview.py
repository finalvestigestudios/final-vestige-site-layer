"""Executable offline Git-custody regression suite. No WordPress / external I/O."""
from __future__ import annotations
import json
import sys
from pathlib import Path
import subprocess
import tempfile
import unittest
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
HOME = Path('experience2/home-flagship')
PRIVATE = HOME / 'qa/integration/private-preview'
CONTRACT = HOME / 'qa/integration/check_contract.py'
ASSETS = ['index.html','flagship.css','chronicle.css','chronicle-lens.css',
'inquiry.css','observer-lab.css','reading-trail.css','flagship.js','observer-lab.js',
'chronicle-lens.js','reading-trail.js']

# Tests copy the real candidate PHP/Python source from this exact checkout.


def run(repo, *args, check=True):
    result = subprocess.run(args,cwd=repo, capture_output=True, text=True)
    if check and result.returncode: raise AssertionError(result.stderr)
    return result


class AttestedBuilderTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='fv-attest-test-')
        self.repo=Path(self.tmp.name)/'repo'
        self.repo.mkdir()
        src=self.repo/HOME
        private=self.repo/PRIVATE
        private.mkdir(parents=True)
        (self.repo/CONTRACT).parent.mkdir(parents=True,exist_ok=True)
        for name in ASSETS:
            (src/name).write_text('/* fixture: '+name+' */\n')
        (src/'source-manifest.json').write_text('{"records": []}\n')
        (self.repo/CONTRACT).write_text('ASSETS='+repr(ASSETS)+'\n'
            'def scan(root):\n'
            '  return ({"present":all((root/n).is_file() for n in ASSETS)}, {}, [] if all((root/n).is_file() for n in ASSETS) else ["missing"])\n')
        for name in ['build_private_preview.py','fv-ex2-private-preview.php']:
            candidate = HERE/name
            if not candidate.is_file():
                raise RuntimeError('Run from the complete Git checkout: missing '+str(candidate))
            (private/name).write_bytes(candidate.read_bytes())
        source_gate = self.repo/HOME/'qa/release-candidate/source_gate.mjs'
        source_gate.parent.mkdir(parents=True,exist_ok=True)
        source_gate.write_text('''import {writeFileSync} from 'node:fs';
const p=process.argv[process.argv.indexOf('--report')+1];
writeFileSync(p,JSON.stringify({source:{status:'PASS'},media:{status:'HOLD'},release:{status:'HOLD'}}));
''')
        (private/'attest_private_preview.py').write_bytes((HERE/'attest_private_preview.py').read_bytes())
        run(self.repo,'git','init','-q')
        run(self.repo,'git','config','user.name','QA Tester')
        run(self.repo,'git','config','user.email','tester@example.invalid')
        run(self.repo,'git','add','-A')
        run(self.repo,'git','commit','-qm','Create synthetic checkout for security tests')
        self.sha=run(self.repo,'git','rev-parse','HEAD').stdout.strip()
        self.out=Path(self.tmp.name)/'private.zip'
        self.report=Path(self.tmp.name)/'receipt.json'

    def tearDown(self): self.tmp.cleanup()

    def build(self, sha=None):
        return run(self.repo,sys.executable,str(self.repo/PRIVATE/'attest_private_preview.py'),
            '--repo',str(self.repo),'--expected-head',sha or self.sha,
            '--out',str(self.out),'--report',str(self.report),check=False)

    def test_exact_head_build_attests_zip_and_maintains_hold(self):
        r=self.build()
        self.assertEqual(r.returncode,0,r.stderr)
        receipt=json.loads(self.report.read_text())
        self.assertEqual(receipt['git_head'],self.sha)
        self.assertEqual(receipt['source_files_verified'],17)
        self.assertEqual(receipt['canonical_source_gate'],'PASS')
        self.assertTrue(receipt['deterministic_rebuild'])
        self.assertEqual(receipt['production_release'],'HOLD')
        with ZipFile(self.out) as archive:
            self.assertEqual(len(archive.namelist()),4)
            self.assertEqual(set(Path(n).suffix for n in archive.namelist()),{'.php','.json','.txt'})

    def test_canonical_source_gate_rejects_a_bad_page(self):
        target=self.repo/HOME/'qa/release-candidate/source_gate.mjs'
        target.write_text("import {writeFileSync} from 'node:fs';"
        "const p=process.argv[process.argv.indexOf('--report')+1];"
        "writeFileSync(p,JSON.stringify({source:{status:'FAIL'},release:{status:'HOLD'}}));")
        run(self.repo,'git','add','-A')
        run(self.repo,'git','commit','-qm','Synthetic source gate rejects')
        sha=run(self.repo,'git','rev-parse','HEAD').stdout.strip()
        r=self.build(sha)
        self.assertNotEqual(r.returncode,0)
        self.assertIn('SOURCE PASS',r.stderr)

    def test_wrong_git_sha_fails_before_build(self):
        r=self.build('f'*40)
        self.assertNotEqual(r.returncode,0)
        self.assertIn('SHA MISMATCH',r.stderr)
        self.assertFalse(self.out.exists())

    def test_malformed_sha_fails(self):
        r=self.build('main')
        self.assertNotEqual(r.returncode,0)
        self.assertIn('40 lowercase',r.stderr)

    def test_dirty_homepage_blocks(self):
        (self.repo/HOME/'index.html').write_text('modified')
        r=self.build()
        self.assertNotEqual(r.returncode,0)
        self.assertIn('DIRTY',r.stderr)

    def test_dirty_php_blocks(self):
        target=self.repo/PRIVATE/'fv-ex2-private-preview.php'
        target.write_text(target.read_text()+'\n// uncommented change')
        r=self.build()
        self.assertNotEqual(r.returncode,0)
        self.assertIn('DIRTY',r.stderr)

    def test_dirty_contract_rejected_before_import(self):
        target=self.repo/CONTRACT
        target.write_text(target.read_text()+'\nraise RuntimeError("SHOULD NOT EXECUTE")\n')
        r=self.build()
        self.assertNotEqual(r.returncode,0)
        self.assertIn('DIRTY',r.stderr)
        self.assertNotIn('SHOULD NOT EXECUTE',r.stderr)

    def test_dirty_builder_rejected_before_import(self):
        target=self.repo/PRIVATE/'build_private_preview.py'
        target.write_text(target.read_text()+'\nraise RuntimeError("SHOULD NOT EXECUTE")\n')
        r=self.build()
        self.assertNotEqual(r.returncode,0)
        self.assertIn('DIRTY',r.stderr)
        self.assertNotIn('SHOULD NOT EXECUTE',r.stderr)

    def test_untracked_source_blocks(self):
        target=self.repo/HOME/'reading-trail.js'
        run(self.repo,'git','rm','-q','--cached',str(target.relative_to(self.repo)))
        r=self.build()
        self.assertNotEqual(r.returncode,0)
        self.assertIn('ls-files',r.stderr)

    def test_symlink_source_rejected(self):
        target=self.repo/HOME/'index.html'
        target.unlink()
        target.symlink_to(self.repo/HOME/'flagship.css')
        r=self.build()
        self.assertNotEqual(r.returncode,0)
        self.assertIn('Unsafe/missing',r.stderr)

    def test_caller_sha_not_considered_attested_without_git(self):
        (self.repo/'.git').rename(self.repo/'.git-offline')
        r=self.build()
        self.assertNotEqual(r.returncode,0)
        self.assertIn('Git failed',r.stderr)

    def test_invalid_contract_asset_set_fails(self):
        contract=self.repo/CONTRACT
        contract.write_text(contract.read_text()+"\nASSETS=['index.html']\n")
        run(self.repo,'git','add','-A')
        run(self.repo,'git','commit','-qm','Unexpected manifest')
        new_sha=run(self.repo,'git','rev-parse','HEAD').stdout.strip()
        r=self.build(new_sha)
        self.assertNotEqual(r.returncode,0)
        self.assertIn('11-asset',r.stderr)


if __name__=='__main__': unittest.main(verbosity=2)
