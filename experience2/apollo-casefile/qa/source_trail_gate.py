#!/usr/bin/env python3
"""Deterministic Apollo 1 custody/export contract: no external packages."""
import csv
import io
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from render import SOURCE_FIELDS, export_rows, export_assets, render, validate
manifest=json.loads((ROOT/'records.json').read_text(encoding='utf8'))
custody=json.loads((ROOT/'custody.json').read_text(encoding='utf8'))
validate(manifest)
rows=export_rows(manifest,custody)
assert len(rows)==6 and [r['claim_id'] for r in rows]==[f'{i:02}' for i in range(1,7)]
assert all(r['geometry']=='not_assigned' and r['media_status'].startswith('link_only_') for r in rows)
assert all(r['board_locator'] and r['evidence_boundary'] and r['image_evidence_limit'] for r in rows)
assert rows[2]['board_locator'].startswith('Part V, Data Analysis')
assert rows[3]['board_locator'].startswith('Part V, Data Analysis')
assert rows[-1]['later_response_url'].startswith('https://www.nasa.gov/')
assert all(not r['later_response_url'] for r in rows[:-1])
assert all(x['geometry'] is None for x in manifest['atlas'])
assert custody['usage_policy'].endswith('/images-and-media/')
export_assets(manifest,custody)
csv_rows=list(csv.DictReader(io.StringIO((ROOT/'evidence-export.csv').read_text(encoding='utf8'))))
assert csv_rows==rows
assert list(csv_rows[0])==SOURCE_FIELDS
j=json.loads((ROOT/'evidence-export.json').read_text(encoding='utf8'))
assert j['records']==rows and j['not_a_rights_clearance'] and j['no_geographic_coordinates']
html=render(manifest,custody)
assert html==(ROOT/'index.html').read_text(encoding='utf8')
assert html.count('href="evidence-export.csv"')==1 and html.count('href="evidence-export.json"')==1
assert len(re.findall(r'<details class="ex2-source" id="source-0[1-6]"',html))==6
assert len(re.findall(r'<li class="ex2-ledger__card" id="custody-0[1-6]" tabindex="-1"',html))==6
assert not re.search(r'<img\b|<picture\b|<iframe\b|<canvas\b',html,re.I)
print('SOURCE_TRAIL_GATE_PASS: six custodial claims, two deterministic exports, six drawers, no image bytes or geolocation')
