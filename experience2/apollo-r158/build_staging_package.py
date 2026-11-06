#!/usr/bin/env python3
"""Deterministic isolated Apollo Research Desk WP staging candidate, not a deployment."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

SOURCE = {
    'templates/ledger.html': ('experience2/apollo-r157/ledger_with_chronology_review.html', '67b612be3dfb385fd03e952a59e9ec5088c25a89821a3420a5f199326da57c83'),
    'assets/research-desk.js': ('experience2/apollo-r154/r153_source_ledger_compat.js', 'd6faa0f392b70563734603459320d00f968be911404afb265872766939b8ae4e'),
}
CSS = [
 'experience2/research-desk/assets/source-ledger.css',
 'experience2/apollo-r156/source_custody_review.css',
 'experience2/apollo-r154/r153_source_ledger_compat.css',
 'experience2/apollo-r157/chronology_rail.css',
]
# Byte-exact source identity. If an upstream branch rebases, an explicit review is required.
CSS_SHA256 = [
 '38676056e2aee5e3db285072bd847b5b5438832d76d9c451e4f56d27134ee291',
 '25da3b9b2e89eee3be15aaa3101350c56faf23ba8fa02496b12f4d4764271761',
 '3ed553aeba0a1fca64074945391fc21de44d131a67b87f730590f8d6338b2013',
 '5e7a0f723b2da874277cd6a23daa41f6ffd20f5fafbc874d77399bd3eb28e3d5',
]
STAMP=(1980,1,1,0,0,0)

def sha(data): return hashlib.sha256(data).hexdigest()

def build(repo, out):
    repo, out = Path(repo), Path(out)
    entries={}
    input_manifest={}
    for dest,(path,expected) in SOURCE.items():
        raw=(repo/path).read_bytes()
        assert sha(raw)==expected, f'upstream input SHA-256 changed: {path}: {sha(raw)}'
        entries[dest]=raw;input_manifest[path]=expected
    css_parts=[]
    for path,expected in zip(CSS,CSS_SHA256):
        raw=(repo/path).read_bytes()
        assert sha(raw)==expected, f'upstream CSS SHA-256 changed: {path}: {sha(raw)}'
        input_manifest[path]=expected
        css_parts.append(b'/* source: '+path.encode()+b' */\n'+raw+b'\n')
    entries['assets/research-desk.css']=b''.join(css_parts)
    stub=(repo/'experience2/apollo-r158/wordpress-staging-adapter.stub.php').read_text()
    for key,path in [('HTML','templates/ledger.html'),('CSS','assets/research-desk.css'),('JS','assets/research-desk.js')]:
        assert stub.count('@@'+key+'_SHA256@@')==1
        stub=stub.replace('@@'+key+'_SHA256@@',sha(entries[path]))
    entries['fv-apollo-research-desk.php']=stub.encode()
    manifest={'status':'STAGING_HOLD_NOT_LIVE','provenance':'Apollo R157 source-pinned staging package','upstream_sha256':input_manifest,
              'bundled_sha256':{k:sha(v) for k,v in sorted(entries.items())},
              'commercial_offer':'NONE_VERIFIED','media_rights':'NOT_CLEARED','axe':'NOT_EXECUTED_BY_BUILD'}
    entries['evidence/MANIFEST.json']=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
    out.mkdir(parents=True,exist_ok=True)
    zip_path=out/'fv-apollo-r158-wordpress-staging.zip'
    with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,raw in sorted(entries.items()):
            zi=zipfile.ZipInfo('fv-apollo-r158/'+name,STAMP)
            zi.compress_type=zipfile.ZIP_DEFLATED
            zi.external_attr=0o644<<16
            z.writestr(zi,raw,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    (out/'build_receipt.json').write_text(json.dumps({**manifest,'zip_sha256':sha(zip_path.read_bytes()),'zip_bytes':zip_path.stat().st_size},indent=2,sort_keys=True)+'\n')
    print(json.dumps({'zip_sha256':sha(zip_path.read_bytes()),'bytes':zip_path.stat().st_size,'paths':len(entries)},sort_keys=True))
    return zip_path

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();build(a.repo,a.out)
