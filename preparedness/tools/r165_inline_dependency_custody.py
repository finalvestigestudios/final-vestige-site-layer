#!/usr/bin/env python3
"""R165: fail-closed inline-JS custody + sandboxed model smoke checks.

NOT a browser, privacy, medical, merchant, or QD approval. Always exits 2.
Previous R164 -> R163 -> R162 -> R161 custodians must pass before audit passes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

SCHEMA = 'fv-preparedness-r165-inline-js-custody-v1'
EXPECTED = {
    'shelter_common.js': 'efe1c7910d99437e3687621dabab8ce55dc24fd4',
    'reunion_card.js': 'b1a09b1eda1ae26f081de65b400a37bc19538035',
}
STAGED = 'preparedness/review/r163/family-reunification-card.body.html'
PLACEHOLDER = re.compile(r'\{\{inline-js:([a-z_]+\.js)\}\}')
RISK = re.compile(
    r'(?:\bfetch\s*\(|\bsendBeacon\s*\(|\bXMLHttpRequest\b|\bWebSocket\b|'
    r'\bEventSource\b|\blocalStorage\s*[.\[]|\bsessionStorage\s*[.\[]|'
    r'\bindexedDB\s*[.\[]|\bdocument\.cookie\b|\bpostMessage\s*\(|'
    r'\bFormData\s*\(|\bnavigator\.serviceWorker\b|\beval\s*\(|'
    r'\bFunction\s*\(|\bimport\s*\(|\binnerHTML\s*=|\bouterHTML\s*=|'
    r'\binsertAdjacentHTML\s*\(|\bdocument\.write\s*\(|'
    r'\bwindow\.open\s*\(|\bImage\s*\(|\bsetAttribute\s*\(\s*[\'\"](?:src|href)|'
    r'\bhttp[s]?\s*:\s*//|\bdata\s*:\s*text/html)',
    re.I)


def need(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError(msg)


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def inspect_script(name: str, code: str) -> None:
    need(name in EXPECTED, 'unknown script dependency')
    need(bool(code.strip()), f'{name}: empty script')
    need(not re.search(r'</?script\b|<!--|-->|\]\]>', code, re.I),
         f'{name}: HTML/script boundary injection')
    need(not PLACEHOLDER.search(code) and '{{' not in code,
         f'{name}: nested template token')
    need(not RISK.search(code), f'{name}: sensitive network/storage/dynamic code sink')
    if name == 'shelter_common.js':
        need(code.count('URL.createObjectURL(blob)') == 1 and
             code.count('URL.revokeObjectURL(url)') == 1 and
             'text/plain;charset=utf-8' in code,
             'shared helper: local plain-text download contract changed')
        need('function paCleanText(' in code and 'function paIsoOrNull(' in code,
             'shared helper: sanitization contract missing')
    elif name == 'reunion_card.js':
        for anchor in ('function rcClean(', 'function rcModel(', 'function rcWarnings(',
                       'minimal ? null : row("If not, meet at", c.meet2)',
                       'var back = minimal', 'rcLooksLikeStreetAddress', 'rcLooksLikeGovId'):
            need(anchor in code, 'reunion model contract missing: '+anchor)


def expand_checked(template: str, scripts: dict[str, str]) -> tuple[str, dict]:
    need(set(scripts) == set(EXPECTED), 'script closure requires exactly two known files')
    names = PLACEHOLDER.findall(template)
    need(names == ['shelter_common.js', 'reunion_card.js'],
         'script ordering, closure, or multiplicity changed')
    for name, code in scripts.items():
        inspect_script(name, code)
    expanded = PLACEHOLDER.sub(lambda m: scripts[m.group(1)], template)
    need('{{inline-js:' not in expanded, 'unresolved/unknown inline dependency')
    need(expanded.count('function rcModel(') == 1 and
         expanded.count('function paCleanText(') == 1,
         'duplicate or missing model function after expansion')
    need(len(expanded) == len(template) - sum(len('{{inline-js:'+n+'}}') for n in names)
         + sum(len(scripts[n]) for n in names), 'non-exact template expansion')
    return expanded, {'dependency_order': names, 'expanded_sha256': hashlib.sha256(expanded.encode()).hexdigest()}


# Evaluates only pinned pure-function helpers in a Node vm without DOM, fetch, storage or require.
# A positive result is NOT an exfiltration check, browser privacy proof, or safety review.
NODE_SMOKE = r'''
const vm=require('node:vm');
const data=JSON.parse(require('node:fs').readFileSync(0,'utf8'));
const context=vm.createContext({Date,Math,Number,String,Object,Array,RegExp,isFinite,
    console:{log(){throw Error('logging disabled')}}},
    {codeGeneration:{strings:false,wasm:false}});
for(const source of data.scripts) vm.runInContext(source,context,{timeout:600});
const call=(expression)=>vm.runInContext(expression,context,{timeout:600});
function assert(test,label){if(!test)throw Error(label)}
const inp={hhName:'Household',hhPhone:'1234567890',outName:'Contact',outPhone:'1234567890',
 meet1:'Library',meet2:'Park',school:'School',schoolPlan:'Check school notice',
 pickup:'On authorized list',careName:'Carer',carePhone:'1234567890',access:'Needs assistance',reviewed:'2020-01-01'};
context.TEST_INPUT=inp;
const small=JSON.parse(JSON.stringify(call('rcModel(TEST_INPUT,true)')));
const large=JSON.parse(JSON.stringify(call('rcModel(TEST_INPUT,false)')));
const serialized=JSON.stringify(small);
for(const forbidden of ['School','Carer','Needs assistance','Park','authorized list'])
  assert(!serialized.includes(forbidden),'minimal card leaked field: '+forbidden);
assert(JSON.stringify(large).includes('School'),'standard card lost school');
assert(JSON.stringify(large).includes('Park'),'standard card lost alternate meeting place');
assert(call('rcClean({hhName:"X".repeat(100),schoolPlan:"Y".repeat(100)}).hhName.length')===24,'name cap');
assert(call('rcClean({hhName:"X".repeat(100),schoolPlan:"Y".repeat(100)}).schoolPlan.length')===44,'plan cap');
assert(call('rcPhone("+1 (555) 010-0000abc")').indexOf('a')<0,'phone filter');
assert(call('rcLooksLikeGovId("123-45-6789")')===true,'ID warning detector');
assert(call('rcLooksLikeStreetAddress("100 Main Street")')===true,'address warning detector');
assert(call('rcWarnings({outName:"",outPhone:"",meet1:""},"2026-11-06").length')>=2,'empty plan reminders');
assert(call('rcWarnings({reviewed:"2020-01-01",outName:"A",outPhone:"1234567890",meet1:"P"},"2026-11-06").some(s=>s.includes("year"))'),'review date');
process.stdout.write(JSON.stringify({model_smoke:'PASS',checks:10,privacy_verified:false,release_approved:false}));
'''


def model_smoke(scripts: dict[str, str], executable: str | None = None) -> dict:
    exe = executable if executable is not None else shutil.which('node')
    if not exe:
        return {'model_smoke': 'NOT_RUN_NODE_MISSING', 'checks': 0}
    payload = json.dumps({'scripts': [scripts[n] for n in EXPECTED]})
    try:
        completed = subprocess.run([exe, '-e', NODE_SMOKE], input=payload,
                                   text=True, capture_output=True, timeout=8, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError('sandboxed model smoke unavailable: '+type(exc).__name__) from exc
    need(completed.returncode == 0, 'sandboxed model smoke failed: '+completed.stderr[:500])
    result = json.loads(completed.stdout)
    need(result.get('model_smoke') == 'PASS' and result.get('checks') >= 10,
         'sandboxed model evidence incomplete')
    return result


def audit(root: Path) -> dict:
    import sys
    sys.path.insert(0, str(root / 'preparedness' / 'tools'))
    import r164_family_card_browser_contract as prior
    old = prior.audit(root)
    need(old.get('state') == 'DRAFT_HARD_HOLD', 'R164/body/citation custody failed')
    template = (root / STAGED).read_text(encoding='utf-8')
    scripts = {}
    blobs = {}
    for name, expected in EXPECTED.items():
        path = root / 'preparedness' / 'tools' / name
        need(path.is_file() and not path.is_symlink(), name+': missing/linked dependency')
        raw = path.read_bytes()
        blob = git_blob(raw)
        need(blob == expected, name+': JS code changed; manual re-review required')
        blobs[name] = blob
        scripts[name] = raw.decode('utf-8')
    _, expansion = expand_checked(template, scripts)
    smoke = model_smoke(scripts)
    return {'schema': SCHEMA, 'state': 'DRAFT_HARD_HOLD',
            'dependency_blob_shas': blobs, **expansion, **smoke,
            'model_smoke_is_browser_test': False, 'transmission_absence_proven': False,
            'privacy_verified': False, 'source_review_complete': False,
            'independent_qd_pass': False, 'publication_authorized': False,
            'paid_offer_authorized': False}


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, default=Path('.'))
    opts = p.parse_args(argv)
    try:
        result = audit(opts.repo.resolve(strict=True))
    except (OSError, ImportError, KeyError, UnicodeError, ValueError, TypeError) as exc:
        result = {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD',
                  'reason': str(exc), 'publication_authorized': False}
    print(json.dumps(result, sort_keys=True))
    return 2  # even complete, passing static checks cannot permit production release


if __name__ == '__main__':
    raise SystemExit(main())
