"""Run: python -m unittest -v test_semantic_search.py (from this folder).
Unit tests of stage-only source integrity. Browser QA is separate and mandatory.
"""
from __future__ import annotations
import hashlib
import importlib.util
import unittest
from pathlib import Path
from stage_semantic_search import build, sha, blob, ORIGINAL_JS_GIT_BLOB
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def inputs():
    # A full repository checkout uses actual source-pinned R174 -> R176 logic.
    canonical_js=ROOT/'research-desk/assets/source-ledger.js'
    orig=(canonical_js if canonical_js.exists() else HERE/'source-ledger-original.js').read_bytes()
    new=(HERE/'source-ledger-semantic-search.js').read_bytes()
    r174=ROOT/'apollo-r174/research-desk-provenance-candidate-UNPUBLISHED.html'
    r176_transform=ROOT/'apollo-r176/catalog_semantics.py'
    if r174.exists() and r176_transform.exists():
        spec=importlib.util.spec_from_file_location('r176_catalog_semantics',r176_transform)
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        html=mod.integrate(r174.read_text(encoding='utf8'))[0].encode('utf8')
    else:
        # Local archive QA fixture ONLY; does not substitute for canonical source CI.
        html=(ROOT/'evidence/R176-SOURCE-DERIVED-FRAGMENT-NOT-EXACT-WP.html').read_bytes()
    return orig,new,html

class SemanticSearchStagingGates(unittest.TestCase):
    def test_original_pr_158_git_blob_matches(self):
        a,_,_=inputs();self.assertEqual(blob(a),ORIGINAL_JS_GIT_BLOB)
    def test_valid_offline_fixture(self):
        a,b,c=inputs();report,doc=build(a,b,c,expected_r176_sha256=sha(c))
        self.assertEqual(report['historical_records'],6)
        self.assertEqual(report['nasa_media_custody_records'],6)
        self.assertEqual(len(report['preserved_links']),14)
        self.assertEqual(doc.count(b'Catalog identification not verified.'),1)
        self.assertIn(b'card.textContent',doc)
        self.assertFalse(report['production_wordpress_modified'])
    def test_wrong_js_original_holds(self):
        a,b,c=inputs()
        with self.assertRaisesRegex(ValueError,'original PR #158'):
            build(a+b' ',b,c,expected_r176_sha256=sha(c))
    def test_wrong_candidate_sha_holds(self):
        a,b,c=inputs()
        with self.assertRaisesRegex(ValueError,'independently pinned'):
            build(a,b,c,expected_r176_sha256='0'*64)
    def test_extra_link_even_with_pin_holds(self):
        a,b,c=inputs();c=c.replace(b'</section>',b'<a href="https://unapproved.test/buy">Buy</a></section>')
        with self.assertRaisesRegex(ValueError,'source links'):
            build(a,b,c,expected_r176_sha256=sha(c))
    def test_extra_script_even_with_pin_holds(self):
        a,b,c=inputs();c=c.replace(b'</section>',b'<script>alert(1)</script></section>')
        with self.assertRaisesRegex(ValueError,'executable'):
            build(a,b,c,expected_r176_sha256=sha(c))
    def test_missing_custody_blocks_even_with_pin(self):
        a,b,c=inputs();c=c.replace(b'data-fvx-r174-media-custody="01"',b'data-removed="01"')
        with self.assertRaisesRegex(ValueError,'inventory'):
            build(a,b,c,expected_r176_sha256=sha(c))
    def test_missing_semantic_index_blocks(self):
        a,b,c=inputs();b=b.replace(b'card.textContent',b'card.outerHTML')
        with self.assertRaisesRegex(ValueError,'source-custody'):
            build(a,b,c,expected_r176_sha256=sha(c))
    def test_new_tracking_fetch_blocks(self):
        a,b,c=inputs();b+=b'\nfetch("https://example.org/track")'
        with self.assertRaisesRegex(ValueError,'tracking'):
            build(a,b,c,expected_r176_sha256=sha(c))

if __name__=='__main__':unittest.main()
