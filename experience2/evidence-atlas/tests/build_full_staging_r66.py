#!/usr/bin/env python3
"""Three source-verified R66 WordPress plugin directories. Does NOT install WP."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_full_staging_r64 import build as build_base
from test_desk_profiles_r52 import EXPECTED,blob

def build(output:Path):
    manifest=build_base(output)
    suite=(output/'fv-ex2-apollo-suite/fv-ex2-apollo-suite.php').read_text()
    js=(output/'fv-ex2-evidence-atlas/assets/atlas.js').read_bytes()
    digest=blob(js)
    assert "'assets/atlas.js' => '"+digest+"'" in suite
    assert '0.0.66-staging' in suite
    assert len(manifest['files'])==11
    for name,d in manifest['files'].items():
        assert hashlib.sha256((output/name).read_bytes()).hexdigest()==d
    manifest.update(schema='fv.apollo.r66.wp-triplet.v1',
      custody_fields_verified=54,custody_review='R37 + R55 source metadata pins',
      browser_axe_verified=False,wordpress_installed=False,
      hosted_core_web_vitals=False,release='STAGING_HOLD')
    (output/'STAGING-MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path)
    print(json.dumps(build(p.parse_args().output),sort_keys=True))
