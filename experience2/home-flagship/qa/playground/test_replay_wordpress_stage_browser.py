"""Controlled local HTTP and actual Chromium: never represents a WordPress installation."""
import asyncio
import base64
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.parse import urlsplit
from unittest.mock import patch

from replay_wordpress_stage_browser import Capture, Hold, browser_review, passing

# One-pixel GIF, strictly synthetic. No historical archival image is supplied.
GIF = base64.b64decode('R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==')


def mock_html(external_css=False, omit_margin=False, srcset=False):
    margin = 71 if omit_margin else 72
    spans = ''.join(f'<span class="fv-margin-strip__item" style="--i:{i}">record {i}</span>' for i in range(margin))
    chapters = ''.join(f'<a href="#chapter-{i}">Chapter {i}</a>' for i in range(7))
    sections = ''.join(f'<section id="chapter-{i}">Evidence section {i}</section>' for i in range(7))
    cases = ''.join(f'<article data-fv-case="c{i}"><img src="/media/c{i}.gif" '
                    + ('srcset="/media/c0.gif 2x" ' if srcset and i==0 else '')
                    + f'alt="Synthetic test image {i}"></article>' for i in range(3))
    css = 'https://unapproved.example/attack.css' if external_css else '/assets/style.css'
    return (f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{css}"></head><body>'
            + f'<main data-fv-home-flagship><div class="fv-margin-strip">{spans}</div>'
            + f'<nav class="fv-hf__chapter-nav">{chapters}</nav>{sections}'
            + '<div data-fv-subscriptions-local-only="true">NO EMAIL COLLECTION</div>'
            + '<a href="/focus/">Focus</a><a href="/focus/">Book</a>'
            + cases + '</main><script src="/assets/flagship.js"></script></body></html>')


class ProbeServer:
    def __init__(self):
        self.data = {'/': (mock_html().encode(), 'text/html'),
                     '/assets/style.css': (b'body{margin:0}main{max-width:100%;overflow-wrap:anywhere}', 'text/css'),
                     '/assets/flagship.js': (b'document.documentElement.dataset.fvTest="executed";', 'text/javascript'),
                     **{f'/media/c{i}.gif': (GIF,'image/gif') for i in range(3)}}
        root = self
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                path=urlsplit(self.path).path
                if path == '/redirect':
                    self.send_response(302);self.send_header('Location','/assets/style.css');self.end_headers();return
                if path not in root.data:
                    self.send_response(404);self.end_headers();return
                data, mime=root.data[path]
                self.send_response(200)
                self.send_header('Content-Type',mime)
                self.end_headers()
                self.wfile.write(data)
            def log_message(self,*args):pass
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
    def __enter__(self):
        self.thread.start()
        self.url=f'http://127.0.0.1:{self.server.server_port}'
        self.manifest={'images':{f'{self.url}/media/c{i}.gif':{
            'sha256':hashlib.sha256(GIF).hexdigest(), 'bytes':len(GIF)} for i in range(3)}}
        return self
    def __exit__(self,*args):
        self.server.shutdown();self.server.server_close();self.thread.join()


class HttpReplayTests(unittest.TestCase):
    def test_actual_local_http_capture_then_real_chromium_seven_widths_and_no_js(self):
        with ProbeServer() as s, tempfile.TemporaryDirectory() as temp:
            html, receipt=Capture(s.url,s.manifest).assemble()
            self.assertEqual(receipt['archival_images_verified'],3)
            self.assertEqual(receipt['scripts'],1)
            self.assertEqual(receipt['stylesheets'],1)
            self.assertTrue(all('sha256' in entry for entry in receipt['http_resources']))
            browser,checks=asyncio.run(browser_review(html,Path(temp),'/usr/bin/chromium'))
            self.assertTrue(passing(checks),checks)
            self.assertEqual(len([k for k in checks if k.isdigit()]),7)
            self.assertEqual(checks['no_js']['all_three_cases_visible'],True)
            self.assertTrue((Path(temp)/'wp-http-replay-1440.png').is_file())
            self.assertFalse('https://unapproved.example' in html)

    def test_no_external_stylesheets(self):
        with ProbeServer() as s:
            s.data['/']=(mock_html(external_css=True).encode(),'text/html')
            with self.assertRaises(Hold): Capture(s.url,s.manifest).assemble()

    def test_missing_margin_fails(self):
        with ProbeServer() as s:
            s.data['/']=(mock_html(omit_margin=True).encode(),'text/html')
            with self.assertRaisesRegex(Hold,'72 preserved'): Capture(s.url,s.manifest).assemble()

    def test_wrong_image_digest_same_byte_count_fails(self):
        with ProbeServer() as s:
            wrong=bytearray(GIF);wrong[10]^=1
            s.data['/media/c1.gif']=(bytes(wrong),'image/gif')
            with self.assertRaisesRegex(Hold,'fingerprint'): Capture(s.url,s.manifest).assemble()

    def test_srcset_fails_closed_instead_of_claiming_archive_custody(self):
        with ProbeServer() as s:
            s.data['/']=(mock_html(srcset=True).encode(),'text/html')
            with self.assertRaisesRegex(Hold,'srcset'):Capture(s.url,s.manifest).assemble()

    def test_redirect_and_public_url_rejected(self):
        with ProbeServer() as s:
            with self.assertRaises(Hold): Capture(s.url,s.manifest).get('/redirect')
            with self.assertRaises(Hold): Capture(s.url,s.manifest).get('https://finalvestige.com/')
            with self.assertRaises(Hold): Capture('http://example.com',s.manifest)

    def test_missing_approved_exhibit_fails(self):
        with ProbeServer() as s:
            s.manifest['images'].pop(next(iter(s.manifest['images'])))
            with self.assertRaises(Hold):Capture(s.url,s.manifest).assemble()


if __name__=='__main__': unittest.main()
