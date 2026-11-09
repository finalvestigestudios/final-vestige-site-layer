"""Real temp-filesystem security regressions for the sealed WordPress plugin mount.
Synthetic content only; no production access, real subscriptions or staging runtime.
"""
from pathlib import Path
import unittest
import test_run_local_playground as runner
import test_make_local_playground as staging
import make_local_playground as builder
from run_local_playground import AdmissionError

class RunnerMountCustody(unittest.TestCase):
    setUp = runner.LauncherTests.setUp
    prep = runner.LauncherTests.prep
    def test_public_html_copy_rejected(self):
        (self.out/'plugin'/builder.ZIPROOT/'index.html.txt').write_text('REDACTED SYNTHETIC MARKUP')
        with self.assertRaisesRegex(AdmissionError, 'Unsafe public files'):
            self.prep()
    def test_hidden_asset_rejected(self):
        (self.out/'plugin'/builder.ZIPROOT/'.secret').write_text('SYNTHETIC')
        with self.assertRaisesRegex(AdmissionError, 'Unsafe public files'):
            self.prep()
    def test_nested_asset_directory_rejected(self):
        d=self.out/'plugin'/builder.ZIPROOT/'assets';d.mkdir()
        (d/'source.js').write_text('/* SYNTHETIC */')
        with self.assertRaisesRegex(AdmissionError, 'Unsafe public files'):
            self.prep()
    def test_unexpected_php_script_rejected(self):
        (self.out/'plugin'/builder.ZIPROOT/'debug.php').write_text('<?php echo "test";')
        with self.assertRaisesRegex(AdmissionError, 'Unsafe public files'):
            self.prep()
    def test_symlinked_public_directory_rejected(self):
        target=self.out/'elsewhere';target.mkdir()
        (self.out/'plugin'/builder.ZIPROOT/'assets').symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(AdmissionError,'Unsafe public files'):
            self.prep()

class BuilderMountCustody(unittest.TestCase):
    setUp = staging.StageTests.setUp
    tearDown = staging.StageTests.tearDown
    _cmd = staging.StageTests._cmd
    def test_builder_rejects_public_asset_before_writing_zip(self):
        out=self.base/'out';d=out/'plugin'/builder.ZIPROOT/'assets';d.mkdir(parents=True)
        (d/'index.html.txt').write_text('SECRET SYNTHETIC SOURCE')
        with self.assertRaisesRegex(ValueError,'Unexpected potentially public files'):
            builder.build(self.repo,out,self.head)
        self.assertFalse((out/'sealed-review.zip').exists())
    def test_builder_rejects_existing_plugin_symlink_without_writing_external(self):
        out=self.base/'out';d=out/'plugin'/builder.ZIPROOT;d.mkdir(parents=True)
        canary=self.base/'external.php';canary.write_text('CANARY_UNMODIFIED')
        (d/builder.PLUGIN).symlink_to(canary)
        with self.assertRaisesRegex(ValueError,'Unsafe staging output file'):
            builder.build(self.repo,out,self.head)
        self.assertEqual(canary.read_text(),'CANARY_UNMODIFIED')
    def test_builder_rejects_zip_symlink_without_writing_external(self):
        out=self.base/'out';out.mkdir()
        canary=self.base/'external.zip';canary.write_text('CANARY_UNMODIFIED')
        (out/'sealed-review.zip').symlink_to(canary)
        with self.assertRaisesRegex(ValueError,'Unsafe staging output file'):
            builder.build(self.repo,out,self.head)
        self.assertEqual(canary.read_text(),'CANARY_UNMODIFIED')
    def test_builder_rejects_plugin_dir_symlink(self):
        out=self.base/'out';(out/'plugin').mkdir(parents=True)
        other=self.base/'external-plugin';other.mkdir()
        (out/'plugin'/builder.ZIPROOT).symlink_to(other,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'Unsafe staging output directory'):
            builder.build(self.repo,out,self.head)
        self.assertFalse((other/builder.PLUGIN).exists())
    def test_builder_rejects_blueprint_symlink(self):
        out=self.base/'out';out.mkdir()
        canary=self.base/'external-blueprint.json';canary.write_text('CANARY_UNMODIFIED')
        (out/'blueprint.json').symlink_to(canary)
        with self.assertRaisesRegex(ValueError,'Unsafe staging output file'):
            builder.build(self.repo,out,self.head)
        self.assertEqual(canary.read_text(),'CANARY_UNMODIFIED')

if __name__ == '__main__':unittest.main()
