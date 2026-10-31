#!/usr/bin/env python3
"""Deterministic build and WordPress-API-mock integration, with tamper detection."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

BRIDGE=Path(__file__).resolve().parents[1]
CASEFILE=BRIDGE.parent/'apollo-casefile'
PHP=BRIDGE/'qa/php_shortcode_harness.php'

def call(*args):
    result=subprocess.run(args,capture_output=True,text=True,check=True,timeout=60)
    return result.stdout

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
    assert 'No syntax errors' in call('php','-l',str(BRIDGE/'fv-ex2-apollo-casefile.php'))
    assert 'No syntax errors' in call('php','-l',str(PHP))
    os.environ['FV_EX2_ALLOW_UNPINNED_FIXTURE']='1'
    call(sys.executable,str(BRIDGE/'build.py'))
    files=sorted((BRIDGE/'generated').glob('*'))
    first={x.name:digest(x) for x in files}
    call(sys.executable,str(BRIDGE/'build.py'))
    second={x.name:digest(x) for x in files}
    assert first==second,'build is not byte-for-byte deterministic'
    manifest=json.loads((BRIDGE/'generated/manifest.json').read_text())
    # The current offline fixture has four known response-file differences.
    # The checked-in builder MUST reject it without a test-only override.
    env=os.environ.copy();env.pop('FV_EX2_ALLOW_UNPINNED_FIXTURE',None)
    failed=subprocess.run([sys.executable,str(BRIDGE/'build.py')],capture_output=True,text=True,env=env)
    if manifest['source_matches_pr215']:
        assert failed.returncode==0, failed.stderr
        assert manifest['source_pin_mismatches']==[]
    else:
        assert failed.returncode != 0 and 'SOURCE_PIN_MISMATCH' in failed.stderr
        assert sorted(manifest['source_pin_mismatches'])==['assets/response.css','assets/response.js','response-crosswalk.json','response_lab.py']
    assert len(manifest['outputs_sha256'])==7
    assert all(first[n]==digest(BRIDGE/'generated'/n) for n in manifest['outputs_sha256'])
    assert all(len(manifest['upstream_source_git_blob_sha1'][n])==40 for n in manifest['upstream_source_git_blob_sha1'])
    report=json.loads(call('php',str(PHP),'once'))
    assert report['first_has_sources'] and report['second_is_anchor'] and report['asset_base_replaced']
    assert report['first_bytes']>50000
    # Tamper test: copy the entire adapter to a clean tempfile, mutate just one file,
    # and ensure the PHP shortcode emits its fallback instead of broken partial markup.
    with tempfile.TemporaryDirectory(prefix='fv-apollo-bridge-') as tmp:
        dst=Path(tmp)
        shutil.copytree(BRIDGE/'generated',dst/'generated')
        shutil.copy(BRIDGE/'fv-ex2-apollo-casefile.php',dst/'fv-ex2-apollo-casefile.php')
        harness=(dst/'probe.php')
        harness.write_text('''<?php define('ABSPATH','/mock/');function add_shortcode($a,$b){}function plugin_dir_path($p){return dirname($p).'/';}function plugin_dir_url($p){return 'https://staging.invalid/plugin/';}function esc_url($v){return htmlspecialchars($v,ENT_QUOTES,'UTF-8');}require __DIR__.'/fv-ex2-apollo-casefile.php';echo fv_ex2_apollo_casefile_shortcode();''')
        # Pretend this temp-copy was built on an exact pinned upstream version.
        # First prove the pristine copy renders without any fixture override.
        mf=dst/'generated/manifest.json'
        current=json.loads(mf.read_text());current['source_matches_pr215']=True
        mf.write_text(json.dumps(current))
        assert 'id="documentary-trails"' in call('php',str(harness))
        target=dst/'generated/apollo.js'
        target.write_bytes(target.read_bytes()+b'\n// mutation intentionally injected by local test\n')
        fallback=call('php',str(harness))
        assert 'staging component unavailable' in fallback
        assert 'id="documentary-trails"' not in fallback
    text=(BRIDGE/'generated/fragment.html').read_text()
    assert all(f'id="{n}"' in text for n in ('chronology','research-desk','claim-ledger','comparison-lab','response-audit','documentary-trails','source-gallery','atlas'))
    assert text.count('{{FV_EX2_ASSET_BASE}}')==4
    assert 'no NASA image bytes' in text.lower() or 'no nasa image bytes' in text.lower() or 'no nasa photographs' in text.lower()
    assert '<main ' not in text and '<h1' not in text
    assert not any(s in text.lower() for s in ('<script','<style','<img'))
    print('WP_BRIDGE_CONTRACT_PASS',json.dumps({'build_outputs':len(first),'sha256_deterministic':True,'php_shortcodes_verified':True,'tamper_fails_closed':True,'chapter_count':8,'no_images':True,'pinned_upstream_enforced':True,'offline_fixture_mismatches':manifest['source_pin_mismatches']},sort_keys=True))
    return {'builder':True,'determinism':True,'php_mock':True,'tamper_fail_closed':True,'outputs':first,'source_head':'exact_PR215' if manifest['source_matches_pr215'] else 'offline_fixture_with_four_earlier_response_files'}

if __name__=='__main__':
    evidence=run()
    (BRIDGE/'qa'/'BRIDGE_CONTRACT_RESULTS.json').write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
