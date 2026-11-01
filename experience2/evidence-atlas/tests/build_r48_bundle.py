#!/usr/bin/env python3
"""Deterministic, staging-HOLD Apollo R48 review archive, no network or deploy."""
from pathlib import Path
import argparse,hashlib,json,sys,tempfile,zipfile
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import build_atlas,build_wordpress_stage

def build(out:Path,qa:Path)->dict:
    if not (qa/'R48_BROWSER_RECEIPT.json').is_file():
        raise ValueError('Require executed browser receipt; no invented QA evidence')
    receipt=json.loads((qa/'R48_BROWSER_RECEIPT.json').read_text())
    if len(receipt.get('tests',[]))!=19 or not all(row.get('pass') for row in receipt['tests']):
        raise ValueError('Require actual 19/19 Chromium QA receipt')
    if set(receipt.get('screenshots',{})) != {'390','1440'}:
        raise ValueError('Require reproducible mobile and desktop screenshots')
    files={}
    for f in sorted(HERE.rglob('*')):
        if f.is_file() and '__pycache__' not in f.parts and f.suffix in {'.md','.py','.js','.css','.php'}:
            files['experience2/evidence-atlas/'+str(f.relative_to(HERE))]=f.read_bytes()
    crosswalk=HERE.parent/'research-desk/sources/R37_PHOTO_CUSTODY_CROSSWALK.json'
    if build_atlas.git_blob(crosswalk.read_bytes()) != build_atlas.EXPECTED_BLOB:
        raise ValueError('Unreviewed R37 source ledger')
    files['experience2/research-desk/sources/'+crosswalk.name]=crosswalk.read_bytes()
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp)
        build_atlas.build(root/'preview')
        build_wordpress_stage.build(root/'wordpress')
        for f in sorted(root.rglob('*')):
            if f.is_file():files['compiled/'+str(f.relative_to(root))]=f.read_bytes()
    for f in sorted(qa.glob('*')):
        if f.is_file() and (f.suffix=='.png' or f.name in {'R48_BROWSER_RECEIPT.json','probe-390.txt','R38_SOURCE_PARITY_READONLY.json'}):
            files['qa/'+f.name]=f.read_bytes()
    manifest={'schema':'fv.ex2.apollo.r48.bundle.v1','release':'STAGING_HOLD',
       'exact_custody_git_blob':build_atlas.EXPECTED_BLOB,
       'axe_core':'NOT_AVAILABLE_NOT_EXECUTED','navigated_wordpress':'NOT_TESTED',
       'hosted_CWV':'NOT_MEASURED','photo_rights':'6 UNREVIEWED',
       'sha256':{name:hashlib.sha256(data).hexdigest() for name,data in sorted(files.items())}}
    files['SHA256_MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
    out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644<<16
            z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(out) as z:
        assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in manifest['sha256'].items())
    return {'path':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
            'verified_entries':len(manifest['sha256']),'release':'STAGING_HOLD'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--qa',type=Path,required=True);a=p.parse_args()
    print(json.dumps(build(a.output,a.qa),sort_keys=True,indent=2))
