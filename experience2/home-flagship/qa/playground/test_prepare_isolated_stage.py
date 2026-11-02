"""Offline regression suite: only synthetic theme/plugin ZIPs, no WordPress writes."""
import io
import subprocess
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from prepare_isolated_stage import (safe_zip_contents, validate_theme, validate_plugin,
                                    create_blueprint, build_stage, digest, verify_theme_pin, verify_stage_checkout, STAGE_FILES, STAGE_SOURCE)

HEAD = 'a'*40


def zip_bytes(files):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
        for path, body in files.items():z.writestr(path,body)
    return b.getvalue()


def fixture_plugin():
    p=b'<?php if (!defined(\'ABSPATH\')) { exit; } return [];'
    m={'release_status':'HOLD_UNPUBLISHED_STAGING_ONLY',
       'payload_in_php_executable_only':True,'payload_sha256':digest(p),
       'expected_git_head_given_by_caller':HEAD}
    files={'fv-ex2-private-preview.php':b"<?php FV_EX2_ALLOW_PREVIEW fv_ex2_private_authorized ['staging', 'development', 'local']",
           'fv-ex2-private-payload.php':p,'STAGING_MANIFEST.json':json.dumps(m).encode(),
           'INSTALLATION_HOLD.txt':b'HOLD'}
    return zip_bytes({'fv-ex2-private-preview/'+k:v for k,v in files.items()})


class StageTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        (self.base/'repo').mkdir()
        self.themezip=self.base/'assembler.zip'
        self.themezip.write_bytes(zip_bytes({'assembler/style.css':b'/*\nTheme Name: Assembler\n*/',
                                             'assembler/templates/index.html':b'<!-- wp:post-content /-->'}))

    def test_blueprint_preview_is_private_local_and_does_not_set_homepage(self):
        bp=create_blueprint();s=json.dumps(bp)
        self.assertTrue(bp['login'])
        self.assertIn('WP_ENVIRONMENT_TYPE',s)
        self.assertIn('FV_EX2_ALLOW_PREVIEW',s)
        self.assertIn("'post_status' => 'private'",s)
        self.assertIn("wp_get_environment_type() !== 'local'",s)
        self.assertNotIn('update_option(',s)
        self.assertNotIn('finalvestige.com',s)
        self.assertNotIn('wp site empty',s)
        self.assertNotIn('importWxr',s)

    def test_theme_is_validated(self):
        f=safe_zip_contents(self.themezip,strip_root=True)
        validate_theme(f)
        self.assertEqual(set(f),{'style.css','templates/index.html'})

    def test_wrong_theme_refused(self):
        self.themezip.write_bytes(zip_bytes({'assembler/style.css':b'Theme Name: Other',
                                             'assembler/templates/index.html':b'x'}))
        with self.assertRaisesRegex(ValueError,'Assembler'):
            validate_theme(safe_zip_contents(self.themezip,strip_root=True))

    def test_zip_slip_refused(self):
        self.themezip.write_bytes(zip_bytes({'assembler/../evil.php':b'x'}))
        with self.assertRaisesRegex(ValueError,'Unsafe'):
            safe_zip_contents(self.themezip,strip_root=True)

    def test_case_collision_refused(self):
        self.themezip.write_bytes(zip_bytes({'assembler/style.css':b'x','assembler/STYLE.CSS':b'y'}))
        with self.assertRaisesRegex(ValueError,'colliding'):
            safe_zip_contents(self.themezip,strip_root=True)

    def test_wrong_archive_root_refused(self):
        self.themezip.write_bytes(zip_bytes({'evil/style.css':b'x'}))
        with self.assertRaisesRegex(ValueError,'assembler'):
            safe_zip_contents(self.themezip,strip_root=True)

    def test_private_plugin_guards(self):
        pz=self.base/'p.zip';pz.write_bytes(fixture_plugin())
        plugin={k.split('/',1)[1]:v for k,v in safe_zip_contents(pz,strip_root=False).items()}
        self.assertEqual(validate_plugin(plugin)['expected_git_head_given_by_caller'],HEAD)
        plugin['script.js']=b'public source'
        with self.assertRaisesRegex(ValueError,'Unexpected'):
            validate_plugin(plugin)

    def test_plugin_payload_tamper_refused(self):
        pz=self.base/'p.zip';pz.write_bytes(fixture_plugin())
        plugin={k.split('/',1)[1]:v for k,v in safe_zip_contents(pz,strip_root=False).items()}
        plugin['fv-ex2-private-payload.php']+=b'tamper'
        with self.assertRaisesRegex(ValueError,'Tampered'):
            validate_plugin(plugin)

    def test_build_produces_local_mounts_and_holds(self):
        def attest(repo,head,out):
            out.write_bytes(fixture_plugin())
            return {'git_head':head,'canonical_source_gate':'PASS','production_release':'HOLD',
                    'status':'ATTESTED_SOURCE_ONLY_RELEASE_HOLD'}
        out=self.base/'output'
        with patch('prepare_isolated_stage.verify_stage_checkout',return_value={'verified':'synthetic-test-only'}):
            record=build_stage(self.base/'repo',HEAD,self.themezip,out,expected_theme_sha256=digest(self.themezip.read_bytes()),attester=attest)
        self.assertEqual(record['release'],'HOLD')
        self.assertEqual(record['wordpress_instance'],'NOT_STARTED')
        self.assertFalse((out/'mounts'/'fv-ex2-private-preview'/'index.html').exists())
        self.assertTrue((out/'mounts'/'assembler'/'templates'/'index.html').exists())
        self.assertIn('--port=9400',json.loads((out/'playground-cli-arguments.json').read_text()))
        with self.assertRaisesRegex(ValueError,'empty'):
            build_stage(self.base/'repo',HEAD,self.themezip,out,expected_theme_sha256=digest(self.themezip.read_bytes()),attester=attest)

    def test_mismatched_receipt_refused(self):
        def attest(repo,head,out):
            out.write_bytes(fixture_plugin())
            return {'git_head':'b'*40,'canonical_source_gate':'PASS','production_release':'HOLD','status':'INVALID'}
        with patch('prepare_isolated_stage.verify_stage_checkout',return_value={'verified':'synthetic-test-only'}):
            with self.assertRaisesRegex(ValueError,'Attestation'):
                build_stage(self.base/'repo',HEAD,self.themezip,self.base/'output',expected_theme_sha256=digest(self.themezip.read_bytes()),attester=attest)

    def test_output_inside_repo_refused(self):
        with self.assertRaisesRegex(ValueError,'outside'):
            build_stage(self.base/'repo',HEAD,self.themezip,self.base/'repo'/'test')

    def test_missing_exact_git_sha_refused(self):
        with self.assertRaisesRegex(ValueError,'full exact'):
            build_stage(self.base/'repo','main',self.themezip,self.base/'out')

    def test_theme_digest_not_optional_or_derived_from_input(self):
        raw = self.themezip.read_bytes()
        with self.assertRaisesRegex(ValueError,'independently recorded'):
            verify_theme_pin(raw, None)
        with self.assertRaisesRegex(ValueError,'SHA-256 mismatch'):
            verify_theme_pin(raw, 'f'*64)
        self.assertEqual(verify_theme_pin(raw,digest(raw)),digest(raw))

    def test_unpinned_stage_refused_even_with_synthetic_attester(self):
        with patch('prepare_isolated_stage.verify_stage_checkout',return_value={'verified':'test'}):
            with self.assertRaisesRegex(ValueError,'THEME PROVENANCE HOLD'):
                build_stage(self.base/'repo',HEAD,self.themezip,self.base/'out',attester=lambda *_: {})

    def make_git_checkout(self):
        repo=self.base/'real-git'
        repo.mkdir()
        subprocess.run(['git','init','-q',str(repo)],check=True)
        for fname in STAGE_FILES:
            path=repo/STAGE_SOURCE/fname
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text('test source '+fname+'\n')
        subprocess.run(['git','-C',str(repo),'add','.'],check=True)
        subprocess.run(['git','-C',str(repo),'-c','user.name=FV Local QA',
                        '-c','user.email=local@example.invalid','commit','-qm','stage source fixture'],check=True)
        head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
        return repo,head

    def test_real_git_stage_sources_exact_clean_and_dirty_rejected(self):
        repo,head=self.make_git_checkout()
        receipt=verify_stage_checkout(repo,head)
        self.assertEqual(len(receipt),len(STAGE_FILES))
        with self.assertRaisesRegex(ValueError,'checkout HEAD'):
            verify_stage_checkout(repo,'a'*40)
        (repo/STAGE_SOURCE/STAGE_FILES[0]).write_text('unexpected change')
        with self.assertRaisesRegex(ValueError,'uncommitted/modified'):
            verify_stage_checkout(repo,head)

    def test_stage_symlink_refused(self):
        repo,head=self.make_git_checkout()
        target=repo/STAGE_SOURCE/STAGE_FILES[1]
        target.unlink()
        target.symlink_to(repo/STAGE_SOURCE/STAGE_FILES[0])
        with self.assertRaisesRegex(ValueError,'missing/unsafe'):
            verify_stage_checkout(repo,head)


if __name__=='__main__':unittest.main()
