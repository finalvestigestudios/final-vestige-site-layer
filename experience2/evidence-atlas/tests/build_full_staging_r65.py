#!/usr/bin/env python3
"""R65 pinned three-plugin distribution, review only; no WordPress writes."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_full_staging_r64 import build as original_build

def build(output:Path):
    manifest=original_build(output)
    css=(output/'fv-ex2-apollo-suite/apollo-suite.css').read_text()
    php=(output/'fv-ex2-apollo-suite/fv-ex2-apollo-suite.php').read_text()
    assert '.fva-card__external' in css and 'min-height:44px' in css
    assert '0.0.66-staging' in php
    manifest['schema']='fv.apollo.r65.wp-triplet.v1'
    manifest['scope']='Original R38 plus source-built Atlas, no embedded NASA photography'
    manifest['browser_axe_verified']=False
    manifest['full_source_target_audit']='qa-r65/R65_ALL_TARGETS_BROWSER_RECEIPT.json (external QA attachment)'
    (output/'STAGING-MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    for name,digest in manifest['files'].items():
        assert hashlib.sha256((output/name).read_bytes()).hexdigest()==digest
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path)
    print(json.dumps(build(p.parse_args().output),sort_keys=True))
