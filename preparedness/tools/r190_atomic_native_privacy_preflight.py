#!/usr/bin/env python3
"""R190: atomically bind native source/citation gates to six-tool privacy exports.

DRAFT-ONLY diagnostic for a trusted complete FV repository checkout. Never a
source, medical, food-safety, privacy, independent QD, merchant, or publication
approval. Does not touch WordPress or execute network actions. It copies source
into a disposable directory; R188 itself performs native builds in a second
isolated copy. This wrapper rebuilds the disposable outer copy to allow R189 to
inspect actual generated tool HTML (which R188 alone does not retain).
"""
from __future__ import annotations

import argparse
import hashlib
from importlib import util
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile

SCHEMA = 'fv-preparedness-r190-atomic-native-six-tool-privacy-v1'
HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
# Independently fetched connected GitHub blob IDs at R189 exact head
# 84a4c3e47dae1a5a140316af363dc121f1a43fb0.
PINS = {
    'r188_producer_code_custody_gate.py': '032694b92098838fd99e6cbbd0ce04bf80e1dd36',
    'r188_producer_bound_preflight.py': 'd64827690d4af16df2cc783f16672f02542cc280',
    'r189_tool_privacy_and_commerce_gate.py': 'b98fb8707459b0772ce93e232105d3dc5547bafa',
}
NATIVE_STEPS = ('validate','build','unit_tests','r174','r175','r177',
                'r178','r179','r180','r182','r184','r185')
TOOL_COUNT = 6
ARTICLE_COUNT = 35
MAX_FILES = 5000
MAX_BYTES = 8_000_000
SKIP_DIRS = frozenset({'build', '__pycache__', '.git', '.pytest_cache'})


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def _files_and_digest(prep: Path) -> dict[str,str]:
    """Deterministic source inventory; refuse symlinks and anomalous file kinds."""
    if not prep.is_dir() or prep.is_symlink():
        raise ValueError('missing or symlinked Preparedness root')
    result: dict[str,str] = {}
    for root, dirs, filenames in os.walk(prep, topdown=True, followlinks=False):
        root_path = Path(root)
        for d in dirs:
            if (root_path/d).is_symlink():
                raise ValueError('symlinked source directory: '+d)
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in filenames:
            p = root_path/name
            if name.endswith('.pyc'):
                continue
            rel = p.relative_to(prep).as_posix()
            mode = p.lstat().st_mode
            if not stat.S_ISREG(mode):
                raise ValueError('nonregular source file: '+rel)
            if p.stat().st_size > MAX_BYTES:
                raise ValueError('oversize source file: '+rel)
            payload = p.read_bytes()
            if len(payload) > MAX_BYTES:
                raise ValueError('read source size overrun: '+rel)
            result[rel] = hashlib.sha256(payload).hexdigest()
            if len(result) > MAX_FILES:
                raise ValueError('source inventory file-count limit')
    if not result:
        raise ValueError('empty Preparedness source inventory')
    return dict(sorted(result.items()))


def _manifest_digest(inventory: dict[str,str]) -> str:
    return hashlib.sha256(json.dumps(inventory, sort_keys=True, separators=(',',':')).encode()).hexdigest()


def _load_pinned(tools: Path, filename: str, expected_sha: str):
    if filename not in PINS or expected_sha != PINS[filename]:
        raise ValueError('unrecognized or unreviewed admission producer')
    if tools.is_symlink() or not tools.is_dir():
        raise ValueError('missing/symlinked tools directory')
    path = tools / filename
    if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_BYTES:
        raise ValueError('missing or unsafe admission producer: '+filename)
    if git_blob(path.read_bytes()) != expected_sha:
        raise ValueError('admission producer Git blob changed: '+filename)
    spec = util.spec_from_file_location('fv_r190_' + filename.replace('.','_'), path)
    if spec is None or spec.loader is None:
        raise ValueError('invalid admission module: '+filename)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _no_false_clearance(obj, where='receipt') -> None:
    risky = {'publication_authorized','publication_allowed','independent_qd_pass',
        'independent_qd_verified','qualified_safety_review_complete',
        'qualified_source_review','privacy_browser_qa_complete',
        'merchant_offer_verified','commercial_offer_verified','paid_checkout_enabled',
        'wordpress_publication_performed','wordpress_published',
        'customer_conversion_verified'}
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in risky and value is not False:
                raise ValueError(where+'.'+key+': false clearance')
            _no_false_clearance(value, where+'.'+str(key))
    elif isinstance(obj, list):
        for i,value in enumerate(obj):
            _no_false_clearance(value, where+'['+str(i)+']')


