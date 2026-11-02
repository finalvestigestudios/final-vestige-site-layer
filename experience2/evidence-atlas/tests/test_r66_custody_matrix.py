#!/usr/bin/env python3
"""R66: immutable 54-cell source-custody matrix matches pinned NASA metadata."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import build_atlas

class CustodyMatrixR66(unittest.TestCase):
    def test_all_54_values_match_sha_pinned_r37_and_r55_sources(self):
        source=(ROOT/'atlas.js').read_text()
        result=re.search(r'const pinnedCustody=(\[.*?\]);\n',source)
        self.assertIsNotNone(result)
        matrix=json.loads(result.group(1))
        custody=build_atlas.validate_custody()
        audit=build_atlas.validate_rights_audit(custody)
        self.assertEqual(len(matrix),6)
        for row,meta,rights in zip(matrix,custody['records'],audit['records']):
            self.assertEqual(len(row),9)
            expected=[meta['catalog'],meta['identity_note'],
              ('Not printed on the linked NASA page; attribution provisional.'
                if meta['id']=='01' else 'Identifier displayed in the linked NASA page PIA field.'),
              rights['image_credit_as_displayed'] or 'No individual image credit displayed in reviewed metadata.',
              rights['producer_as_displayed'] or 'No producing center displayed in reviewed metadata.',
              rights['page_last_updated'],
              f"NASA metadata reviewed {audit['page_text_reviewed_on']}; no human link check or photograph inspection completed.",
              None, # The shared exact rights sentence is assembled from two literals.
              f"{meta['photo_role']}. The photograph alone does not prove the cause or sequence of the Apollo 1 fire."]
            self.assertEqual(row,expected)
        self.assertIn("'Individual review required.'+' No photograph is reproduced here.'",source)
        self.assertIn('if(!custodyIntact())return false;',source)
        self.assertEqual(source.count('const pinnedCustody='),1)
    def test_runtime_git_blob_matches_suite_integrity_gate(self):
        path=ROOT/'atlas.js'
        sha=subprocess.check_output(['git','hash-object',str(path)],text=True).strip()
        suite=(ROOT/'integration/fv-ex2-apollo-suite.php').read_text()
        self.assertIn("'assets/atlas.js' => '"+sha+"'",suite)
        self.assertIn('0.0.66-staging',suite)
        self.assertNotIn('wp_insert_post(',suite)
    def test_export_remains_rights_pending_and_no_external_code_paths(self):
        js=(ROOT/'atlas.js').read_text()
        self.assertNotIn('fetch(',js)
        self.assertNotIn('navigator.geolocation',js)
        self.assertNotIn('.innerHTML',js)
        self.assertIn('no photograph is reproduced',js.lower())
        page=build_atlas.make_html(build_atlas.validate_custody(),'','')
        self.assertEqual(page.count('data-fva-drawer'),6)
        self.assertEqual(page.count('data-fva-record '),6)
        self.assertNotIn('<img',page)
        self.assertNotIn('data-lat=',page)

if __name__=='__main__':unittest.main()
