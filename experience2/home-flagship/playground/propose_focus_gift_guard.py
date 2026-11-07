#!/usr/bin/env python3
"""Render a REVIEW-ONLY Focus-page script replacement; never writes WordPress.

Pass a locally exported PUBLIC page HTML file; this tool validates the exact
pinned existing inline script against #1415 source custody, changes that one
script in memory, and writes a separate local preview file. Fail closed on drift.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import re
import sys

EXPECTED_SOURCE_SHA256 = "f5b7a56cf46a17b350a6245684cc222d59ce4b7da62650515d208169f89426a7"
SCRIPT_RE = re.compile(r'<script\s+id=[\'\"]fvf-gift-v2[\'\"]\s*>(.*?)</script>', re.S | re.I)

def stage(source_html: str, new_js: str, pinned_script: str) -> str:
    if hashlib.sha256(pinned_script.encode()).hexdigest() != EXPECTED_SOURCE_SHA256:
        raise ValueError('Published script custody differs from pinned #1415 source; abort')
    matches = list(SCRIPT_RE.finditer(source_html))
    if len(matches) != 1:
        raise ValueError(f'Expected exactly one published gift script; found {len(matches)}')
    old = matches[0].group(1)
    if old != pinned_script:
        raise ValueError('Current exported HTML script does not match published source; abort')
    code_without_comments = re.sub(r'/\*.*?\*/|//[^\n]*', '', new_js, flags=re.S)
    if re.search(r'\b(?:URLSearchParams|location|fetch|XMLHttpRequest)\b', code_without_comments):
        raise ValueError('Refuse untrusted URL or network signals to subscriber UI')
    if '</script' in new_js.lower():
        raise ValueError('Refuse script tag termination inside candidate')
    return source_html[:matches[0].start()] + '<script id="fvf-gift-v3">' + new_js + '</script>' + source_html[matches[0].end():]

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--public-html-export',required=True,type=pathlib.Path)
    ap.add_argument('--pinned-fixture',required=True,type=pathlib.Path)
    ap.add_argument('--candidate-js',default=pathlib.Path(__file__).with_name('focus_gift_guard.js'),type=pathlib.Path)
    ap.add_argument('--out',required=True,type=pathlib.Path)
    args=ap.parse_args()
    if args.out.resolve() == args.public_html_export.resolve():
        ap.error('Output must not overwrite source')
    fixture=json.loads(args.pinned_fixture.read_text())
    if fixture['page_id'] != 1579:
        raise ValueError('Not WordPress public Focus Page 1579')
    content=stage(args.public_html_export.read_text(), args.candidate_js.read_text(),fixture['script'])
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(content)
    print(json.dumps({'status':'LOCAL_PREVIEW_ONLY','source_page_id':1579,'existing_script_sha256':EXPECTED_SOURCE_SHA256,'output_sha256':hashlib.sha256(content.encode()).hexdigest(),'output':str(args.out),'not_jetpack_verified':True},indent=2))
    return 0
if __name__=='__main__':
    sys.exit(main())
