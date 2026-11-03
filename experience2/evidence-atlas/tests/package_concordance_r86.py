#!/usr/bin/env python3
"""Deterministic R86 source + generated HTML review ZIP (never a deployable plugin)."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[3]
SOURCE=(
'experience2/evidence-atlas/tools/build_concordance_r86.py',
'experience2/evidence-atlas/tools/concordance_r86.css',
'experience2/evidence-atlas/tests/test_concordance_r86.py',
'experience2/evidence-atlas/tests/browser_concordance_r86.py',
'experience2/evidence-atlas/tests/package_concordance_r86.py',
'experience2/evidence-atlas/R86_CROSS_COMPONENT_CONCORDANCE_STAGING_HOLD.md',
'.github/workflows/ex2-apollo-r86-concordance.yml',
'experience2/research-desk/templates/ledger.html',
'experience2/evidence-atlas/build_atlas.py',
'experience2/evidence-atlas/atlas.css',
'experience2/evidence-atlas/atlas.js',
'experience2/evidence-atlas/tools/build_rights_board_r85.py',
'experience2/research-desk/sources/R37_PHOTO_CUSTODY_CROSSWALK.json',
'experience2/evidence-atlas/sources/R79_NASA_PAGE_AUDIT.json',
'experience2/evidence-atlas/sources/NASA_PAGE_RIGHTS_AUDIT_R55.json',
)
BUILT=('R86_EVIDENCE_CONCORDANCE.html','concordance_r86.css','R86_CONCORDANCE_RECEIPT.json')
def package(built,out):
    contents={}
    for path in SOURCE: contents['source/'+path]=(ROOT/path).read_bytes()
    for name in BUILT: contents['built/'+name]=(built/name).read_bytes()
    receipt=json.loads(contents['built/R86_CONCORDANCE_RECEIPT.json'])
    assert receipt['release']=='STAGING_HOLD'
    assert receipt['photo_rights_cleared']==0 and not receipt['approved_for_publication']
    contents['SHA256_MANIFEST.json']=(json.dumps({
        'schema':'fv.apollo.r86.deterministic-review.v1','release':'STAGING_HOLD',
        'not_deployable':True,
        'files_sha256':{k:hashlib.sha256(v).hexdigest() for k,v in sorted(contents.items())}
    },sort_keys=True,indent=2)+'\n').encode()
    out.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(out,'w',compression=ZIP_DEFLATED,compresslevel=9) as archive:
        for name in sorted(contents):
            info=ZipInfo(name,date_time=(1980,1,1,0,0,0))
            info.compress_type=ZIP_DEFLATED
            info.external_attr=0o100644<<16
            info.create_system=3
            archive.writestr(info,contents[name],compress_type=ZIP_DEFLATED,compresslevel=9)
    return hashlib.sha256(out.read_bytes()).hexdigest()
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--built',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    print('R86 deterministic ZIP SHA256',package(a.built,a.out))
