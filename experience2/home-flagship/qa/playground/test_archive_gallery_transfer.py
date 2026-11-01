#!/usr/bin/env python3
"""Executable negative controls for a hidden/lazy three-case WordPress gallery."""
import hashlib
import unittest
from urllib.parse import urlsplit
from archive_gallery_transfer import audit_archive_gallery

HOST = 'http://127.0.0.1:8080'
DATA = {'apollo.webp':(1,1,1),'franklin.jpg':(1,1,1),'nypl.jpg':(1,1,1)}
SOURCE = {'apollo': 'apollo.webp','franklin': 'franklin.jpg','malbone': 'nypl.jpg'}

class AdmissionError(RuntimeError): pass

def must(c, msg):
    if not c: raise AdmissionError(msg)

class Response:
    def __init__(self, page, name):
        self.status=200 if not page.bad_http else 404
        self.url=HOST+'/media/'+name if not page.redirect else 'https://finalvestige.com/media/'+name
        self._body=(b'Z' if page.corrupt else name[:1].encode())
    def body(self):return self._body

class Request:
    def __init__(self,page):self.page=page
    def get(self,src,timeout):
        assert timeout==30000
        return Response(self.page,src.split('/')[-1])

class Locator:
    def __init__(self,page,kind,case=None):self.page,self.kind,self.case=page,kind,case
    def count(self):return 0 if self.page.missing==self.case else 1
    def all(self):return [object()]*self.page.count
    def is_visible(self):return self.kind=='button' or (self.page.active==self.case)
    def click(self):
        if self.kind=='button':self.page.active=self.case
        else:raise AssertionError('clicked non-button')
    def locator(self,q):
        if self.kind=='panel' and q=='img[data-fv-archive-img]':return Locator(self.page,'photo',self.case)
        raise AssertionError(q)
    def get_attribute(self,n):
        if n=='alt':return 'Accurate archival description' if not self.page.blank_alt else ' '
        if n=='srcset':return 'https://i0.wp.com/...' if self.page.bad_srcset else None
        raise AssertionError(n)
    def scroll_into_view_if_needed(self,timeout):
        if self.page.active!=self.case:raise AssertionError('lazy image not revealed')
        self.page.loaded.add(self.case)
    def evaluate(self,expression):
        if self.kind!='photo' or self.case not in self.page.loaded:raise AssertionError('unloaded')
        if 'currentSrc' in expression:return (HOST+'/media/'+SOURCE[self.case]) if not self.page.off_origin else 'https://finalvestige.com/media/'+SOURCE[self.case]
        if 'naturalWidth' in expression:return [1,1]
        raise AssertionError(expression)

class Page:
    def __init__(self):
        self.active='apollo';self.loaded=set();self.request=Request(self)
        self.count=3;self.missing=None;self.redirect=False;self.off_origin=False
        self.bad_srcset=False;self.blank_alt=False;self.corrupt=False;self.bad_http=False
    def locator(self,q):
        if q=='.fv-hf img':return Locator(self,'all')
        for c in SOURCE:
            if q==f'[data-fv-case-button="{c}"]':return Locator(self,'button',c)
            if q==f'[data-fv-case="{c}"]':return Locator(self,'panel',c)
        raise AssertionError('unknown selector '+q)
    def wait_for_function(self,expression,arg,timeout):
        if arg not in self.loaded:raise AssertionError('waited on lazy image before revealing')
        assert 'naturalWidth>0' in expression and timeout==30000

def verify(name,body,dims,sha):
    assert hashlib.sha256(body).hexdigest()==sha
    return {'bytes':len(body),'sha256':sha,'dimensions':dims}

class TransferTests(unittest.TestCase):
    def setUp(self):
        self.p=Page();self.sha={name:hashlib.sha256(name[:1].encode()).hexdigest() for name in DATA}
    def go(self):return audit_archive_gallery(self.p,('http','127.0.0.1:8080'),self.sha,DATA,must,verify)
    def test_hidden_lazy_panels_are_selected_and_scrolled_before_decode(self):
        out=self.go()
        self.assertEqual(self.p.loaded,{'apollo','franklin','malbone'})
        self.assertEqual(self.p.active,'apollo')
        self.assertEqual(len(out),3)
        self.assertTrue(all(x['transfer'].startswith('VISIBLE_CASE') for x in out.values()))
    def test_missing_case_image_or_duplicate_gallery_images_rejected(self):
        for c in (2,4):
            self.p.count=c
            with self.subTest(count=c),self.assertRaises(AdmissionError):self.go()
            self.p=Page()
        self.p.missing='malbone'
        with self.assertRaises(AdmissionError):self.go()
    def test_external_srcset_and_no_alt_rejected(self):
        self.p.bad_srcset=True
        with self.assertRaises(AdmissionError):self.go()
        self.p=Page();self.p.blank_alt=True
        with self.assertRaises(AdmissionError):self.go()
    def test_production_redirect_or_cross_origin_rejected(self):
        self.p.off_origin=True
        with self.assertRaises(AdmissionError):self.go()
        self.p=Page();self.p.redirect=True
        with self.assertRaises(AdmissionError):self.go()
    def test_bad_http_and_same_size_image_byte_mutation_rejected(self):
        self.p.bad_http=True
        with self.assertRaises(AdmissionError):self.go()
        self.p=Page();self.p.corrupt=True
        with self.assertRaises(AssertionError):self.go()
    def test_incomplete_trusted_image_identity_rejected(self):
        self.sha.pop('nypl.jpg')
        with self.assertRaises(AdmissionError):self.go()

if __name__=='__main__': unittest.main()
