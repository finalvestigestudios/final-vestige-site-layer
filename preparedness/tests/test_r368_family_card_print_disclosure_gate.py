"""R368 adversarial tests: print disclosure, source identity, no-JS evidence.
Offline Chromium tests use synthetic documents, NEVER authentic WP/print receipts.
"""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOL=Path(__file__).resolve().parents[1]/'tools'/'r368_family_card_print_disclosure_gate.py'
spec=importlib.util.spec_from_file_location('r368',TOOL)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)

CLEAN='''<!doctype html><html lang="en"><head><style>
.pa-card-mainhide{display:block}
@media print {.pa-card-mainhide{display:block!important}}
</style></head><body><section class="pa-article"><div class="pa-alert pa-alert--stop pa-card-mainhide"><p class="pa-alert-title">A printed card can be lost</p><p>Anyone who finds it can read it.</p></div><noscript><p>Interactive features unavailable when JavaScript is disabled.</p></noscript></section></body></html>'''
HIDDEN=CLEAN.replace('display:block!important','display:none!important')


def local_root(base,source=CLEAN,meta=None):
    root=base/'preparedness'
    p=root/m.BODY_PATH;q=root/m.META_PATH
    p.parent.mkdir(parents=True)
    p.write_text(source)
    if meta is None:meta={'slug':m.SLUG,'n':104,'status':{'publish':'draft'},'safety_review':{'state':'pending'}}
    q.write_text(json.dumps(meta))
    return root,p,q


