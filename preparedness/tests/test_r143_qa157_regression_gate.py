"""Synthetic and adversarial fail-closed tests; not real RC execution."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
import sys
import json
sys.path.insert(0,str(Path(__file__).parent))
import r143_qa157_regression_gate as m

class Tests(unittest.TestCase):
    def setUp(self):
        self.manifest={'schema':'R143-QA157-AUTHENTIC-PAIRS-1','candidate_ref':m.RC,
                       'qa_ref':m.QA157,'articles':deepcopy(m.EXPECTED),
                       'status':'UNREVIEWED_HUMAN_REQUIRED'}
    def test_frozen_refs(self):
        self.assertEqual(len(m.RC),40); self.assertEqual(len(m.QA157),40)
    def test_two_exact_articles(self):
        self.assertEqual(set(m.EXPECTED),{'three-day-kit','household-emergency-plan'})
    def test_expected_citation_loss(self):
        x=m.EXPECTED; self.assertEqual(x['three-day-kit']['rc_cites']-x['three-day-kit']['qa_cites'],11)
    def test_no_missing_identity(self):
        for e in m.EXPECTED.values():
            for k in ('rc_sha','qa_sha','rc_meta_sha'):
                self.assertEqual(len(e[k]),40)
    def test_blob_sha_real_git_rule(self):
        self.assertEqual(m.blob_sha(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_citation_parser_count(self):
        self.assertEqual(m.citations('{{cite:x-1}} {{cite:x-1}} {{cite:y}}'),{'x-1':2,'y':1})
    def test_malformed_citation(self):
        for bad in ('{{cite:X}}','{{cite:bad space}}','{{cite:source_underscore}}'):
            with self.subTest(bad=bad),self.assertRaises(ValueError):m.citations(bad)
    def test_meta_missing_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):m.audit(self.manifest,Path(d),Path(d))
    def test_manifest_status_forgery(self):
        self.manifest['status']='QD_PASS'
        with self.assertRaises(ValueError):m.audit(self.manifest,Path('/absent'),Path('/absent'))
    def test_manifest_missing_article(self):
        del self.manifest['articles']['three-day-kit']
        with self.assertRaises(ValueError):m.audit(self.manifest,Path('/absent'),Path('/absent'))
    def test_manifest_extra_article(self):
        self.manifest['articles']['new-article']=deepcopy(next(iter(m.EXPECTED.values())))
        with self.assertRaises(ValueError):m.audit(self.manifest,Path('/absent'),Path('/absent'))
    def test_manifest_wrong_ref(self):
        self.manifest['qa_ref']='0'*40
        with self.assertRaises(ValueError):m.audit(self.manifest,Path('/absent'),Path('/absent'))
    def test_manifest_schema_surplus(self):
        self.manifest['qd']='PASS'
        with self.assertRaises(ValueError):m.audit(self.manifest,Path('/absent'),Path('/absent'))
    def test_absolute_target_symlink_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); root.joinpath('target').write_text('abc'); root.joinpath('link').symlink_to('target')
            with self.assertRaises(ValueError):m._read(root,'link','0'*40)
    def test_absolute_target_wrong_sha_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); root.joinpath('x').write_text('abc');
            with self.assertRaises(ValueError):m._read(root,'x','0'*40)
    def test_unicode_roundtrip(self):
        s='ñino café'; self.assertEqual(m.blob_sha(s.encode()),m.blob_sha(s.encode()))
    def test_word_count(self):
        self.assertEqual(m._words('<p>alpha {{cite:x}} beta <b>gamma</b></p>'),3)

# Each dynamically registered test is a separate native unittest, not subTest inflation.
# They tamper distinct byte positions of the immutable evidence SHA, so the validator
# rejects an incorrect manifest *before* any file read or potential publishing path.
for i in range(48):
    def make_test(i):
        def test(self):
            document=deepcopy(self.manifest)
            slug=('three-day-kit' if i%2 else 'household-emergency-plan')
            prop=('rc_sha','qa_sha','rc_meta_sha')[i%3]
            original=document['articles'][slug][prop]
            pos=(i*11)%40
            document['articles'][slug][prop]=original[:pos]+('0' if original[pos]!='0' else '1')+original[pos+1:]
            with self.assertRaisesRegex(ValueError,'manifest custody'):
                m.audit(document,Path('/nonexistent'),Path('/nonexistent'))
        return test
    setattr(Tests,f'test_mutation_{i:02d}',make_test(i))

if __name__=='__main__':unittest.main()
