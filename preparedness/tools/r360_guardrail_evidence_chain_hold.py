#!/usr/bin/env python3
"""R360: source-pinned, fail-closed orchestration of independent Preparedness gates.

Every child gate is a *review/diagnostic* gate, not a safety certification.
The generated receipt is never a QD pass, publishing authorization, or sale.
Read-only. No WordPress, social, checkout, analytics, or network mutations.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

SCHEMA = 'fv-preparedness-r360-guardrail-chain-v1'
PINNED_PARENT = '3076317ae51b7527146920ab738e5b421b3e5cee'
# The content SHAs below were read from exact R359 source tree on 2026-11-13 PT.
GATES = {
 'r350_nine_branch_content_custody_hold.py':'4f3446a907b4c53c3ea33773d8f2c25cd512c94a',
 'r351_canonical_route_gate.py':'aaac2009bea3bfa1ecb0562d03f26c2d468819ec',
 'r352_tool_lifecycle_custody_gate.py':'6b9a6047cfbbb151caba404102e589d455ebe4e7',
 'r353_private_wp_preview_parity_hold.py':'e30195338e0de50c475d0ed178cefd2cac0c3db6',
 'r354_exact_claim_render_custody_hold.py':'6140181eae7147f56878eb4b37a2c3028ec17d91',
 'r355_sensitive_form_privacy_provenance_hold.py':'74408a00e3ca6f5da8f3ed98a917577c989b0941',
 'r356_noscript_contract_hold.py':'3ebd0e4e7b6124b03a076448091ccb2dd8fed7de',
 'r357_qa_boundary_hold.py':'edcf5224e1aaa46c80b1686fdb61d508e5699a1f',
 'r358_monotonic_gate_hold.py':'4253958181a17030f4175088562e6948f9b58aff',
 'r359_tool104_print_dispatch_citation_hold.py':'718abdb757d1f3ca8dbb719dc3e97d50ff53376e',
}
NO_APPROVAL = ('may_publish','may_merge','qd_pass','safety_review_complete',
 'privacy_review_complete','verified_sale','native_export_verified',
 'independent_qd_pass','medical_safety_verified','merchant_approved',
 'publication_authorized','verified_paid_conversion',
 'ready_to_publish','publish_allowed','safe_to_publish')
HOLD = {k:False for k in NO_APPROVAL}
_STATUS = re.compile(r'^[A-Z][A-Z0-9_]{3,90}$')


def git_blob(data: bytes) -> str:
 return hashlib.sha1(b'blob '+str(len(data)).encode('ascii')+b'\0'+data).hexdigest()


def evaluate_child(name: str, exit_code: int, stdout: str, stderr: str='') -> dict:
 """Admit machine evidence only when child has a parseable explicit hard hold."""
 errors=[]
 if name not in GATES: errors.append('UNREGISTERED_CHILD')
 if type(exit_code) is not int or exit_code != 2: errors.append('UNEXPECTED_CHILD_EXIT')
 if not isinstance(stdout,str) or len(stdout)>2_000_000: errors.append('INVALID_OUTPUT_SIZE')
 if not isinstance(stderr,str) or len(stderr)>20_000: errors.append('INVALID_STDERR_SIZE')
 payload={}
 if not errors:
  try:
   payload=json.loads(stdout,object_pairs_hook=_unique)
   if type(payload) is not dict: raise ValueError('not an object')
  except (ValueError,TypeError,OverflowError): errors.append('INVALID_JSON')
 status=payload.get('status') if isinstance(payload,dict) else None
 if type(status) is not str or not _STATUS.fullmatch(status) or not status.endswith('HARD_HOLD'):
  errors.append('MISSING_EXPLICIT_HARD_HOLD')
 for k in NO_APPROVAL:
  if isinstance(payload,dict) and k in payload and payload[k] is not False:
   errors.append('UNAUTHORIZED_APPROVAL:'+k)
 if isinstance(payload,dict) and payload.get('state') in ('PASS','VERIFIED','LIVE','APPROVED','PUBLISH_READY'):
  errors.append('UNAUTHORIZED_SUCCESS_STATE')
 if status == 'INVALID_HARD_HOLD': errors.append('CHILD_INVALID_HOLD')
 if isinstance(payload,dict) and payload.get('errors'): errors.append('CHILD_REPORTED_ERRORS')
 # Do not turn a child's diagnostic status into a claim of validated native exports.
 return {'gate':name,'status':status if isinstance(status,str) else None,
         'diagnostic_errors':payload.get('errors',[]) if isinstance(payload,dict) and isinstance(payload.get('errors',[]),list) else ['MALFORMED_ERRORS'],
         'admission':'REVIEW_ONLY_HARD_HOLD' if not errors else 'INVALID_HARD_HOLD',
         'errors':sorted(set(errors))}


def _unique(pairs):
 out={}
 for k,v in pairs:
  if k in out: raise ValueError('duplicate JSON key')
  out[k]=v
 return out


def verify_source(path: Path, expected: str) -> str | None:
 """Use bytes, not Python source import, for pin checking."""
 try:
  if path.is_symlink() or not path.is_file() or path.stat().st_size>500_000:
   return 'MISSING_UNSAFE_OR_OVERSIZE_CHILD'
  return None if git_blob(path.read_bytes())==expected else 'CHILD_BLOB_DRIFT'
 except (OSError,ValueError):
  return 'CHILD_SOURCE_UNAVAILABLE'


def summarize(children: list, *, missing: list | None=None) -> dict:
 errors=[]
 if type(children) is not list or len(children)!=len(GATES):
  errors.append('INCOMPLETE_GATE_COVERAGE')
 names=[x.get('gate') if isinstance(x,dict) else None for x in children] if isinstance(children,list) else []
 if sorted(names,key=str)!=sorted(GATES): errors.append('GATE_NAME_COVERAGE_MISMATCH')
 if any(not isinstance(x,dict) or x.get('admission')!='REVIEW_ONLY_HARD_HOLD' for x in children):
  errors.append('CHILD_NOT_ADMITTED')
 missing=missing or []
 if missing: errors.append('UNAVAILABLE_OR_DRIFTED_SOURCE')
 return {'schema':SCHEMA,'status':'INVALID_HARD_HOLD' if errors else 'REVIEW_REQUIRED_HARD_HOLD',
         'source_parent_commit':PINNED_PARENT,'gate_count':len(GATES),
         'gate_results':children,'source_holds':missing,'errors':sorted(set(errors)),
         **HOLD}


def audit(root: Path, *, timeout: int=25) -> dict:
 root=Path(root).resolve()
 tool_dir=root/'preparedness'/'tools'
 missing=[]; children=[]
 if not (root/'.git').exists():
  return summarize([],missing=['AUTHENTIC_CHECKOUT_MISSING'])
 for name,sha in GATES.items():
  path=tool_dir/name
  reason=verify_source(path,sha)
  if reason:
   missing.append(name+':'+reason)
   children.append({'gate':name,'admission':'INVALID_HARD_HOLD','errors':[reason]})
   continue
  try:
   args=[sys.executable,'-I',str(path),'--repo-root',str(root)]
   if name=='r357_qa_boundary_hold.py': args+=['--qa','157']
   p=subprocess.run(args,text=True,capture_output=True,timeout=timeout,check=False)
   children.append(evaluate_child(name,p.returncode,p.stdout,p.stderr))
  except (OSError,subprocess.SubprocessError,UnicodeError) as exc:
   children.append({'gate':name,'admission':'INVALID_HARD_HOLD','errors':['CHILD_EXECUTION:'+type(exc).__name__]})
 return summarize(children,missing=missing)


if __name__=='__main__':
 parser=argparse.ArgumentParser()
 parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
 doc=audit(parser.parse_args().repo_root)
 print(json.dumps(doc,sort_keys=True,indent=2))
 raise SystemExit(2) # Permanent hard hold; there is no authorization mode.
