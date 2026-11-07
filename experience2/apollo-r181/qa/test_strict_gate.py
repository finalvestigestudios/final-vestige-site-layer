"""R181 security and attribution safeguards; no outbound network."""
import asyncio
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from strict_gate import approved_url, _host, preflight, save_receipt

class SafetyTests(unittest.TestCase):
    def args(self, **kwargs):
        d={'fixture':None,'url':None,'approved_host':None,'axe_js':None,
           'axe_sha256':None,'image_policy':'links-only','minimum_images':0}
        d.update(kwargs)
        return SimpleNamespace(**d)

    def test_fixture_must_exist_and_cannot_be_release_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            f=Path(temp)/'fixture.html'; f.write_text('<p>private lab test</p>')
            self.assertEqual(preflight(self.args(fixture=f)), 'LAB_FIXTURE_ONLY')
            r=save_receipt(Path(temp),'LAB_FIXTURE_ONLY',[],[],complete=True)
            self.assertEqual(r['verdict'],'HOLD')
            self.assertIn('missing_expected_contexts',r['blockers'])
            with self.assertRaises(ValueError): preflight(self.args(fixture=Path(temp)/'missing.html'))

    def test_ambiguous_or_missing_mode_rejected(self):
        with self.assertRaises(ValueError): preflight(self.args())
        with self.assertRaises(ValueError): preflight(self.args(fixture=Path('/dev/null'),url='https://stage.example.org/'))

    def test_approved_origin_normalization_and_redirect_policy(self):
        valid='https://approved-stage.example.org/path?utm_source=youtube'
        self.assertTrue(approved_url(valid,'approved-stage.example.org'))
        for bad in [
          'http://approved-stage.example.org/x',
          'https://approved-stage.example.org.evil.test/x',
          'https://finalvestige.com/article',
          'https://www.finalvestige.com/',
          'https://approved-stage.example.org:444/x',
          'https://user:pw@approved-stage.example.org/x',
          'https://approved-stage.example.org/x#anchor',
          'file:///tmp/site.html',
        ]:
            self.assertFalse(approved_url(bad,'approved-stage.example.org'),bad)

    def test_unsafe_hostnames_rejected(self):
        for h in ['finalvestige.com','www.finalvestige.com','localhost','127.0.0.1','::1',
                  'example.org.','*.example.org','internal','',None]:
            with self.subTest(h=h):
                with self.assertRaises(ValueError): _host(h)

    def test_invalid_axe_rejected_even_with_real_staging_url(self):
        u='https://approved-stage.example.org/apollo/'
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'mock.js'; path.write_bytes(b'window.axe={run:()=>({violations:[]})};')
            for extra in ({}, {'axe_js':path}, {'axe_js':path,'axe_sha256':'f'*64}):
                with self.assertRaises(ValueError): preflight(self.args(url=u,approved_host='approved-stage.example.org',**extra))

    def test_gallery_requires_explicit_minimum(self):
        with self.assertRaises(ValueError): preflight(self.args(url='https://finalvestige.com',approved_host='finalvestige.com',image_policy='gallery'))
        with tempfile.TemporaryDirectory() as temp:
            f=Path(temp)/'fake_axe.js'; f.write_bytes(b'// not real\n'*20000)
            import hashlib
            sha=hashlib.sha256(f.read_bytes()).hexdigest()
            a=self.args(url='https://approved-stage.example.org/',approved_host='approved-stage.example.org',
                        image_policy='gallery',minimum_images=0,axe_js=f,axe_sha256=sha)
            with self.assertRaises(ValueError): preflight(a)
            a.minimum_images=3
            self.assertEqual(preflight(a),'WORDPRESS_STAGING_CANDIDATE')

    def test_incomplete_or_browser_error_never_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            for complete in (False, True):
                r=save_receipt(out,'WORDPRESS_STAGING_CANDIDATE',[],[{'error':'TimeoutError'}],complete=complete)
                self.assertEqual(r['verdict'],'HOLD')

if __name__=='__main__':unittest.main()
