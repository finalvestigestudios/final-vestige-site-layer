#!/usr/bin/env python3
"""Board-claim compare contract; stdlib only; no image or atlas invention."""
import json, re, sys
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from render import render,validate
records=json.loads((ROOT/"records.json").read_text("utf8"))
custody=json.loads((ROOT/"custody.json").read_text("utf8"))
validate(records)
html=render(records,custody)
assert html==render(records,custody), "render not deterministic"
assert len(re.findall(r'<template data-ex2-compare-template="0[1-6]">',html))==6
assert html.count('<div data-ex2-compare-pane="a"')==1
assert html.count('<div data-ex2-compare-pane="b"')==1
assert html.count('data-ex2-compare-id="02"')==2
assert html.count('data-ex2-compare-id="05"')==2
assert html.count('<option value="02" selected>')==1
assert html.count('<option value="05" selected>')==1
assert 'data-ex2-compare-tools hidden' in html
assert 'Two claims. <em>Different kinds of proof.</em>' in html
assert all('href="#source-'+r['id']+'"' in html for r in records['records'])
assert all(r['rights'].startswith('link_only_') for r in records['records'])
assert all(x['geometry'] is None for x in records['atlas'])
assert not re.search(r'<img\b|<picture\b|<iframe\b|<canvas\b',html,re.I)
assert 'onchange=' not in html and 'onclick=' not in html
for c in custody['claims']:
    assert c['board_locator'].replace('&','&amp;') in html
    assert c['boundary'].replace('&','&amp;') in html
class IDs(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[]
    def handle_starttag(self,tag,attrs):
        val=dict(attrs).get('id')
        if val:self.ids.append(val)
p=IDs();p.feed(html)
assert len(set(p.ids))==len(p.ids), 'duplicate document IDs'
print('COMPARE_CONTRACT_PASS: six canonical templates, no-JS pair, claims, links, rights, geometry')
