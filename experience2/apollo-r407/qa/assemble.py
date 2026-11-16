#!/usr/bin/env python3
"""Fail-closed, read-only inputs -> deterministic local staging candidate; NEVER installs WP."""
import argparse
import hashlib
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
 'templates/ledger.html':'403d128c57b9bc82dac7c619651689070edef86c',
 'assets/source-ledger.css':'b8cf00afeceba115a9e9d19044fc11dcf2890cbe',
 'assets/research-desk-resilient.css':'2c99fdeecd4d4245908c0f52f6a679c6f5d7718a',
 'assets/research-desk-r407.js':'222e084d4d5cba5b979037df2018d82946fa9a75',
 'assets/chronology.css':'d60a1c52dca1a6b82f15cb6009a1a876a2ad33b2',
}
def blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def assemble(pr158:Path,r404:Path,out:Path):
    sources={
      'templates/ledger.html':pr158/'templates/ledger.html',
      'assets/source-ledger.css':pr158/'assets/source-ledger.css',
      'assets/research-desk-resilient.css':r404/'assets/research-desk-resilient.css',
      'assets/research-desk-r407.js':ROOT/'assets/research-desk-r407.js',
      'assets/chronology.css':ROOT/'assets/chronology.css',
    }
    if out.exists():raise ValueError('refuse existing output path: '+str(out))
    contents={}
    for name,path in sources.items():
        if not path.is_file():raise ValueError('missing dependency: '+str(path))
        data=path.read_bytes()
        if blob(data)!=EXPECTED[name]:raise ValueError('Git blob mismatch: '+str(path))
        contents[name]=data
    # No output directory exists before ALL source hashes have passed.
    out.mkdir(parents=True)
    for name,data in sorted(contents.items()):
        target=out/name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    shutil.copyfile(ROOT/'staging-shortcode.php',out/'staging-shortcode.php')
    print('BUILT_ONLY: immutable sources verified, WordPress staging NOT installed:',out)
if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--pr158-root',type=Path,required=True)
    parser.add_argument('--r404-root',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    a=parser.parse_args()
    assemble(a.pr158_root,a.r404_root,a.out)
