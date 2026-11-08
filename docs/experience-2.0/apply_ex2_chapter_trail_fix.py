#!/usr/bin/env python3
"""Create an OFFLINE, derived seven-chapter review bundle with keyboard-focus fix.

Reads a protected local source ZIP, never connects to a network or CMS, and
refuses unexpected hashes. The derived bundle intentionally DOES NOT satisfy
existing exact-source release preflight until separately admitted by QD.
"""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

PARENT_ZIP = '9833800a112027b17dfec154358d7b630e258feb581820b749ca26ab88ffe69d'
PARENT_PHP = '91adf4e42a711bf253370a706b29d1428131051333e470af4a841948d1e97b04'
PHP_PATH = 'mu-plugins/fv-ex2-playground-review.php'
EXPECTED_FILES = {'REVIEW.txt', 'SOURCE_CUSTODY.json', 'blueprint.json', PHP_PATH,
                  'mu-plugins/fv-ex2-private-browser-receipt.php'}
CSS_ANCHOR = '\nFVPG_CSS_END\n'
JS_ANCHOR = '\nFVPG_JS_END\n'

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def derive(src: Path, dst: Path, css: Path, js: Path) -> dict:
    raw=src.read_bytes()
    if digest(raw)!=PARENT_ZIP:
        raise ValueError('PROTECTED_PARENT_SHA_MISMATCH')
    with ZipFile(src) as archive:
        members=archive.infolist()
        if set(x.filename for x in members)!=EXPECTED_FILES:
            raise ValueError('UNEXPECTED_PARENT_BUNDLE_MEMBERS')
        content={i.filename:archive.read(i.filename) for i in members}
    if digest(content[PHP_PATH])!=PARENT_PHP:
        raise ValueError('PROTECTED_PARENT_PLUGIN_SHA_MISMATCH')
    original=content[PHP_PATH].decode('utf-8')
    css_text=css.read_text('utf-8').strip()
    js_text=js.read_text('utf-8').strip()
    for marker in (CSS_ANCHOR,JS_ANCHOR):
        if original.count(marker)!=1: raise ValueError('UNEXPECTED_SOURCE_ANCHOR_'+marker.strip())
    if not css_text.startswith('/* Experience 2.0 chapter trail: accessible no-script fallback.'):
        raise ValueError('CSS_PATCH_NOT_REVIEWED')
    if not js_text.startswith('/* Experience 2.0 chapter trail: align keyboard focus'):
        raise ValueError('JS_PATCH_NOT_REVIEWED')
    updated=original.replace(CSS_ANCHOR,'\n'+css_text+'\n'+CSS_ANCHOR)
    updated=updated.replace(JS_ANCHOR,'\n'+js_text+'\n'+JS_ANCHOR)
    if updated==original: raise ValueError('EMPTY_PATCH')
    content[PHP_PATH]=updated.encode('utf-8')
    original_custody=json.loads(content['SOURCE_CUSTODY.json'])
    if original_custody.get('native_wordpress_tested') is not False:
        raise ValueError('UNEXPECTED_PARENT_WORDPRESS_CLAIM')
    original_custody['files_sha256'][PHP_PATH]=digest(content[PHP_PATH])
    original_custody['derived_review_patch']='chapter-trail-keyboard-focus-2026-11-07'
    original_custody['parent_zip_sha256']=PARENT_ZIP
    original_custody['parent_php_sha256']=PARENT_PHP
    # Do not reuse the old canonical source hash as if the bytes were unchanged.
    original_custody['parent_exact_source_sha256']=original_custody.pop('exact_source_sha256',None)
    original_custody['exact_source_sha256']=digest(content[PHP_PATH])
    original_custody['source_hash_scheme']='derived_review_php_sha256_only_not_release_source'
    original_custody['release_authorized']=False
    original_custody['native_wordpress_tested']=False
    original_custody['requires_fresh_exact_source_acceptance']=True
    content['SOURCE_CUSTODY.json']=(json.dumps(original_custody,indent=2,sort_keys=True)+'\n').encode()
    dst.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(dst,'w') as output:
        for info in members:
            output.writestr(info,content[info.filename])
    report={'parent_zip_sha256':PARENT_ZIP,'parent_php_sha256':PARENT_PHP,
            'derived_zip_sha256':digest(dst.read_bytes()),
            'derived_php_sha256':digest(content[PHP_PATH]),
            'css_patch_sha256':digest(css_text.encode()),'js_patch_sha256':digest(js_text.encode()),
            'native_wordpress_tested':False,'release_authorized':False,
            'status':'OFFLINE_REVIEW_ONLY_REQUIRES_NEW_SOURCE_ADMISSION'}
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parent',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--css',required=True,type=Path)
    parser.add_argument('--js',required=True,type=Path)
    args=parser.parse_args()
    print(json.dumps(derive(args.parent,args.out,args.css,args.js),indent=2))
