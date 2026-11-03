#!/usr/bin/env python3
"""Assemble three complete, unchanged-source WordPress plugin directories for
PRIVATE REVIEW ONLY. This builds files; it never connects to or writes WordPress.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[3]
HERE=ROOT/'experience2/evidence-atlas'
DESK=ROOT/'experience2/research-desk'
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE/'tests'))
import build_wordpress_stage
from test_desk_profiles_r52 import EXPECTED,blob

ACTIVE_DESK_PROFILE='r84-chronology-certainty'
RESEARCH_FILES=tuple(sorted(EXPECTED[ACTIVE_DESK_PROFILE]))
SUITE_FILES=('integration/fv-ex2-apollo-suite.php','integration/apollo-suite.css')

def build(output:Path):
    for relative,sha in EXPECTED[ACTIVE_DESK_PROFILE].items():
        source=DESK/relative
        if not source.is_file() or blob(source.read_bytes())!=sha:
            raise ValueError('Do not stage unverified original R38 file: '+relative)
    output.mkdir(parents=True,exist_ok=True)
    atlas_manifest=build_wordpress_stage.build(output)
    assert atlas_manifest['media_rights_unreviewed']==6
    assert atlas_manifest['embedded_images']==0 and atlas_manifest['geographic_pins']==0
    for relative in RESEARCH_FILES:
        dst=output/'fv-ex2-research-desk'/relative
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(DESK/relative,dst)
    for relative in SUITE_FILES:
        src=HERE/relative
        dst=output/'fv-ex2-apollo-suite'/Path(relative).name
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dst)
    allfiles=sorted(p for p in output.rglob('*') if p.is_file() and p.name!='STAGING-MANIFEST.json')
    expected=4+len(RESEARCH_FILES)+len(SUITE_FILES)
    assert len(allfiles)==expected,(len(allfiles),expected)
    paths={p.relative_to(output).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in allfiles}
    manifest={'schema':'fv.apollo.r64.wp-triplet.v1','release':'STAGING_HOLD',
              'wordpress_installed':False,'axe_certified':False,'media_rights_unreviewed':6,
              'embedded_images':0,'geographic_pins':0,'R38_git_blobs':EXPECTED['r38-custody-search'],
              'active_desk_profile':ACTIVE_DESK_PROFILE,
              'active_desk_git_blobs':EXPECTED[ACTIVE_DESK_PROFILE],
              'atlas_crosswalk_git_blob':atlas_manifest['source_crosswalk_blob'],
              'plugin_directories':['fv-ex2-evidence-atlas','fv-ex2-research-desk','fv-ex2-apollo-suite'],
              'shortcode':'[fv_ex2_apollo_suite]','files':paths}
    (output/'STAGING-MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    return manifest

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(build(args.output),sort_keys=True))
