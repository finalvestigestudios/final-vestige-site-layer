#!/usr/bin/env python3
"""Adversarial Playwright image-event handoff tests (no live stage claims)."""
import unittest
from browser_consumed_media import BrowserEvidencePage, BrowserMediaAdmissionClosed
from archive_gallery_transfer import audit_archive_gallery
from test_archive_gallery_transfer import Page, DATA, must, verify, AdmissionError, SOURCE, HOST

MIME={'apollo.webp':'image/webp','franklin.jpg':'image/jpeg','nypl.jpg':'image/jpeg'}
class BrowserResponse:
    def __init__(self, page, case):
        name=SOURCE[case]
        self.url=HOST+'/media/'+name
        self.status=404 if page.bad_http else 200
        self.headers={'content-type':'text/html' if page.bad_mime else MIME[name]}
        self.from_service_worker=page.service_worker
        self.request=type('RequestEvent',(),{
            'url':self.url,'resource_type':'document' if page.bad_type else 'image',
            'redirected_from':object() if page.redirect else None})()
        self.raw=b'Z' if page.browser_corrupt else name[:1].encode()
        self.finished_called=False
    def finished(self):self.finished_called=True
    def body(self):
        assert self.finished_called
        return self.raw
class BrowserPage(Page):
    def __init__(self):
        super().__init__()
        self.events=[];self.bad_mime=False;self.bad_type=False;self.service_worker=False
        self.no_event=False;self.duplicate_event=False;self.browser_corrupt=False
        # Independent HTTP client is intentionally unusable; there must be NO second GET.
        self.request.get=lambda *args,**kwargs: (_ for _ in ()).throw(
            AssertionError('unapproved second network request'))
    def wait_for_function(self,expression,arg,timeout):
        super().wait_for_function(expression,arg,timeout)
        if not self.no_event:
            event=BrowserResponse(self,arg)
            self.events.append(event)
            if self.duplicate_event:self.events.append(event)
class Tests(unittest.TestCase):
    def setUp(self):
        import hashlib
        self.page=BrowserPage()
        self.identities={name:hashlib.sha256(name[:1].encode()).hexdigest() for name in DATA}
    def go(self):
        p=BrowserEvidencePage(self.page,self.page.events,('http','127.0.0.1:8080'))
        return audit_archive_gallery(p,('http','127.0.0.1:8080'),
                                     self.identities,DATA,must,verify)
    def test_three_browser_loaded_lazy_case_bodies_pass_without_secondary_get(self):
        self.assertEqual(len(self.go()),3)
        self.assertEqual(self.page.active,'apollo')
        self.assertEqual(self.page.loaded,set(SOURCE))
        self.assertTrue(all(r.finished_called for r in self.page.events))
    def test_browser_bytes_changed_but_independent_get_could_match(self):
        self.page.browser_corrupt=True
        with self.assertRaises(AssertionError):self.go()
    def test_absent_or_duplicate_browser_image_events_fail_closed(self):
        for mode in ('no_event','duplicate_event'):
            self.page=BrowserPage();setattr(self.page,mode,True)
            with self.subTest(mode=mode),self.assertRaises(BrowserMediaAdmissionClosed):self.go()
    def test_mime_http_resource_type_controls_fail_closed(self):
        for mode in ('bad_mime','bad_http','bad_type'):
            self.page=BrowserPage();setattr(self.page,mode,True)
            with self.subTest(mode=mode),self.assertRaises(BrowserMediaAdmissionClosed):self.go()
    def test_redirect_or_service_worker_substitution_fail_closed(self):
        for mode in ('redirect','service_worker'):
            self.page=BrowserPage();setattr(self.page,mode,True)
            with self.subTest(mode=mode),self.assertRaises(BrowserMediaAdmissionClosed):self.go()
    def test_external_origin_filename_query_and_null_ledger_fail_closed(self):
        p=BrowserEvidencePage(self.page,self.page.events,('http','127.0.0.1:8080'))
        for src in ('https://finalvestige.com/media/apollo.webp',
                    HOST+'/media/other.jpg',HOST+'/media/apollo.webp?x=1'):
            with self.subTest(src=src),self.assertRaises(BrowserMediaAdmissionClosed):p.request.get(src)
        with self.assertRaises(BrowserMediaAdmissionClosed):
            BrowserEvidencePage(self.page,None,('http','127.0.0.1:8080'))
if __name__=='__main__':unittest.main()