def adjudicate(native: dict, privacy: dict, *, build_returncode: int, unchanged: bool) -> None:
    """Pure strict two-gate contract; raises rather than issue a release pass."""
    if type(build_returncode) is not int or build_returncode != 0 or unchanged is not True:
        raise ValueError('disposable native build failed or altered authored source')
    if not isinstance(native,dict) or native.get('schema') != 'fv-preparedness-r188-producer-bound-preflight-v1':
        raise ValueError('wrong native admission identity')
    if native.get('state') != HOLD or native.get('native_structural_checks_complete') is not True:
        raise ValueError('native structural validation/build/tests incomplete')
    proof = native.get('producer_code')
    if not isinstance(proof,dict) or proof.get('schema') != 'fv-preparedness-r188-producer-code-custody-v1' or proof.get('producer_count') != 16 or proof.get('state') != HOLD:
        raise ValueError('16 code producers not pinned')
    if not re.fullmatch('[0-9a-f]{64}', proof.get('producer_manifest_sha256','')):
        raise ValueError('no producer manifest fingerprint')
    result = native.get('native')
    if not isinstance(result,dict) or result.get('schema') != 'fv-preparedness-r186-whole-archive-native-preflight-v1' or result.get('state') != HOLD:
        raise ValueError('native receipt schema or state invalid')
    census = result.get('census')
    if not isinstance(census,dict) or {k:census.get(k) for k in ('articles','tools','distinct_draft_canonicals','published')} != {'articles':35,'tools':6,'distinct_draft_canonicals':41,'published':0}:
        raise ValueError('35+6 unique-draft destination census invalid')
    checks = native.get('checks')
    if not isinstance(checks,list) or len(checks) != len(NATIVE_STEPS):
        raise ValueError('twelve native source/citation/safety checks not present')
    if [x.get('step') if isinstance(x,dict) else None for x in checks] != list(NATIVE_STEPS):
        raise ValueError('native gate roster or order changed')
    for i, item in enumerate(checks):
        if item.get('status') != ('CHECKED' if i < 3 else 'STRUCTURAL_HOLD'):
            raise ValueError('native step is not structurally complete: '+NATIVE_STEPS[i])
    if not isinstance(privacy,dict) or privacy.get('schema') != 'fv-preparedness-r189-six-tool-privacy-commerce-v1' or privacy.get('state') != HOLD:
        raise ValueError('six-tool privacy gate missing/invalid')
    if privacy.get('errors') != []:
        raise ValueError('six-tool privacy gate reports violations')
    for key,count in [('tools_checked',6),('js_producers_verified',9),('wp_exports_checked',6)]:
        if type(privacy.get(key)) is not int or privacy[key] != count:
            raise ValueError('privacy source/export coverage drift: '+key)
    for key in ('publication_authorized','independent_qd_pass','qualified_safety_review_complete',
                'privacy_browser_qa_complete','merchant_offer_verified'):
        if privacy.get(key) is not False:
            raise ValueError('privacy gate claimed clearance: '+key)
    if privacy.get('verified_paid_orders') is not None or privacy.get('realized_net_revenue') is not None:
        raise ValueError('privacy gate asserted unverified sales or revenue')
    if native.get('publication_authorized') is not False or native.get('independent_qd_pass') is not False or native.get('merchant_offer_verified') is not False:
        raise ValueError('native admission falsely cleared release/commercial status')
    _no_false_clearance(native)
    _no_false_clearance(privacy)


