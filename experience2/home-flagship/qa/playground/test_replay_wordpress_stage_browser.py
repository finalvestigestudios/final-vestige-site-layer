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


def mock_html(external_css=False, omit_margin=False, srcset=False, missing_control=False):
    margin = 71 if omit_margin else 72
    spans = ''.join(f'<span class="fv-margin-strip__item" style="--i:{i}">record {i}</span>' for i in range(margin))
    chapters = ''.join(f'<a href="#chapter-{i}">Chapter {i}</a>' for i in range(7))
    sections = ''.join(f'<section id="chapter-{i}">Evidence section {i}</section>' for i in range(7))
    cases = ''.join(f'<article data-fv-case="{name}"><img src="/media/c{i}.gif" '
                    + ('srcset="/media/c0.gif 2x" ' if srcset and i==0 else '')
                    + f'alt="Synthetic test image {i}"></article>'
                    for i,name in enumerate(('apollo', 'franklin', 'malbone')))
    css = 'https://unapproved.example/attack.css' if external_css else '/assets/style.css'
    controls = ("""<div class="fv-hf__studio-controls" hidden><button data-fv-direction-choice="museum">Museum</button><button data-fv-direction-choice="dossier">Dossier</button></div>
       <div data-fv-case-buttons hidden><button data-fv-case-button="apollo">Apollo</button><button data-fv-case-button="franklin">Franklin</button><button data-fv-case-button="malbone">Malbone</button></div>
       <div data-fv-chronicle-lens hidden><button data-fv-chronicle-view="addition">Addition</button><button data-fv-chronicle-view="original">Original</button></div>
       <div data-fv-observer-controls hidden><button data-fv-observer-switch="b">Frame B</button><button data-fv-observer-switch="a">Frame A</button></div>""")
    if missing_control:
        controls = controls.replace('data-fv-direction-choice="museum"', 'data-fv-unapproved="museum"')
    return (f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{css}"></head><body>'
            + f'<main class="fv-hf" data-fv-home-flagship data-fv-direction="dossier"><div class="fv-margin-strip">{spans}</div>'
            + '<section class="fv-hf__opening"><div class="fv-hf__folio-arrival">Test folio</div></section>'
            + f'<nav class="fv-hf__chapter-nav">{chapters}</nav>{sections}'
            + '<div data-fv-subscriptions-local-only="true">NO EMAIL COLLECTION</div>'
            + '<a href="/focus/">Focus</a><a href="/focus/">Book</a>'
            + controls + '<section class="fv-hf__chronicle" data-fv-chronicle-mode="record"><div class="fv-hf__chronicle-paper">'
            + '<article class="fv-hf__chronicle-entry fv-hf__chronicle-entry--first">Original test entry</article>'
            + '<article class="fv-hf__chronicle-entry fv-hf__chronicle-entry--second">Later test addition</article>'
            + '</div></section>'
            + '<div data-fv-observer-frame="a">Observer A</div><div data-fv-observer-frame="b">Observer B</div>'
            + cases + '</main><script src="/assets/flagship.js"></script></body></html>')

# Test-only state transitions: never assert synthetic history or production functionality.
TEST_JS = r"""const root=document.querySelector('[data-fv-home-flagship]');
for(const selector of ['.fv-hf__studio-controls','[data-fv-case-buttons]','[data-fv-chronicle-lens]','[data-fv-observer-controls]'])
 document.querySelector(selector).hidden=false;
const ids=['apollo','franklin','malbone'];
function selectCase(which){for(const p of document.querySelectorAll('[data-fv-case]'))p.hidden=p.dataset.fvCase!==which;}
selectCase('apollo');
function observer(which){for(const n of document.querySelectorAll('[data-fv-observer-frame]'))n.hidden=n.dataset.fvObserverFrame!==which;}
observer('a');
for(const b of document.querySelectorAll('[data-fv-direction-choice]'))b.addEventListener('click',()=>root.dataset.fvDirection=b.dataset.fvDirectionChoice);
for(const b of document.querySelectorAll('[data-fv-case-button]')){
 b.addEventListener('click',()=>selectCase(b.dataset.fvCaseButton));
 b.addEventListener('keydown',e=>{const i=ids.indexOf(b.dataset.fvCaseButton);let next;
  if(e.key==='ArrowRight')next=ids[(i+1)%3];if(e.key==='Home')next=ids[0];
  if(next){e.preventDefault();selectCase(next);document.querySelector('[data-fv-case-button="'+next+'"]').focus();}
 });
}
for(const b of document.querySelectorAll('[data-fv-chronicle-view]'))b.addEventListener('click',()=>document.querySelector('.fv-hf__chronicle').dataset.fvChronicleMode=b.dataset.fvChronicleView);
for(const b of document.querySelectorAll('[data-fv-observer-switch]'))b.addEventListener('click',()=>observer(b.dataset.fvObserverSwitch));
"""


# Styling is deliberately synthetic but must make the two feature transitions
# visibly real: a DOM state change alone must no longer earn a test PASS.
TEST_CSS = r"""body{margin:0}main{max-width:100%;overflow-wrap:anywhere}
.fv-hf__opening{background:#182826;padding:32px}
.fv-hf__folio-arrival{background:#40332b;border:4px solid #cfb27e;padding:38px}
.fv-hf[data-fv-direction="museum"] .fv-hf__opening{background:#75432e}
.fv-hf[data-fv-direction="museum"] .fv-hf__folio-arrival{background:#c4a77f}
.fv-hf__chronicle-paper{display:grid;grid-template-columns:1fr 1fr}
.fv-hf__chronicle-entry{padding:22px;border:2px solid #342b20}
.fv-hf__chronicle[data-fv-chronicle-mode="addition"] .fv-hf__chronicle-entry--first{display:none}
.fv-hf__chronicle[data-fv-chronicle-mode="original"] .fv-hf__chronicle-entry--second{display:none}
"""


class ProbeServer:
    def __init__(self):
        self.data = {'/': (mock_html().encode(), 'text/html'),
                     '/assets/style.css': (TEST_CSS.encode(), 'text/css'),
                     '/assets/flagship.js': (TEST_JS.encode(), 'text/javascript'),
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
