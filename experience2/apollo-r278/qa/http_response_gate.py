#!/usr/bin/env python3
"""Actual PHP loopback HTTP response/header gate via urllib. Not a browser CSP test."""
from pathlib import Path
from contextlib import closing
import socket,subprocess,time
from urllib.request import urlopen
from urllib.error import URLError,HTTPError
HERE=Path(__file__).resolve().parent
with socket.socket() as s:
  s.bind(('127.0.0.1',0));port=s.getsockname()[1]
proc=subprocess.Popen(['php','-S',f'127.0.0.1:{port}',str(HERE/'http_router.php')],cwd=HERE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
base=f'http://127.0.0.1:{port}'
try:
  for _ in range(100):
    try:
      with closing(urlopen(base+'/atlas',timeout=.2)) as r:
        html=r.read().decode();csp=r.headers.get('Content-Security-Policy','')
      break
    except URLError:time.sleep(.04)
  else:raise AssertionError('PHP server failed')
  assert "script-src 'none'" in csp and "style-src 'self'" in csp
  assert html.count('data-fv-review-ready="false"')==2
  assert html.count('href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/"')==4
  assert html.count('href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"')==2
  assert html.count('<link rel="stylesheet" href="/assets/review-custody.css">')==1
  assert '<script' not in html and 'merchant.invalid' not in html
  with closing(urlopen(base+'/assets/review-custody.css',timeout=2)) as r:
    assert r.status==200 and r.headers.get_content_type()=='text/css'
    assert '.fv-r273__disclosure' in r.read().decode()
  with closing(urlopen(base+'/atlas?missing_css=1',timeout=2)) as r:
    assert '<link rel="stylesheet" href="/assets/missing.css">' in r.read().decode()
  try:urlopen(base+'/assets/missing.css',timeout=2)
  except HTTPError as e:assert e.code==404
  else:raise AssertionError('Missing CSS must 404')
  print('R278 PHP HTTP/CSP header gate 6/6 PASS; Python client only')
finally:
  proc.terminate()
  try:proc.wait(timeout=3)
  except subprocess.TimeoutExpired:proc.kill()
