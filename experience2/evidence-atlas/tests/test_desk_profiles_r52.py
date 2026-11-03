#!/usr/bin/env python3
"""R52 exact whole-profile admission tests; no WordPress or external network."""
from __future__ import annotations
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROBE = HERE / 'php_desk_profiles_r52_probe.php'
PLUGIN = ROOT / 'integration/fv-ex2-apollo-suite.php'
EXPECTED = {
    'pr158-original': {
        'final-vestige-ex2-research-desk.php':'d1879a90101b5475990132369178f42743f4b57c',
        'templates/ledger.html':'403d128c57b9bc82dac7c619651689070edef86c',
        'assets/source-ledger.css':'b8cf00afeceba115a9e9d19044fc11dcf2890cbe',
        'assets/source-ledger.js':'32e757cc4dc8708397ff65ac21e89dd319781d78'
    },
    'r38-custody-search': {
        'final-vestige-ex2-research-desk.php':'44a43c63ba262de4193295563f5762df6e731077',
        'templates/ledger.html':'4842afb84b4c993cfc4861ce7f5a7a4d7b451871',
        'assets/source-ledger.css':'7b0972fc3a920ded08f9783fddcfc9c609c7ff06',
        'assets/source-ledger.js':'57f4a639d4c37fc4355b10fe7dec085bf87c6eb7',
        'sources/R37_PHOTO_CUSTODY_CROSSWALK.json':'ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea'
    },
    'r84-chronology-certainty': {
        'final-vestige-ex2-research-desk.php':'44a43c63ba262de4193295563f5762df6e731077',
        'templates/ledger.html':'3372c0c369eedcbf715902e1eb692c57a29c7b6d',
        'assets/source-ledger.css':'feb9a524cd10437a606fa166e19d4cae5fc24320',
        'assets/source-ledger.js':'57f4a639d4c37fc4355b10fe7dec085bf87c6eb7',
        'sources/R37_PHOTO_CUSTODY_CROSSWALK.json':'ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea'
    }
}

def blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def php(payload):
    run = subprocess.run(['php', str(PROBE)], input=json.dumps(payload), text=True,
        capture_output=True, check=True)
    return json.loads(run.stdout)

class ExactDeskProfiles(unittest.TestCase):
    def test_php_syntax_and_profiles_exact(self):
        for source in (PLUGIN, PROBE):
            subprocess.run(['php', '-l', str(source)], check=True, capture_output=True)
        self.assertEqual(php({'mode':'profiles'}), EXPECTED)

    def test_profile_is_atomic_and_tamper_resistant(self):
        files = {
            'final-vestige-ex2-research-desk.php': b'<?php // R52 test only\n',
            'templates/ledger.html': b'<section data-fvx-ledger>six records</section>\n',
            'assets/source-ledger.css': b'.fv-ex2-ledger{display:block}\n',
            'assets/source-ledger.js': b'(()=>{return true})()\n',
            'sources/R37_PHOTO_CUSTODY_CROSSWALK.json': b'{"six":true}\n'
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, contents in files.items():
                target = root / name; target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(contents)
            pins = {name:blob(contents) for name,contents in files.items()}
            self.assertTrue(php({'dir':tmp,'pins':pins})['matched'])
            # The original four-file profile is also valid on its own.
            self.assertTrue(php({'dir':tmp,'pins':dict(list(pins.items())[:4])})['matched'])
            # R38's five-file profile cannot silently lose its custody crosswalk.
            cross = root / 'sources/R37_PHOTO_CUSTODY_CROSSWALK.json'
            cross.unlink()
            self.assertFalse(php({'dir':tmp,'pins':pins})['matched'])
            cross.write_bytes(files['sources/R37_PHOTO_CUSTODY_CROSSWALK.json'])
            # Any single byte of drift invalidates the entire profile.
            for name,contents in files.items():
                target=root/name; target.write_bytes(contents+b'X')
                self.assertFalse(php({'dir':tmp,'pins':pins})['matched'], name)
                target.write_bytes(contents)
            # Mixed versions may not be admitted by substituting even one pin.
            mixed=dict(pins); mixed['assets/source-ledger.js']='0'*40
            self.assertFalse(php({'dir':tmp,'pins':mixed})['matched'])
            # A pin set cannot escape the root or contain fewer than four members.
            self.assertFalse(php({'dir':tmp,'pins':{'../escape':blob(b'foo'),**pins}})['matched'])
            self.assertFalse(php({'dir':tmp,'pins':dict(list(pins.items())[:3])})['matched'])

    def test_r84_repository_files_match_new_complete_profile(self):
        # Tests the actual source in a checked-out R51/R52 repo, not a synthetic fixture.
        desk = ROOT.parent/'research-desk'
        if not (desk / 'final-vestige-ex2-research-desk.php').is_file():
            self.skipTest('Original Research Desk source not included in standalone R51 archive')
        for name, expected in EXPECTED['r84-chronology-certainty'].items():
            self.assertEqual(blob((desk/name).read_bytes()), expected, name)
        self.assertTrue(php({'dir':str(desk),'pins':EXPECTED['r84-chronology-certainty']})['matched'])
        self.assertFalse(php({'dir':str(desk),'pins':EXPECTED['r38-custody-search']})['matched'])
        self.assertFalse(php({'dir':str(desk),'pins':EXPECTED['pr158-original']})['matched'])

    def test_production_write_absent(self):
        source = PLUGIN.read_text()
        for marker in ('wp_insert_post(', 'wp_update_post(', 'update_option(', 'wp_remote_get(', 'wp_remote_post('):
            self.assertNotIn(marker, source)
        self.assertIn('return fv_ex2_apollo_suite_fallback()', source)

if __name__ == '__main__': unittest.main()