class PureFunctions(unittest.TestCase):
    def test_sha_known(self):
        self.assertEqual(m.git_blob(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_report_hard_hold_clean(self):
        r=m.report();self.assertEqual(r['status'],'REVIEW_REQUIRED_HARD_HOLD')
    def test_report_hard_hold_invalid(self):
        self.assertEqual(m.report(['x'])['status'],'INVALID_HARD_HOLD')
    def test_flags_all_false(self):
        self.assertTrue(all(v is False for v in m.HOLD.values()))
    def test_error_dedup_sort(self):
        self.assertEqual(m.report(['z','a','z'])['errors'],['a','z'])
    def test_review_dedup_sort(self):
        self.assertEqual(m.report([],{},['z','a','z'])['human_review'],['a','z'])
    def test_schema_nonempty(self):self.assertTrue(m.SCHEMA.startswith('fv-preparedness-'))
    def test_pinned_sha_lengths(self):self.assertEqual(len(m.PIN_BODY),40);self.assertEqual(len(m.PIN_META),40)
    def test_no_checkout(self):
        with tempfile.TemporaryDirectory() as d:
            e,_,s=m.read_original(Path(d));self.assertIn('MISSING_OR_SYMLINKED_SOURCE',e);self.assertIsNone(s)
    def test_no_directory(self):
        e,_,s=m.read_original(Path('/totally/absent-root'));self.assertIn('MISSING_AUTHENTIC_PREPAREDNESS_ROOT',e)
    def test_integration_no_checkout(self):
        with tempfile.TemporaryDirectory() as d:
            r=m.audit(Path(d));self.assertEqual(r['status'],'INVALID_HARD_HOLD')
    def test_missing_chromium(self):
        e,_=m.browser_probe(CLEAN,CLEAN,CLEAN,executable='/missing-browser');self.assertIn('CHROMIUM_UNAVAILABLE',e)
    def test_missing_browser_input(self):
        e,_=m.browser_probe(None,CLEAN,CLEAN);self.assertIn('BAD_BROWSER_INPUT',e)
    def test_oversized_browser_input(self):
        e,_=m.browser_probe('A'*2_000_001,CLEAN,CLEAN);self.assertIn('BROWSER_INPUT_TOO_LARGE',e)
    def test_main_always_exit2(self):
        with tempfile.TemporaryDirectory() as d:self.assertEqual(m.main(['--root',d]),2)
    def test_bad_utf8_original(self):
        with tempfile.TemporaryDirectory() as d:
            root,p,_=local_root(Path(d));p.write_bytes(b'\xff')
            self.assertTrue(any('UNREADABLE' in e for e in m.read_original(root)[0]))
    def test_missing_source(self):
        with tempfile.TemporaryDirectory() as d:
            root,p,_=local_root(Path(d));p.unlink()
            self.assertIn('MISSING_OR_SYMLINKED_SOURCE',m.read_original(root)[0])
    def test_missing_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            root,_,q=local_root(Path(d));q.unlink()
            self.assertIn('MISSING_OR_SYMLINKED_SOURCE',m.read_original(root)[0])
    def test_symlink_original(self):
        with tempfile.TemporaryDirectory() as d:
            root,p,q=local_root(Path(d));p.unlink();p.symlink_to(q)
            self.assertIn('MISSING_OR_SYMLINKED_SOURCE',m.read_original(root)[0])
    def test_bad_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            root,_,q=local_root(Path(d));q.write_text('{broken')
            self.assertTrue(any('MALFORMED' in e for e in m.read_original(root)[0]))
    def test_real_source_fixture_pins_are_not_production(self):
        with tempfile.TemporaryDirectory() as d:
            root,_,_=local_root(Path(d));e,ev,s=m.read_original(root)
            self.assertIn('PINNED_ORIGINAL_SOURCE_IDENTITY_CHANGED',e)
            self.assertEqual(ev['original_warning_occurrences'],1)
    def test_baseline_matched_local_fixture(self):
        with tempfile.TemporaryDirectory() as d:
            root,p,q=local_root(Path(d))
            with patch.object(m,'PIN_BODY',m.git_blob(p.read_bytes())),patch.object(m,'PIN_META',m.git_blob(q.read_bytes())):
                e,ev,s=m.read_original(root)
            self.assertFalse(e,e);self.assertIn('printed card',s)


META_CHANGES={
    'wrong_slug':{'slug':'wrong','n':104,'status':{'publish':'draft'},'safety_review':{'state':'pending'}},
    'wrong_n':{'slug':m.SLUG,'n':102,'status':{'publish':'draft'},'safety_review':{'state':'pending'}},
    'missing_n':{'slug':m.SLUG,'status':{'publish':'draft'},'safety_review':{'state':'pending'}},
    'published':{'slug':m.SLUG,'n':104,'status':{'publish':'published'},'safety_review':{'state':'pending'}},
    'private':{'slug':m.SLUG,'n':104,'status':{'publish':'private'},'safety_review':{'state':'pending'}},
    'missing_status':{'slug':m.SLUG,'n':104,'safety_review':{'state':'pending'}},
    'safety_approved':{'slug':m.SLUG,'n':104,'status':{'publish':'draft'},'safety_review':{'state':'approved'}},
    'safety_not_required':{'slug':m.SLUG,'n':104,'status':{'publish':'draft'},'safety_review':{'state':'not_required'}},
    'safety_missing':{'slug':m.SLUG,'n':104,'status':{'publish':'draft'}},
    'safety_boolean':{'slug':m.SLUG,'n':104,'status':{'publish':'draft'},'safety_review':{'state':True}},
    'missing_warning':{'slug':m.SLUG,'n':104,'status':{'publish':'draft'},'safety_review':{'state':'pending'}},
}
class MetadataTamper(unittest.TestCase):pass
for name,meta in META_CHANGES.items():
    def test(self,v=meta,k=name):
        with tempfile.TemporaryDirectory() as d:
            orig=CLEAN.replace(m.ALERT,'') if k=='missing_warning' else CLEAN
            root,p,q=local_root(Path(d),source=orig,meta=v)
            with patch.object(m,'PIN_BODY',m.git_blob(p.read_bytes())),patch.object(m,'PIN_META',m.git_blob(q.read_bytes())):
                errors,_,_=m.read_original(root)
            self.assertTrue(errors,k)
    setattr(MetadataTamper,'test_'+name,test)

SOURCE_MUTATIONS={
    'alert_case':CLEAN.replace(m.ALERT,'A Printed Card Can Be Lost'),
    'alert_removed':CLEAN.replace(m.ALERT,'A card may be lost'),
    'warning_duplicate':CLEAN+CLEAN,
    'privacy_removed':CLEAN.replace(m.PRIVACY,'Privacy is fine'),
    'privacy_duplicate':CLEAN+CLEAN.replace(m.ALERT,'other'),
}
class SourceTamper(unittest.TestCase):pass
for name,body in SOURCE_MUTATIONS.items():
    def test(self,v=body,k=name):
        with tempfile.TemporaryDirectory() as d:
            root,p,q=local_root(Path(d),source=v)
            with patch.object(m,'PIN_BODY',m.git_blob(p.read_bytes())),patch.object(m,'PIN_META',m.git_blob(q.read_bytes())):
                e,_,_=m.read_original(root)
            self.assertIn('ORIGINAL_PRIVACY_DISCLOSURE_ANCHOR_DRIFT',e,k)
    setattr(SourceTamper,'test_'+name,test)

BROWSER_MUTATIONS={
    'print_display_none':CLEAN.replace('display:block!important','display:none!important'),
    'print_visibility_hidden':CLEAN.replace('display:block!important','visibility:hidden!important'),
    'print_opacity_zero':CLEAN.replace('display:block!important','opacity:0!important'),
    'screen_display_none':CLEAN.replace('display:block}', 'display:none}'),
    'print_parent_hidden':CLEAN.replace('display:block!important','display:none!important'),
    'missing_alert':CLEAN.replace(m.ALERT,'Another header'),
    'missing_privacy':CLEAN.replace(m.PRIVACY,'A less clear warning'),
    'duplicate_alert':CLEAN.replace('</section>','<div class="pa-alert"><p class="pa-alert-title">A printed card can be lost</p><p>Anyone who finds it can read it.</p></div></section>'),
    'no_noscript':CLEAN.replace('<noscript><p>Interactive features unavailable when JavaScript is disabled.</p></noscript>',''),
    'hidden_noscript':CLEAN.replace('<noscript><p>','<noscript><p style="display:none">'),
}

class ChromiumVisibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not Path('/usr/bin/chromium').is_file():raise unittest.SkipTest('chromium absent')
    def test_clean_offline_media(self):
        errors,states=m.browser_probe(CLEAN,CLEAN,CLEAN)
        self.assertFalse(errors,errors)
        self.assertTrue(all(states[k]['print']['targets'][0]['visible'] for k in states))
        self.assertTrue(all(states[k]['screen']['noJsRendered'] for k in states))
    def test_source_hidden_in_print_reproduces_bug(self):
        errors,states=m.browser_probe(HIDDEN,CLEAN,CLEAN)
        self.assertIn('DISCLOSURE_HIDDEN:original:print',errors)
        self.assertTrue(states['original']['screen']['targets'][0]['visible'])
    def test_wp_hidden_in_print(self):
        errors,_=m.browser_probe(CLEAN,HIDDEN,CLEAN)
        self.assertIn('DISCLOSURE_HIDDEN:wordpress:print',errors)
    def test_preview_hidden_in_print(self):
        errors,_=m.browser_probe(CLEAN,CLEAN,HIDDEN)
        self.assertIn('DISCLOSURE_HIDDEN:preview:print',errors)
    def test_alert_not_enough_if_nojs_missing(self):
        bad=BROWSER_MUTATIONS['no_noscript']
        errors,_=m.browser_probe(CLEAN,bad,CLEAN)
        self.assertIn('NOJS_FALLBACK_NOT_RENDERED:wordpress',errors)
    def test_missing_privacy_body_not_cleared(self):
        errors,_=m.browser_probe(CLEAN,CLEAN,BROWSER_MUTATIONS['missing_privacy'])
        self.assertIn('DISCLOSURE_MISSING_OR_MULTIPLE:preview:print',errors)

class BrowserTamper(unittest.TestCase):pass
for name,body in BROWSER_MUTATIONS.items():
    def test(self,v=body,k=name):
        if not Path('/usr/bin/chromium').is_file():self.skipTest('chromium absent')
        e,_=m.browser_probe(CLEAN,v,CLEAN)
        self.assertTrue(e,k)
    setattr(BrowserTamper,'test_'+name,test)

class GuardrailSeparation(unittest.TestCase):
    def test_missing_r367_dependency(self):
        with tempfile.TemporaryDirectory() as d:
            root,p,q=local_root(Path(d))
            with patch.object(m,'PIN_BODY',m.git_blob(p.read_bytes())),patch.object(m,'PIN_META',m.git_blob(q.read_bytes())):
                r=m.audit(root)
            self.assertIn('R367_DEPENDENCY_MISSING',r['errors'])
    def test_draft_result_never_approved(self):
        r=m.report([],{'something':'PASS'});self.assertTrue(all(r[k] is False for k in m.HOLD))
    def test_invalid_result_never_approved(self):
        r=m.report(['FAIL']);self.assertTrue(all(r[k] is False for k in m.HOLD))
    def test_no_remote_actions_in_tool(self):
        src=TOOL.read_text()
        for forbidden in ['requests.post(', 'urllib.request.urlopen(', 'httpx.post(', 'selenium.webdriver.Remote(', 'wp-json/wp/v2/posts']:
            self.assertNotIn(forbidden,src)
    def test_no_user_private_data_persisted(self):
        src=TOOL.read_text()
        self.assertNotIn('localStorage',src);self.assertNotIn('sessionStorage',src)

if __name__=='__main__':unittest.main()
