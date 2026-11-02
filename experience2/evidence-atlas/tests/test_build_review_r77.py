"""R77 deterministic source archive unit tests; uses local git fixtures only."""
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from build_review_r77 import build

class TestR77Determinism(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)/'source'
        self.root.mkdir()
        def g(*parts):
            return subprocess.check_output(['git','-C',str(self.root),*parts],stderr=subprocess.DEVNULL)
        g('init','-q')
        (self.root/'source.php').write_text('<?php echo "test";\n')
        (self.root/'tests.py').write_text('assert True\n')
        g('add','.')
        g('-c','user.name=Apollo QA','-c','user.email=apollo@invalid.local','commit','-qm','seed')
        self.head=g('rev-parse','HEAD').decode().strip()
        self.g=g
        self.files=('source.php','tests.py')
    def tearDown(self): self.tmp.cleanup()
    def test_repeated_archives_identical(self):
        one=Path(self.tmp.name)/'one.zip'
        two=Path(self.tmp.name)/'two.zip'
        a=build(self.root,self.head,one,self.files)
        b=build(self.root,self.head,two,self.files)
        self.assertEqual(one.read_bytes(),two.read_bytes())
        self.assertEqual(a['sha256'],b['sha256'])
        with ZipFile(one) as z:
            data=json.loads(z.read('R77_SOURCE_MANIFEST.json'))
            self.assertEqual(data['head'],self.head)
            self.assertEqual(data['photo_rights_cleared'],0)
            self.assertEqual(z.namelist(),['source.php','tests.py','R77_SOURCE_MANIFEST.json'])
            self.assertEqual(data['files']['source.php']['sha256'],hashlib.sha256((self.root/'source.php').read_bytes()).hexdigest())
    def test_mutated_checkout_refused(self):
        (self.root/'source.php').write_text('tampered')
        with self.assertRaisesRegex(ValueError,'DIRTY_OR_DIFFERENT_HEAD'):
            build(self.root,self.head,Path(self.tmp.name)/'x.zip',self.files)
    def test_wrong_head_refused(self):
        with self.assertRaisesRegex(ValueError,'DIRTY_OR_DIFFERENT_HEAD'):
            build(self.root,'a'*40,Path(self.tmp.name)/'x.zip',self.files)
    def test_repo_internal_output_refused(self):
        with self.assertRaisesRegex(ValueError,'OUTPUT_INSIDE_REPOSITORY'):
            build(self.root,self.head,self.root/'output.zip',self.files)
    def test_unsorted_duplicate_allowlist_refused(self):
        with self.assertRaisesRegex(ValueError,'FILE_ALLOWLIST_INVALID'):
            build(self.root,self.head,Path(self.tmp.name)/'x.zip',('tests.py','source.php'))
        with self.assertRaisesRegex(ValueError,'FILE_ALLOWLIST_INVALID'):
            build(self.root,self.head,Path(self.tmp.name)/'x.zip',('source.php','source.php'))

if __name__=='__main__':unittest.main()
