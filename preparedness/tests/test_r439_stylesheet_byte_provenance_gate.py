"""R439 offline synthetic CSS custody regression tests; never QD or WordPress acceptance."""
from __future__ import annotations
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS=Path(__file__).resolve().parents[1]/'tools'
SRC=TOOLS/'r439_stylesheet_byte_provenance_gate.py'
spec=importlib.util.spec_from_file_location('r439_stylesheet_byte_provenance_gate',SRC)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ROOT='https://finalvestige.com'
A=ROOT+'/wp-content/themes/site.css'
B=ROOT+'/wp-content/themes/print.css'

def fixture(head='<link rel="stylesheet" href="/wp-content/themes/site.css">',extra=''):
    return ('<!doctype html><html><head>'+head+'</head><body><main><p>Follow official safety guidance.</p></main>'+extra+'</body></html>').encode()

def pin(raw):
    return {'sha256':m.sha(raw),'bytes':len(raw),'mime':'text/css','capture_id':'review-capture-a'}

def basic(raw=b'.notice { color: black; }'):
    return {A:raw}, {A:pin(raw)}

class ByteCustody(unittest.TestCase):
    def test_clean_hash_pinned_asset_has_sri_review_only(self):
        assets,pins=basic()
        out=m.pair_review(fixture(),fixture(),assets,pins)
        self.assertIn('wordpress:'+A+':CSS_SRI_NOT_RECORDED_REVIEW',out['errors'])
        self.assertFalse(out['eligible']);self.assertFalse(out['publication_approved'])
        self.assertFalse(out['paid_offer_approved'])
    def test_valid_sri_256(self):
        raw=b'.warning{color:red}'
        sri=base64.b64encode(hashlib.sha256(raw).digest()).decode()
        doc=fixture(head=f'<link rel="stylesheet" href="/wp-content/themes/site.css" integrity="sha256-{sri}">')
        out=m.graph(doc,{A:raw},{A:pin(raw)})
        self.assertEqual(out['errors'],[])
    def test_valid_sri_384(self):
        raw=b'.x{color:blue}'
        sri=base64.b64encode(hashlib.sha384(raw).digest()).decode()
        doc=fixture(head=f'<link rel="stylesheet" href="/wp-content/themes/site.css" integrity="sha384-{sri}">')
        self.assertEqual(m.graph(doc,{A:raw},{A:pin(raw)})['errors'],[])
    def test_bad_sri(self):
        raw=b'.x{color:blue}'
        sri=base64.b64encode(hashlib.sha256(b'other').digest()).decode()
        doc=fixture(head=f'<link rel="stylesheet" href="/wp-content/themes/site.css" integrity="sha256-{sri}">')
        self.assertTrue(any('CSS_SRI_MISMATCH' in e for e in m.graph(doc,{A:raw},{A:pin(raw)})['errors']))
    def test_wrong_sha(self):
        a,p=basic();p[A]['sha256']='0'*64
        self.assertTrue(any('CSS_PIN_HASH_MISMATCH' in e for e in m.graph(fixture(),a,p)['errors']))
    def test_wrong_length(self):
        a,p=basic();p[A]['bytes']+=1
        self.assertTrue(any('CSS_PIN_LENGTH_MISMATCH' in e for e in m.graph(fixture(),a,p)['errors']))
    def test_no_source_provenance(self):
        a,p=basic();p[A]['capture_id']=''
        self.assertTrue(any('CSS_PIN_SCHEMA_INVALID' in e for e in m.graph(fixture(),a,p)['errors']))
    def test_unknown_asset(self):
        x=m.graph(fixture(),{},{});self.assertTrue(any('CSS_PIN_MISSING' in e for e in x['errors']))
    def test_unpinned_bytes(self):
        a,p=basic();self.assertTrue(any('CSS_PIN_MISSING' in e for e in m.graph(fixture(),a,{})['errors']))
    def test_pin_without_bytes(self):
        a,p=basic();self.assertTrue(any('CSS_ASSET_BYTES_MISSING' in e for e in m.graph(fixture(),{},p)['errors']))
    def test_nested_import_verified(self):
        ra=b'@import "print.css"; .notice{color:black}'
        rb=b'.notice{color:red}'
        a={A:ra,B:rb};p={u:pin(raw) for u,raw in a.items()}
        x=m.graph(fixture(),a,p)
        self.assertEqual(x['dependency_count'],2)
        self.assertIn((A,B),x['edges'])
    def test_nested_import_missing(self):
        a,p=basic(b'@import "print.css";')
        self.assertTrue(any(B in e and 'CSS_ASSET_BYTES_MISSING' in e for e in m.graph(fixture(),a,{**p,B:pin(b'.x{}')})['errors']))
    def test_cycle(self):
        a={A:b'@import "print.css";',B:b'@import "site.css";'}
        x=m.graph(fixture(),a,{u:pin(r) for u,r in a.items()})
        self.assertIn('CSS_IMPORT_CYCLE',x['errors'])
    def test_surplus(self):
        a,p=basic();a[B]=b'.extra{}';p[B]=pin(a[B]);self.assertIn('CSS_SURPLUS_UNREFERENCED_ASSET_OR_PIN',m.graph(fixture(),a,p)['errors'])
    def test_html_link_parity(self):
        a,p=basic();out=m.pair_review(fixture(),fixture(head='<link rel="stylesheet" href="/wp-content/themes/print.css">'),a,p)
        self.assertIn('WP_PREVIEW_CSS_BYTE_GRAPH_DRIFT',out['errors'])
    def test_inline_css_import(self):
        a,p=basic();h=fixture(head='<style>@import "/wp-content/themes/site.css";</style>')
        self.assertIn(('https://finalvestige.com/preparedness/',A),m.graph(h,a,p)['edges'])
    def test_inline_css_change(self):
        a,p=basic();x=m.pair_review(fixture(head='<style>p{color:red}</style>'),fixture(head='<style>p{color:black}</style>'),a,p)
        self.assertIn('WP_PREVIEW_CSS_BYTE_GRAPH_DRIFT',x['errors'])
    def test_unsafe_import(self):
        a,p=basic(b'@import "https://bad.example/evil.css";')
        self.assertTrue(any('CSS_UNTRUSTED_ORIGIN' in e for e in m.graph(fixture(),a,p)['errors']))
    def test_nonimport_url_review(self):
        a,p=basic(b'.a{background:url(/image.jpg)}')
        self.assertTrue(any('CSS_NONIMPORT_URL_REQUIRES_BROWSER_REVIEW' in e for e in m.graph(fixture(),a,p)['errors']))
    def test_unknown_import_syntax(self):
        a,p=basic(b'@import foo(bar);')
        self.assertTrue(any('CSS_UNPARSEABLE_IMPORT' in e for e in m.graph(fixture(),a,p)['errors']))
    def test_css_escape_review(self):
        a,p=basic(b'.x{co\\6cor:red}')
        self.assertTrue(any('CSS_ESCAPE_REQUIRES_BROWSER_REVIEW' in e for e in m.graph(fixture(),a,p)['errors']))
    def test_invalid_encoding(self):
        a,p=basic(b'\xff\xfe')
        self.assertTrue(any('CSS_INVALID_UTF8' in e for e in m.graph(fixture(),a,p)['errors']))
    def test_determinism(self):
        a,p=basic();self.assertEqual(m.graph(fixture(),a,p),m.graph(fixture(),a,p))
    def test_missing_parent_holds(self):
        with patch.object(m,'load_parent',side_effect=ValueError('missing')):
            x=m.audit({}, {}, {}, {}, {})
        self.assertEqual(x['release_state'],'DRAFT_HARD_HOLD');self.assertIn('PARENT_R438_AUDIT_UNAVAILABLE',x['errors'])
    def test_audit_one_still_holds(self):
        a,p=basic()
        with patch.object(m,'load_parent') as mock:
            mock.return_value.audit.return_value={'errors':[]}
            x=m.audit({'articles':[{'slug':'family-plan'}]},{'family-plan':(fixture(),fixture())},{},a,p,test_only=True)
        self.assertFalse(x['publication_approved']);self.assertEqual(len(x['asset_byte_custody_review_rows']),1)
    def test_duplicate_slug(self):
        a,p=basic()
        with patch.object(m,'load_parent') as mock:
            mock.return_value.audit.return_value={'errors':[]}
            x=m.audit({'articles':[{'slug':'family-plan'},{'slug':'family-plan'}]},{'family-plan':(fixture(),fixture())},{},a,p,test_only=True)
        self.assertIn('INVALID_OR_DUPLICATE_ARTICLE_IDENTITY',x['errors'])
    def test_missing_cli_exits_two(self):
        call=subprocess.run([sys.executable,'-I',str(SRC),'/no/manifest','/no/lock','/no/exports','/no/css','/no/assets'],text=True,capture_output=True,timeout=10)
        self.assertEqual(call.returncode,2);self.assertIn('DRAFT_HARD_HOLD',call.stdout)
    def test_safe_reader_real_file(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.css';p.write_bytes(b'.x{}');self.assertEqual(m.read_safe(d,'x.css',20),b'.x{}')
    def test_safe_reader_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'real.css';p.write_bytes(b'.x{}');(Path(d)/'link.css').symlink_to(p)
            with self.assertRaises((ValueError,OSError)):m.read_safe(d,'link.css',20)
    def test_safe_reader_hardlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'real.css';p.write_bytes(b'.x{}');(Path(d)/'link.css').hardlink_to(p)
            with self.assertRaises(ValueError):m.read_safe(d,'real.css',20)
    def test_safe_reader_oversize(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/'x.css').write_bytes(b'A'*101)
            with self.assertRaises(ValueError):m.read_safe(d,'x.css',100)
    def test_safe_reader_directory(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/'folder').mkdir()
            with self.assertRaises(ValueError):m.read_safe(d,'folder',100)
    def test_schema_unknown_fields(self):
        a,p=basic();p[A]['extra']='danger';self.assertTrue(any('CSS_PIN_SCHEMA_INVALID' in e for e in m.graph(fixture(),a,p)['errors']))
    def test_manifest_bool_length(self):
        a,p=basic();p[A]['bytes']=True;self.assertTrue(any('CSS_PIN_LENGTH_MISMATCH' in e for e in m.graph(fixture(),a,p)['errors']))
    def test_no_network_calls(self):
        src=SRC.read_text()
        for txt in ('urllib.request','requests.get(', 'requests.post(', 'httpx.get(', 'wordpress_xmlrpc','os.system(', 'subprocess.run('):
            self.assertNotIn(txt,src)

UNSAFE={
 'http':'http://finalvestige.com/a.css',
 'external':'https://bad.example/a.css',
 'proto_relative':'//bad.example/x.css',
 'javascript':'javascript:alert(1)',
 'data':'data:text/css,body{}',
 'file':'file:///etc/passwd',
 'space':' a.css',
 'newline':'a.css\n',
 'encoded_slash':'/wp%2f..%2f.css',
 'encoded_dot':'/%2e%2e/hi.css',
 'parent':'../untracked.css',
 'dot':'./same.css',
 'backslash':'..\\safe.css',
 'query':'site.css?v=1',
 'fragment':'site.css#t',
 'user':'https://user@finalvestige.com/css.css',
 'port':'https://finalvestige.com:80/css.css',
 'badport':'https://finalvestige.com:hi/css.css',
 'overlong':'a'*2100,
 'empty':'',
 'unicode':'/style-\u202e.css',
 'double_path':'/wp-content//style.css',
 'tab':'\t.css',
 'https_extra_host':'https://finalvestige.com.evil.test/s.css',
 'trailing_space':'/x.css ',
}
for label,url in UNSAFE.items():
    def test_case(self,url=url):
        with self.assertRaises(ValueError):m.canonical(url)
    setattr(ByteCustody,'test_unsafe_ref_'+label,test_case)

BAD_SRI=['sha1-AAAA','sha256-###','sha384','garbage','sha256-!','sha512-@','sha256-deadbeef']
for i,sri in enumerate(BAD_SRI):
    def test_case(self,sri=sri):
        err=m.check_sri(sri,b'hello')
        self.assertTrue('CSS_INVALID_SRI' in err or 'CSS_SRI_MISMATCH' in err)
    setattr(ByteCustody,'test_bad_sri_'+str(i),test_case)

BAD_PINS={
 'bad_mime':('mime','text/plain'),
 'no_mime':('mime',None),
 'capture_int':('capture_id',12),
 'hash_upper':('sha256','A'*64),
 'hash_short':('sha256','f'*60),
 'bytes_float':('bytes',12.0),
 'bytes_negative':('bytes',-1),
 'no_sha':('sha256',None),
}
for label,(key,value) in BAD_PINS.items():
    def test_case(self,key=key,value=value):
        a,p=basic();p[A][key]=value
        self.assertTrue(any('CSS_PIN_' in e for e in m.graph(fixture(),a,p)['errors']))
    setattr(ByteCustody,'test_invalid_pin_'+label,test_case)

if __name__=='__main__':unittest.main()
