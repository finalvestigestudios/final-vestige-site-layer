#!/usr/bin/env python3
"""Deterministic source+QA snapshot ZIP; does not assert reproducible browser timings."""
import hashlib, json, os, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
SRC=ROOT/'experience2'
OUT=ROOT/'Apollo_R357_Evidence.zip'
SOURCES=[
'apollo-r339/assets/chronology-rail.css','apollo-r339/chronology-rail.php',
'apollo-r340/apollo-accession-gallery.php','apollo-r340/assets/accession-gallery.css',
'apollo-r345/evidence-plate.css','apollo-r345/evidence-plate.php',
'apollo-r347/assets/source-index.css','apollo-r347/assets/source-index.js','apollo-r347/source-index.php',
'apollo-r348/assets/source-custody.css','apollo-r348/source-custody.php',
'apollo-r349/source-policy.php','apollo-r350/integrity.php',
'apollo-r355/postfire-ledger.css','apollo-r355/postfire-ledger.php',
'apollo-r354/qa/wp_contract.php','apollo-r354/qa/browser_gate.py',
'apollo-r355/qa/wp_contract.php','apollo-r355/qa/browser_gate.py',
'apollo-r356/asset-bridge.php','apollo-r356/assets/print-proof.css',
'apollo-r356/qa/wp_contract.php','apollo-r356/qa/browser_gate.py','apollo-r357/template-asset-bridge.php','apollo-r357/README.md','apollo-r357/qa/wp_contract.php','apollo-r357/qa/browser_gate.py','apollo-r357/qa/build_evidence.py']
FILES=[SRC/name for name in SOURCES] + sorted((SRC/'apollo-r357/QA').rglob('*'))
FILES=[p for p in FILES if p.is_file()]
MANIFEST={'scope':'Local PHP fixture source and actual Chromium QA, not installed WordPress or production',
 'head_sha':os.environ.get('APOLLO_R357_HEAD_SHA','NOT_SET'),
 'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in FILES}}
manifest=json.dumps(MANIFEST,indent=2,sort_keys=True).encode()+b'\n'
items={str(p.relative_to(ROOT)):p.read_bytes() for p in FILES}
items['R357_MANIFEST.json']=manifest
def build(path):
 with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,data in sorted(items.items()):
   info=zipfile.ZipInfo(name,(1980,1,1,0,0,0))
   info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
   z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
build(OUT)
other=OUT.with_suffix('.repeat.zip');build(other)
assert OUT.read_bytes()==other.read_bytes(),'not byte-identical'
other.unlink()
print(json.dumps({'archive':str(OUT),'files':len(items),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'byte_identical_rebuild':True},indent=2))
