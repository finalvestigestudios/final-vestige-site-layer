#!/usr/bin/env python3
"""Source-pinned R190 native 35+6 checks AND R191 CSS/offer checks.

Executes trusted repository code only in disposable snapshots, retaining no
build exports; always returns exit code 2 and draft/non-release state.
Unlike the R190 wrapper, additionally scans CSS external resource loaders,
SVG/media references and commercial JSON-LD of each six-tool WordPress export.
Native source/safety review, browser QA, merchant verification and QD still
require independent evidence; this is a structural negative gate only.
"""
from __future__ import annotations
import argparse
import hashlib
from importlib import util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

SCHEMA='fv-preparedness-r191-native-css-offer-integrated-v1'
HOLD='DRAFT_HARD_HOLD'
INVALID='INVALID_HARD_HOLD'
PINS={
    'r190_atomic_native_privacy_preflight.py':'cbf52dda1de707d17e516f4cd22432e1b0e20ea9',
    'r191_static_resource_offer_gate.py':'109a06f469f64009d02392b515710591714472a8',
}


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def load(tools: Path, filename: str):
    if (filename not in PINS or tools.is_symlink() or not tools.is_dir()):
        raise ValueError('untrusted tool directory or producer')
    path=tools/filename
    if not path.is_file() or path.is_symlink() or path.stat().st_size>8_000_000:
        raise ValueError('missing/unsafe producer: '+filename)
    if git_blob(path.read_bytes()) != PINS[filename]:
        raise ValueError('changed producer: '+filename)
    spec=util.spec_from_file_location('r191_'+filename.replace('.','_'),path)
    if spec is None or spec.loader is None:raise ValueError('unloadable producer')
    module=util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def admit(native: dict, css: dict, *, build_returncode: int, same_sources: bool) -> None:
    if (type(build_returncode) is not int or build_returncode!=0 or same_sources is not True):
        raise ValueError('disposable build/source-custody failure')
    if (not isinstance(native,dict) or native.get('schema')!='fv-preparedness-r190-atomic-native-six-tool-privacy-v1'
            or native.get('state')!=HOLD or native.get('native_structural_checks_complete') is not True
            or native.get('privacy_exports_structurally_checked') is not True
            or native.get('generated_tools_checked') != 6 or native.get('native_steps_checked') != 12):
        raise ValueError('R190 native/JS/export preflight not authentically completed')
    if (not isinstance(css,dict) or css.get('schema')!='fv-preparedness-r191-resource-offer-boundary-v1'
            or css.get('state')!=HOLD or css.get('errors')!=[]
            or type(css.get('authored_checked')) is not int or css['authored_checked']!=6
            or type(css.get('wp_exports_checked')) is not int or css['wp_exports_checked']!=6):
        raise ValueError('R191 CSS/schema six-source and six-export gate incomplete')
    for record in (native,css):
        for key in ('publication_authorized','independent_qd_pass','merchant_offer_verified'):
            if record.get(key) is not False:raise ValueError('false publication/QD/merchant clearance')
        if record.get('verified_paid_orders') is not None or record.get('realized_net_revenue') is not None:
            raise ValueError('unsupported paid revenue or order claim')
    if css.get('privacy_browser_qa_complete') is not False:
        raise ValueError('CSS structural result misrepresented browser QA')


def preflight(repo: Path, timeout: int=300) -> dict:
    packet={'schema':SCHEMA,'state':INVALID,'publication_authorized':False,
            'independent_qd_pass':False,'privacy_browser_qa_complete':False,
            'merchant_offer_verified':False,'verified_paid_orders':None,
            'realized_net_revenue':None,'native_structural_checks_complete':False,
            'css_offer_exports_structurally_checked':False}
    try:
        if not repo.is_dir() or repo.is_symlink() or type(timeout) is not int or not 10<=timeout<=1200:
            raise ValueError('invalid trusted checkout/timeout')
        source=repo/'preparedness'
        tools=source/'tools'
        r190=load(tools,'r190_atomic_native_privacy_preflight.py')
        css=load(tools,'r191_static_resource_offer_gate.py')
        before=r190._files_and_digest(source)
        packet['original_source_manifest_sha256']=r190._manifest_digest(before)
        native=r190.preflight(repo,timeout)
        packet['r190_state']=native.get('state')
        if native.get('state')!=HOLD:raise ValueError('R190 native checks incomplete: '+str(native.get('blocker',''))[:160])
        if r190._files_and_digest(source)!=before:raise ValueError('original source modified after R190')
        with tempfile.TemporaryDirectory(prefix='fv-r191-css-') as tmp:
            stage=Path(tmp)
            shutil.copytree(source,stage/'preparedness',
                ignore=shutil.ignore_patterns('build','__pycache__','*.pyc'),symlinks=False)
            if r190._files_and_digest(stage/'preparedness')!=before:
                raise ValueError('R191 staged source differs from original')
            run=subprocess.run([sys.executable,'-I','preparedness/tools/build.py'],
                cwd=stage,capture_output=True,text=True,timeout=timeout,check=False)
            packet['draft_build_returncode']=run.returncode
            packet['draft_build_stdout_sha256']=hashlib.sha256(run.stdout.encode()).hexdigest()
            if run.returncode!=0:
                raise ValueError('R191 staged build failed: '+run.stderr[-160:])
            report=css.check(stage/'preparedness')
            packet['css_offer_gate_state']=report.get('state')
            same_sources=r190._files_and_digest(stage/'preparedness')==before
            admit(native,report,build_returncode=run.returncode,same_sources=same_sources)
            packet['css_offer_exports_structurally_checked']=True
            packet['generated_tools_checked']=report['wp_exports_checked']
        if r190._files_and_digest(source)!=before:raise ValueError('original authored content changed')
        packet['native_structural_checks_complete']=True
        packet['state']=HOLD
    except (OSError,ValueError,TypeError,AttributeError,KeyError,ImportError,UnicodeError,
            subprocess.TimeoutExpired) as exc:
        packet['blocker']=str(exc)[:300]
    return packet


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',type=Path,default=Path('.'))
    ap.add_argument('--timeout',type=int,default=300)
    args=ap.parse_args(argv)
    print(json.dumps(preflight(args.repo,args.timeout),sort_keys=True))
    return 2

if __name__=='__main__':raise SystemExit(main())
