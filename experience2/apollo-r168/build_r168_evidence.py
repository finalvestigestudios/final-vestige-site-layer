"""Build deterministic R168 audit package; no network, CMS or merchant actions.

Run after test_wp_source_custody_gate; evidence is *controlled browser fixture*.
"""
from pathlib import Path
import hashlib
import json
import zipfile

HERE=Path(__file__).resolve().parent
OUT=HERE.parent/'Apollo_R168_Pinned_WP_Custody_High_Contrast_STAGING_HOLD.zip'
SOURCE = [
    'wp_source_custody_gate.py','archive-accessibility.r168.css',
    'test_wp_source_custody_gate.py','build_r168_evidence.py',
    'wp_block_pack.py','test_wp_block_pack.py','build_offline.py',
    'stage_patch.py','gallery-independent.css','gallery-independent.js',
    'gallery-fallback.css','gallery-fallback.js','gallery-fallback-flow.r167.css',
    'verified_gallery_excerpt.html','test_integrated_bridge.py',
]
BROWSER = [f'artifacts-r168/r168-{w}.png' for w in (320,360,390,768,1440,1920)] + [
    'artifacts-r168/r168-browser-receipt.json'
]

def build() -> str:
    data={}
    for name in SOURCE+BROWSER:
        p=HERE/name
        if not p.is_file(): raise FileNotFoundError('HOLD: required source/QA evidence missing: '+name)
        data[('source/' if name in SOURCE else '')+name]=p.read_bytes()
    data['MANIFEST_SHA256.json']=(json.dumps({
        'artifact_type':'CONTROLLED_CHROMIUM_R168_STAGING_HOLD',
        'wordPress_writes':0,'production_acceptance':False,
        'files':{name:hashlib.sha256(content).hexdigest() for name,content in sorted(data.items())},
    },indent=2,sort_keys=True)+'\n').encode()
    with zipfile.ZipFile(OUT,'w') as z:
        for name,content in sorted(data.items()):
            meta=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
            meta.compress_type=zipfile.ZIP_DEFLATED
            meta.external_attr=(0o100644<<16)
            z.writestr(meta,content,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return hashlib.sha256(OUT.read_bytes()).hexdigest()

if __name__=='__main__':
    print(json.dumps({'path':str(OUT),'sha256':build()},sort_keys=True))
