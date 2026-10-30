#!/usr/bin/env python3
"""Deterministic build and source-custody guard. No network or dependencies."""
import hashlib
import json
import pathlib
import subprocess
import sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
records=json.loads((ROOT/'records.json').read_text(encoding='utf-8'))
assert len(records['records'])==6, 'Expected six exact NASA source records'
assert len(records['atlas'])==6, 'Expected six curated published posts'
assert all(row['rights'].startswith('link_only') and row['image_url'].startswith('https://www.nasa.gov/image-detail/') for row in records['records']), 'Unsafe image reuse or source'
assert all(item['geometry'] is None and item['location_review']=='unverified' for item in records['atlas']), 'Unreviewed pins prohibited'
results=[]
for i in range(2):
    subprocess.run([sys.executable,str(ROOT/'render.py')],cwd=ROOT,check=True,capture_output=True,text=True)
    output=(ROOT/'index.html').read_bytes()
    assert output.count(b' data-ex2-stage ')==6, 'Wrong chronology record count'
    assert output.count(b'data-ex2-gallery-item')==6, 'Wrong image record count'
    assert b'<img ' not in output, 'No embedded NASA image bytes authorized'
    results.append(hashlib.sha256(output).hexdigest())
assert results[0]==results[1], 'Non-deterministic render'
print('DETERMINISTIC_BUILD_PASS',results[0])
