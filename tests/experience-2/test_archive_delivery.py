#!/usr/bin/env python3
"""Offline Chromium for real response parsing, selection and fail-closed rules.
Synthetic images and data, explicitly NOT live host/network evidence.
"""
import io
import json
import unittest
import sys
import shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools/experience-2"))
from PIL import Image
from playwright.sync_api import sync_playwright
from verify_live_archive_delivery import probe, classify, asset_for, safe_url, ASSETS

def img_bytes(fmt):
    im=Image.new('RGB',(320,240),(160,125,90)); f=io.BytesIO(); im.save(f,format=fmt);return f.getvalue()

GOOD = {
    'apollo':{'body':img_bytes('WEBP'),'mime':'image/webp'},
    'franklin':{'body':img_bytes('JPEG'),'mime':'image/jpeg'},
    'malbone':{'body':img_bytes('JPEG'),'mime':'image/jpeg'}
}

def html_fixture(bad=None):
    bad=bad or {}
    parts=[]
    for key,file in ASSETS.items():
        alt='' if bad.get('no_alt')==key else 'Historical source image; its meaning and limits explained in accompanying text.'
        src=f'https://finalvestige.com/wp-content/uploads/2026/08/{file}'
        # Malbone uses the Jetpack image CDN in the actual published Page 6.
        if key=='malbone': src=f'https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/{file}?fit=1024%2C692&ssl=1'
        parts.append(f'<article class="fv-hf__case" data-fv-case="{key}"><img data-fv-archive-img width="320" height="240" loading="lazy" src="{src}" alt="{alt}" srcset="{src} 1024w" sizes="100vw"><details><summary>Sources and limits</summary><p>Not a complete reconstruction.</p></details></article>')
    return '<!doctype html><meta charset="utf-8"><title>NONPRODUCTION SYNTHETIC fixture</title><main>'+''.join(parts)+'</main>'

class Unit(unittest.TestCase):
    def test_host_allowlist(self):
        self.assertEqual(asset_for('https://i0.wp.com/finalvestige.com/wp-content/uploads/Franklinexpeditionnote.jpg?fit=768'), 'franklin')
        self.assertIsNone(asset_for('https://evil.example/Franklinexpeditionnote.jpg'))
        self.assertEqual(safe_url('https://name:password@finalvestige.com/a.png?token=secret&fit=768%2C519#x'),'finalvestige.com/a.png?fit=768%2C519')
    def test_classifier_fail_closed(self):
        dom={'exists':True,'alt':'source description','naturalWidth':320,'naturalHeight':240,'complete':True,'display':'block','visibility':'visible','rectWidth':320}
        record={'status':200,'mime':'image/webp','decoded_body_bytes':120,'wire_body_bytes':110}
        self.assertEqual(classify(record,dom),[])
        for field,value,flag in [('status',404,'HTTP_NOT_200'),('mime','text/html','NON_IMAGE_CONTENT_TYPE'),('decoded_body_bytes',0,'EMPTY_RESPONSE_BODY'),('wire_body_bytes',None,'WIRE_BYTES_NOT_MEASURED'),('wire_body_bytes',0,'WIRE_BYTES_NOT_MEASURED')]:
            r=dict(record);r[field]=value
            self.assertIn(flag,classify(r,dom))
        self.assertIn('NETWORK_RESPONSE_NOT_OBSERVED',classify(None,dom))
        self.assertIn('IMAGE_NOT_DECODED',classify(record,{**dom,'naturalWidth':0}))
        self.assertIn('ALT_MISSING',classify(record,{**dom,'alt':''}))
        self.assertIn('DOM_IMAGE_MISSING',classify(record,{'exists':False}))

    def test_playwright_fixture(self):
        checks=[]
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox'])
            for width in (320,390,768,1440,1920):
                for dpr in (1,2):
                    fixture={'html':html_fixture(),'responses':GOOD}
                    r=probe(browser,width,dpr,True,'https://finalvestige.com/',fixture=fixture)
                    checks.append((width,dpr,'healthy',r['pass']))
                    self.assertTrue(r['pass'],json.dumps(r)[:2500])
                    for key in ASSETS:
                        it=r['assets'][key]
                        self.assertEqual(it['result'],'PASS')
                        self.assertTrue(it['response']['decoded_body_bytes']>0)
                        self.assertIsNotNone(it['response']['wire_body_bytes'])
                        self.assertNotIn('token=',it['response']['url'])
            # Negative cases (real Chromium request events with intercepted responses):
            cases=[('404',{'franklin':{**GOOD['franklin'],'status':404}},None,'HTTP_NOT_200'),
                   ('bad_mime',{'apollo':{**GOOD['apollo'],'mime':'text/html'}},None,'NON_IMAGE_CONTENT_TYPE'),
                   ('empty_body',{'malbone':{**GOOD['malbone'],'body':b''}},None,'IMAGE_NOT_DECODED'),
                   ('missing_alt',{},'apollo','ALT_MISSING'),
                   ('forbidden',{'apollo':{**GOOD['apollo'],'status':403}},None,'HTTP_NOT_200'),
                   ('tiny_image',{'franklin':{'body':img_bytes('JPEG')[:0], 'mime':'image/jpeg'}},None,'IMAGE_NOT_DECODED')]
            for label,replacements,alt_case,flag in cases:
                fx={'html':html_fixture({'no_alt':alt_case} if alt_case else None),
                    'responses':{k:replacements.get(k,v) for k,v in GOOD.items()}}
                result=probe(browser,390,1,True,'https://finalvestige.com/',fixture=fx)
                checks.append((label,result['pass']))
                self.assertFalse(result['pass'],label)
                self.assertTrue(any(flag in v['errors'] for v in result['assets'].values()),json.dumps(result)[:2000])
            browser.close()
        print('CHROMIUM_FIXTURE_RECEIPT '+json.dumps({'synthetic_positive':10,'synthetic_negative':6,'checks':checks}))

if __name__=='__main__': unittest.main(verbosity=2)