def preflight(repo: Path, timeout: int=300) -> dict:
    """Trusted-checkout diagnostic; never authorizes a publication or merchant link."""
    packet = {'schema':SCHEMA, 'state':INVALID, 'publication_authorized':False,
              'independent_qd_pass':False, 'qualified_safety_review_complete':False,
              'privacy_browser_qa_complete':False, 'merchant_offer_verified':False,
              'verified_paid_orders':None, 'qualified_human_sessions':None,
              'realized_net_revenue':None, 'native_structural_checks_complete':False,
              'privacy_exports_structurally_checked':False}
    try:
        if type(timeout) is not int or timeout < 10 or timeout > 1200 or not repo.is_dir() or repo.is_symlink():
            raise ValueError('invalid trusted checkout/timeout')
        source = repo/'preparedness'
        before = _files_and_digest(source)
        packet['original_source_manifest_sha256'] = _manifest_digest(before)
        tool_dir = source/'tools'
        custody = _load_pinned(tool_dir,'r188_producer_code_custody_gate.py',PINS['r188_producer_code_custody_gate.py'])
        native = _load_pinned(tool_dir,'r188_producer_bound_preflight.py',PINS['r188_producer_bound_preflight.py'])
        privacy = _load_pinned(tool_dir,'r189_tool_privacy_and_commerce_gate.py',PINS['r189_tool_privacy_and_commerce_gate.py'])
        # Verify original 16 producer identities before *any* native execution.
        precondition = custody.verify(source)
        if precondition.get('state') != HOLD or precondition.get('producer_count') != 16:
            raise ValueError('R188 original producer pins not accepted')
        packet['producer_manifest_sha256'] = precondition['producer_manifest_sha256']
        with tempfile.TemporaryDirectory(prefix='fv-prep-r190-') as tmp:
            stage = Path(tmp)
            shutil.copytree(source, stage/'preparedness',
                            ignore=shutil.ignore_patterns('build','__pycache__','*.pyc'),
                            symlinks=False)
            if _files_and_digest(stage/'preparedness') != before:
                raise ValueError('snapshot differs from original authored source')
            native_receipt = native.preflight(stage,timeout)
            packet['native_state'] = native_receipt.get('state')
            if native_receipt.get('state') != HOLD:
                raise ValueError('R188 native structural preflight did not complete')
            # R188's inner copy is discarded. Rebuild only the disposable outer
            # snapshot for the *authentic* R189 generated-HTML inspection.
            run = subprocess.run([sys.executable,'-I','preparedness/tools/build.py'],
                cwd=stage, capture_output=True, text=True, timeout=timeout,
                check=False)
            packet['draft_build_returncode'] = run.returncode
            packet['draft_build_stdout_sha256'] = hashlib.sha256(run.stdout.encode()).hexdigest()
            if run.returncode != 0:
                raise ValueError('disposable WordPress draft build failed: '+run.stderr[-200:])
            if _files_and_digest(stage/'preparedness') != before:
                raise ValueError('build changed staged authored source')
            privacy_receipt = privacy.check(stage/'preparedness')
            packet['privacy_state'] = privacy_receipt.get('state')
            adjudicate(native_receipt, privacy_receipt, build_returncode=run.returncode,
                       unchanged=True)
            if _files_and_digest(stage/'preparedness') != before:
                raise ValueError('privacy gate changed staged authored source')
            packet['native_structural_checks_complete'] = True
            packet['privacy_exports_structurally_checked'] = True
            packet['native_steps_checked'] = len(native_receipt['checks'])
            packet['generated_tools_checked'] = privacy_receipt['wp_exports_checked']
        if _files_and_digest(source) != before:
            raise ValueError('original authored sources changed during audit')
        packet['state'] = HOLD  # all structural checks only; NEVER PASS
    except (OSError, ValueError, TypeError, KeyError, AttributeError,
            ImportError, subprocess.TimeoutExpired, UnicodeError, json.JSONDecodeError) as exc:
        packet['blocker'] = str(exc)[:300]
    return packet


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--timeout', type=int, default=300)
    args = parser.parse_args(argv)
    print(json.dumps(preflight(args.repo,args.timeout),sort_keys=True))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
