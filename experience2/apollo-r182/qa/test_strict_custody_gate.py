"""R181 security and attribution safeguards; no outbound network."""
import asyncio
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from strict_custody_gate import approved_url, _host, preflight, save_receipt

from strict_custody_gate import custody_contract, R182_LINKS, R182_PHOTOS, R182_RESEARCH, R182_IDS, R182_DATES

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

    def test_exact_source_ledger_detects_same_domain_tamper(self):
        cards=[]
        for i in range(6):
            txt=f"Source custody: {R182_IDS[i]} is not the primary source. {R182_DATES[i]}. Media use in a paid product: not cleared."
            if i==0: txt+=' Catalog identification not verified. NASA does not confirm this number.'
            if i==4: txt+=' The photograph cannot identify the precise ignition source.'
            if i in (3,5): txt+=' 2017 exhibit does not depict the 1967 fire.'
            cards.append({'id':f'fv-ex2-ledger-apollo1-record-{i+1:02}','text':txt,
                          'links':[R182_PHOTOS[i],R182_RESEARCH[i]]})
        d={'records':cards,'links':list(R182_LINKS),'forbidden':0}
        self.assertTrue(all(custody_contract(d).values()))
        import copy
        for key, mutate in [
            ('same NASA host wrong photo',lambda x:x['links'].__setitem__(0,'https://www.nasa.gov/image-detail/unrelated/')),
            ('photo link inside card replaced',lambda x:x['records'][0]['links'].__setitem__(0,R182_PHOTOS[1])),
            ('source rights cleared without review',lambda x:x['records'][2].__setitem__('text',x['records'][2]['text'].replace('not cleared','cleared'))),
            ('unverified catalog claim rewritten',lambda x:x['records'][0].__setitem__('text',x['records'][0]['text'].replace('not verified','verified'))),
            ('post-fire photo misdated',lambda x:x['records'][4].__setitem__('text',x['records'][4]['text'].replace('1967-01-28','1967-01-27'))),
            ('geo pin added',lambda x:x.__setitem__('forbidden',1)),
            ('buy link added',lambda x:x['links'].append('https://www.payhip.com/unreviewed')),
        ]:
            with self.subTest(key=key):
                modified=copy.deepcopy(d);mutate(modified)
                self.assertFalse(all(custody_contract(modified).values()))

if __name__=='__main__':unittest.main()
