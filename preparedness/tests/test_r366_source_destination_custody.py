#!/usr/bin/env python3
"""R366 deterministic, offline adversarial tests; no network, WordPress or publisher writes."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'tools'/'r366_source_destination_custody.py'
spec=importlib.util.spec_from_file_location('r366_custody',SCRIPT)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

GOOD='https://www.ready.gov/plan'
GOOD2='https://www.cdc.gov/ready/plan'
SRC={fn:[] for fn in m.SOURCE_FILES}
SRC['register.json']=[dict(id='ready-plan',url=GOOD,supports='Write and practice a household plan.',human_link_check=False)]
SRC['fragments/food.json']=[dict(id='cdc-plan',url=GOOD2,supports='Household readiness.',human_link_check=False)]

class Basics(unittest.TestCase):
    def test_report_permanent_hold(self):
        r=m.report([])
        self.assertEqual(r['status'],'REVIEW_REQUIRED_HARD_HOLD')
        self.assertTrue(all(r[k] is False for k in m.HOLD))
    def test_error_report_hold(self):
        r=m.report(['E']);self.assertEqual(r['status'],'INVALID_HARD_HOLD')
        self.assertEqual(r['errors'],['E'])
    def test_duplicate_json_key(self):
        with self.assertRaisesRegex(ValueError,'DUPLICATE_JSON_KEY'):
            m.decode_json('{"x":1,"x":2}')
    def test_valid_json(self):self.assertEqual(m.decode_json('{"x":1}')['x'],1)
    def test_source_rows(self):
        ids,urls,errs,review=m.source_inventory(SRC)
        self.assertFalse(errs);self.assertEqual(len(ids),2);self.assertEqual(len(urls),2)
    def test_incomplete_fragment_fails(self):
        self.assertIn('SOURCE_FRAGMENT_SET_INCOMPLETE',m.source_inventory({})[2])
    def test_duplicate_id_scope_not_approved(self):
        c={k:[dict(x) for x in v] for k,v in SRC.items()}
        c['fragments/food.json'][0]['id']='ready-plan'
        self.assertTrue(any('SHARED_ID_SCOPE_ADJUDICATION' in x for x in m.source_inventory(c)[3]))
    def test_same_id_same_url_different_scope_review(self):
        c={k:[dict(x) for x in v] for k,v in SRC.items()}
        c['fragments/food.json'][0].update(id='ready-plan',url=GOOD)
        self.assertTrue(any('SHARED_ID_SCOPE_ADJUDICATION' in x for x in m.source_inventory(c)[3]))
    def test_human_review_assertion_requires_evidence(self):
        c={k:[dict(x) for x in v] for k,v in SRC.items()}
        c['register.json'][0]['human_link_check']=True
        self.assertTrue(any('HUMAN_LINK_CHECK_ASSERTION' in x for x in m.source_inventory(c)[3]))
    def test_missing_scope(self):
        c={k:[dict(x) for x in v] for k,v in SRC.items()}
        c['register.json'][0]['supports']='  '
        self.assertTrue(any('MISSING_READING_SCOPE' in x for x in m.source_inventory(c)[2]))
    def test_invalid_source_id(self):
        c={k:[dict(x) for x in v] for k,v in SRC.items()}
        c['register.json'][0]['id']='BAD ID'
        self.assertTrue(any('INVALID_SOURCE_ID' in x for x in m.source_inventory(c)[2]))
    def test_bad_source_record(self):
        c={k:list(v) for k,v in SRC.items()};c['register.json']=[None]
        self.assertTrue(any('INVALID_SOURCE_ID' in x for x in m.source_inventory(c)[2]))
    def test_bad_fragment_type(self):
        c=dict(SRC);c['register.json']={}
        self.assertTrue(any('BAD_FRAGMENT' in x for x in m.source_inventory(c)[2]))
    def test_digest_stable(self):self.assertEqual(m.digest('a'),m.digest('a'))
    def test_html_too_large(self):
        with self.assertRaises(ValueError):m.extract('X'*500001)
    def test_a_without_href(self):
        self.assertIn('LINK_MISSING_HREF',m.extract('<a>No link</a>').errors)
    def test_inline_js_handler(self):
        self.assertIn('INLINE_EVENT_HANDLER',m.extract('<button onclick="buy()">x</button>').errors)
    def test_href_control(self):
        self.assertIn('CONTROL_IN_DESTINATION',m.extract('<a href="https://ready.gov/\x00">bad</a>').errors)
    def test_anchor_set(self):
        self.assertIn('inside',m.extract('<h2 id="inside">here</h2>').ids)
    def test_script_count(self):self.assertEqual(m.extract('<script></script>').scripts,1)

URL_INVALID=[
    ('http://ready.gov/x','NON_HTTPS_DESTINATION'),
    ('javascript:alert(1)','NON_HTTPS_DESTINATION'),
    ('data:text/plain,hi','NON_HTTPS_DESTINATION'),
    ('ftp://ready.gov','NON_HTTPS_DESTINATION'),
    ('https://user:pass@ready.gov/x','EMBEDDED_CREDENTIALS'),
    ('https://ready.gov:8443/x','UNAPPROVED_PORT'),
    ('https://ready.gov:bad/x','INVALID_PORT'),
    ('https://localhost/x','INVALID_OR_LOCAL_HOST'),
    ('https://localhost.localdomain/x','INVALID_OR_LOCAL_HOST'),
    ('https://127.0.0.1/x','DIRECT_IP_DESTINATION'),
    ('https://192.168.0.1/x','DIRECT_IP_DESTINATION'),
    ('https://[::1]/x','DIRECT_IP_DESTINATION'),
    ('https://example..org/x','INVALID_HOSTNAME'),
    ('https://example.org./x','INVALID_OR_LOCAL_HOST'),
    ('https://example.org/has space','CONTROL_OR_WHITESPACE_IN_URL'),
    (' https://example.org','CONTROL_OR_WHITESPACE_IN_URL'),
    ('https://example.org/a\\b','CONTROL_OR_WHITESPACE_IN_URL'),
    ('https://éxample.org/x','INVALID_HOSTNAME'),
    ('https://ex%41mple.org/x','INVALID_OR_LOCAL_HOST'),
    ('https://example.org/\n','CONTROL_OR_WHITESPACE_IN_URL'),
    ('https://example.org/#{{cite:x}}','CITATION_IN_FRAGMENT'),
    ('https:///missing-host','NON_HTTPS_DESTINATION'),
    ('','INVALID_URL_TYPE_OR_SIZE'),
    (None,'INVALID_URL_TYPE_OR_SIZE'),
]

class URLCases(unittest.TestCase):
    pass

def add_url_case(i,url,error):
    def test(self):self.assertEqual(m.valid_url(url)[1],error)
    setattr(URLCases,'test_r366_bad_url_%02d'%i,test)
for i,(url,error) in enumerate(URL_INVALID):add_url_case(i,url,error)

class HrefCases(unittest.TestCase):
    pass

HREF_INVALID=[
    ('//evil.com/a','PROTOCOL_RELATIVE_OR_EMPTY'),
    ('','PROTOCOL_RELATIVE_OR_EMPTY'),
    ('\\evil.com','PROTOCOL_RELATIVE_OR_EMPTY'),
    ('#missing','BROKEN_INTERNAL_ANCHOR'),
    ('#','BROKEN_INTERNAL_ANCHOR'),
    ('/preparedness/ bad','UNSAFE_RELATIVE_URL'),
    ('/preparedness/\\evil','UNSAFE_RELATIVE_URL'),
    ('/preparedness/x\n','UNSAFE_RELATIVE_URL'),
    ('http://ready.gov','NON_HTTPS_DESTINATION'),
    ('mailto:test@example.org','NON_HTTPS_DESTINATION'),
    ('tel:911','NON_HTTPS_DESTINATION'),
    ('data:text/html,x','NON_HTTPS_DESTINATION'),
    ('javascript:void(0)','NON_HTTPS_DESTINATION'),
    ('https://localhost/login','INVALID_OR_LOCAL_HOST'),
]
for i,(href,error) in enumerate(HREF_INVALID):
    def test(self,href=href,error=error):self.assertEqual(m.classify_href(href,ids=['inside'])[1],error)
    setattr(HrefCases,'test_r366_bad_href_%02d'%i,test)

class LinkCustody(unittest.TestCase):
    def check(self,old,new,expected,field='errors'):
        e,r,d=m.compare_link_custody(old,new,{m.valid_url(GOOD)[0]:[1]})
        self.assertTrue(any(expected in x for x in (e if field=='errors' else r)),(e,r,d))
    def test_same_markup_unchanged(self):
        a='<p><a href="%s">Read agency</a></p>'%GOOD
        e,r,d=m.compare_link_custody(a,a,{m.valid_url(GOOD)[0]:[1]})
        self.assertEqual(e,[]);self.assertEqual(r,[]);self.assertEqual(d['new_links'],1)
    def test_swapped_destination_rejected(self):
        self.check(f'<a href="{GOOD}">A</a>',f'<a href="{GOOD2}">A</a>','ORIGINAL_LINK_OCCURRENCE_REMOVED')
    def test_repeated_link_loss(self):
        a=f'<a href="{GOOD}">A</a>'
        self.check(a+a,a,'ORIGINAL_LINK_OCCURRENCE_REMOVED')
    def test_added_link_review(self):
        self.check('<p>x</p>',f'<a href="{GOOD}">x</a>','NEW_LINK_REQUIRES_REVIEW','review')
    def test_added_unregistered_review(self):
        self.check('<p>x</p>',f'<a href="{GOOD2}">x</a>','OUTBOUND_NOT_IN_REGISTER','review')
    def test_no_anchor_rejected(self):
        self.check('<p>x</p>','<a href="#gone">missing</a>','BROKEN_INTERNAL_ANCHOR')
    def test_valid_internal_anchor(self):
        b='<h2 id="ok">h</h2><a href="#ok">go</a>'
        self.assertFalse(m.compare_link_custody(b,b,{})[0])
    def test_new_inline_event_rejected(self):
        self.check('<p>x</p>','<button onclick="x()">now</button>','INLINE_EVENT_HANDLER')
    def test_new_script_rejected(self):
        self.check('<p>x</p>','<p>x</p><script></script>','NEW_EXECUTABLE_SCRIPT')
    def test_new_form_action_rejected(self):
        self.check('<p>x</p>','<form action="https://evil.example/upload"></form>','NEW_FORM_ACTION')
    def test_existing_external_form_still_review(self):
        a='<form action="https://example.org/upload"></form>'
        self.check(a,a,'FORM_ACTION_REQUIRES_PRIVATE_REVIEW')
    def test_retired_commerce_link_rejected(self):
        a='<a href="https://payhip.com/b/000">Buy</a>'
        self.check(a,a,'COMMERCE_DESTINATION_UNVERIFIED')
    def test_product_path_rejected(self):
        a='<a href="https://example.com/product/kit">Buy</a>'
        self.check(a,a,'COMMERCE_DESTINATION_UNVERIFIED')
    def test_checkout_query_rejected(self):
        a='<a href="https://example.com/?checkout=yes">Buy</a>'
        self.check(a,a,'COMMERCE_DESTINATION_UNVERIFIED')
    def test_unsafe_script_href_rejected(self):
        a='<a href="javascript:evil()">click</a>'
        self.check(a,a,'UNSAFE_DESTINATION')
    def test_new_link_without_href_rejected(self):
        self.check('<p>x</p>','<a>missing</a>','LINK_MISSING_HREF')
    def test_source_path_case_retained(self):
        a='<a href="https://example.org/Path?a=B">source</a>'
        self.assertIn('OUTBOUND_NOT_IN_REGISTER',str(m.compare_link_custody(a,a,{})[1]))
    def test_old_link_hash_receipt_changes_on_swap(self):
        a=f'<a href="{GOOD}">x</a>'
        b=f'<a href="{GOOD2}">x</a>'
        self.assertNotEqual(m.compare_link_custody(a,a,{})[2]['new_href_multiset_sha256'],m.compare_link_custody(a,b,{})[2]['new_href_multiset_sha256'])

class NativeGate(unittest.TestCase):
    def test_missing_checkout_hold(self):
        r=m.audit('/nonexistent/path/for/r366')
        self.assertEqual(r['errors'],['AUTHENTIC_GIT_CHECKOUT_REQUIRED'])
        self.assertFalse(r['may_publish'])
    def test_invalid_git_ref(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/'.git').mkdir()
            for bad in ['-x','../main','/tmp/path','weird ref','..','x'*121]:
                self.assertEqual(m.audit(d,bad)['errors'],['INVALID_GIT_REF'])
    def test_unavailable_original_hold(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(['git','init','-q',d],check=True)
            r=m.audit(d,'HEAD')
            self.assertEqual(r['status'],'INVALID_HARD_HOLD')
            self.assertFalse(r['qd_pass'])
    def test_git_read_only_without_index(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(['git','init','-q',d],check=True)
            p=Path(d); (p/'README').write_text('x')
            subprocess.run(['git','-C',d,'add','README'],check=True)
            subprocess.run(['git','-C',d,'-c','user.email=qa@example.invalid','-c','user.name=QA','commit','-qm','fixture'],check=True)
            before=(p/'.git'/'index').read_bytes()
            m.audit(d,'HEAD')
            self.assertEqual(before,(p/'.git'/'index').read_bytes())
    def test_cli_exit_code_two(self):
        r=subprocess.run(['python',str(SCRIPT),'--repo-root','/nonexistent/path/r366'],capture_output=True,text=True)
        self.assertEqual(r.returncode,2);self.assertIn('AUTHENTIC_GIT_CHECKOUT_REQUIRED',r.stdout)
    def test_source_url_query_kept(self):
        self.assertEqual(m.valid_url('https://www.example.org/a/?x=1&y=2')[0],'https://www.example.org/a/?x=1&y=2')
    def test_source_slash_kept(self):
        self.assertNotEqual(m.valid_url('https://www.example.org/a')[0],m.valid_url('https://www.example.org/a/')[0])
    def test_https_host_normalized_only(self):
        self.assertEqual(m.valid_url('https://WWW.EXAMPLE.ORG/A?X=Y')[0],'https://www.example.org/A?X=Y')
    def test_valid_root(self):
        self.assertEqual(m.valid_url('https://www.example.org')[0],'https://www.example.org/')
    def test_local_free_archive(self):
        self.assertEqual(m.classify_href('/preparedness/')[1],None)
    def test_off_archive_link_needs_review(self):
        self.assertEqual(m.classify_href('/focus/')[1],'OFF_ARCHIVE_RELATIVE_REVIEW')
    def test_root_anchor_found(self):
        self.assertEqual(m.classify_href('#ok',ids=['ok']),('anchor:ok',None))

if __name__ == '__main__':unittest.main(verbosity=2)
