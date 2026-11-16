#!/usr/bin/env python3
"""Reproducible, fail-closed candidate ZIP for approved *offline* staging review.
No network calls, WordPress writes, GitHub mutations, installation or activation.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
SOURCES={
 'templates/ledger.html':('research','templates/ledger.html','403d128c57b9bc82dac7c619651689070edef86c'),
 'assets/source-ledger.css':('research','assets/source-ledger.css','b8cf00afeceba115a9e9d19044fc11dcf2890cbe'),
 'assets/research-desk-resilient.css':('r404','assets/research-desk-resilient.css','2c99fdeecd4d4245908c0f52f6a679c6f5d7718a'),
 'assets/research-desk-r406.js':('current','assets/research-desk-r406.js','a925ef792a4f894208f88d8edb3a7b4620b3028f')
}
def git_blob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def assemble(research, r404):
    files={'staging-shortcode.php':(ROOT/'staging-shortcode.php').read_bytes()}
    for dest,(source,rel,expected) in SOURCES.items():
        path = (research if source=='research' else r404 if source=='r404' else ROOT)/rel
        data=path.read_bytes()
        if git_blob(data)!=expected:
            raise ValueError(f'Verification failed: {dest}: expected {expected}, got {git_blob(data)}')
        files[dest]=data
    manifest={'status':'REVIEW_ONLY_UNINSTALLED',
              'parent_pr':2729,'source_prs':{'research':158,'r404':2728},
              'inputs':{k:{'git_blob':git_blob(v),'sha256':hashlib.sha256(v).hexdigest()}
                        for k,v in sorted(files.items())}}
    files['MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,b in sorted(files.items()):
            info=zipfile.ZipInfo('fv-apollo-r406/'+name,date_time=(1980,1,1,0,0,0))
            info.external_attr=0o100644<<16
            info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,b,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return out.getvalue()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--research-desk-dir',required=True,type=Path)
    ap.add_argument('--r404-dir',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args()
    b=assemble(args.research_desk_dir,args.r404_dir)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(b)
    print(json.dumps({'status':'BUILT_OFFLINE_NOT_INSTALLED','sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}))
if __name__=='__main__':main()
