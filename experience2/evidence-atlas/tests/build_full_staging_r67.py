#!/usr/bin/env python3
"""Reproducible three-plugin R67 staging distribution; NEVER installs WordPress."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_full_staging_r66 import build as build_base
from test_desk_profiles_r52 import EXPECTED,blob

def build(output:Path):
    manifest=build_base(output)
    suite=(output/'fv-ex2-apollo-suite/fv-ex2-apollo-suite.php').read_text()
    js=(output/'fv-ex2-evidence-atlas/assets/atlas.js').read_bytes()
    assert "'assets/atlas.js' => '"+blob(js)+"'" in suite
    assert blob((output/'fv-ex2-research-desk/templates/ledger.html').read_bytes()) == EXPECTED['r84-chronology-certainty']['templates/ledger.html']
    assert len(manifest['files'])==11
    for name,d in manifest['files'].items():
        assert hashlib.sha256((output/name).read_bytes()).hexdigest()==d
    manifest.update(schema='fv.apollo.r67.wp-triplet.v1',
        atlas_custody_fields_verified=54,desk_custody_fields_verified=30,
        cross_component_navigation='reviewed-source-custody-gated',
        installed_wordpress=False,axe_core_verified=False,
        hosted_core_web_vitals=False,release='STAGING_HOLD')
    (output/'STAGING-MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    return manifest

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path)
    print(json.dumps(build(parser.parse_args().output),sort_keys=True))
