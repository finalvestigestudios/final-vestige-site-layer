#!/usr/bin/env python3
"""R145: fail-closed, nonpublishing custody audit of Preparedness R133-R144.

No editorial, source, medical, QD, or commercial approval can be inferred from a PASS.
Only --native runs any code from the checked-out tree, inside a temporary copy.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile

EXPECTED_PRS = (1025, 1031, 1037, 1043, 1049, 1057, 1063, 1069, 1076, 1083, 1090, 1096)
EXPECTED_HEADS = (
 '233ba9876b88508d103c5d7fe13906dd975eabc5',
 '8bcd67a2b14b9c3d91aa817ebe59b3afe2b3fa37',
 '072768f207847989c69b10770d83e4e533ce9ba3',
 '52e477b22e1143d4f768369ab7d46265968ccc5a',
 '5a0dfe1067440d7607394ae85b9c2cb6f21b7014',
 '5ea94442b56ec040e8846d784032d38200cd7dae',
 'f88ec21534cf6166e52adab3ed246cdc89f09198',
 'b7f81c8ad6963b7f44fe8898d6bca12f4c562634',
 'b2cac019fb9c85e8555ff4cf0c24aa996a415041',
 '4662ecd45d7ad4ccf55e40fced76fb909f838542',
 'a1dcbf98aec0f1ae07f83f590896603a995e2e99',
 'ee0dcc6e3ad7a3c63a52b1327b99310d3e7e4edc',
)
ANCHOR = '5685b54796d520e8dd50e0cdf4d35e38c9cec7a4'
FROZEN_RC = 'ddb3528ba6494dada1fa1c3a142ce746e3a67706'
R133_LOCK_BLOB = '3eead06268a9a69eeb3130dcdcc8588bd95e980c'
CONTRIBUTORS = {
 'claude/prep-start-bbfeb8': '2122d856fce9f64887c16df3d52e64be9f59a55b',
 'claude/prep-shelter-5e1e0e': '5daeaf2dd5ab71806a6b73c91edfb1d8df5da976',
 'claude/prep-food-ccdc55': 'f911ff7a655de8d81535ea86ec3d65a49ee76648',
 'claude/prep-health-837444': 'd5ef5bafd68361434dd1cc9209915b8e8a4eaf17',
 'claude/prep-hist-food-b81f19': '67e116e536c7410bed30f8f3b1bb8c166f3c223d',
 'claude/prep-hist-home-0e0e38': '7504a5f099594d635e3dd7332a33a2e1346c43a2',
 'claude/prep-hist-field-9db767': '4e5caf812727953aa45e3bda2d382f2c67b6a09c',
}
INDEPENDENT_REFS = {
 'qa157': '7d1ae6b8ef93d10cfb6810987672360885e9c1aa',
 'fixtures169': 'e9cd7766dac59d47ab467d8945269b9146c2aef5',
 'fixture_fix973': '4d40996a559b0124d74a9bb3bdcd481ad1992aa8',
 'home49': '10495883299d53596992c26a8987f629b2904670',
 'home604': 'bdf01b4a3e13fd6179ae9e847c9d4429bbe16176',
}
LOCK_PATH = 'preparedness/docs/r133/locked_files.json'
CITE = re.compile(r'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
BAD_CITE = re.compile(r'\{\{cite:')
SHA = re.compile(r'^[0-9a-f]{40}$')
SAFE_FILE = re.compile(r'^preparedness/(?:docs/r(\d{3})/[A-Za-z0-9_.-]+|tools/r(\d{3})_[A-Za-z0-9_.-]+\.py|tests/test_r(\d{3})_[A-Za-z0-9_.-]+\.py)$')

class Hold(ValueError):
    pass

def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise Hold(message)

def validate_plan(m: dict) -> dict:
    """Validate the independent immutable GitHub snapshot, never approvals."""
    _assert(isinstance(m, dict), 'manifest must be object')
    _assert(m.get('schema') == 'FV-PREP-R145-STACK-1', 'schema mismatch')
    _assert(m.get('anchor') == ANCHOR and m.get('frozen_rc') == FROZEN_RC, 'source ancestry pin mismatch')
    _assert(m.get('release') == 'DRAFT_HOLD', 'release hold missing')
    for key in ('may_publish', 'qd_pass', 'medical_safety_verified', 'merchant_offer_verified', 'automatic_merge'):
        _assert(m.get(key) is False, f'false approval flag: {key}')
    _assert(m.get('contributors') == CONTRIBUTORS and m.get('independent_refs') == INDEPENDENT_REFS,
            'seven contributor / independent QA / homepage reference pins changed')
    _assert(m.get('issues') == [136, 820, 818], 'governance cross-reference missing')
    _assert(m.get('expected_articles') == 35 and m.get('expected_citations') == 2000,
            'article/citation custody baseline mismatch')
    chain = m.get('chain')
    _assert(isinstance(chain, list) and len(chain) == 12, '12 stages required')
    union, previous = set(), ANCHOR
    for idx, row in enumerate(chain):
        _assert(isinstance(row, dict), f'stage {idx}: object required')
        round_id, pr, sha = idx + 133, EXPECTED_PRS[idx], EXPECTED_HEADS[idx]
        _assert(type(row.get('round')) is int and row['round'] == round_id, f'round order mismatch: {round_id}')
        _assert(type(row.get('pr')) is int and row['pr'] == pr, f'PR number mismatch: R{round_id}')
        _assert(row.get('draft') is True and row.get('state') == 'open', f'not open draft R{round_id}')
        _assert(row.get('parent') == previous and row.get('head') == sha, f'chain identity mismatch R{round_id}')
        _assert(isinstance(row.get('files'), list) and len(row['files']) >= 3, f'file inventory missing R{round_id}')
        kinds = set()
        for path in row['files']:
            _assert(isinstance(path,str) and path == path.strip() and '\\' not in path, 'invalid path')
            match = SAFE_FILE.fullmatch(path)
            _assert(match is not None, f'unsafe or non-review path {path}')
            _assert(round_id == int(next(g for g in match.groups() if g)), f'wrong round file path {path}')
            _assert(path not in union, f'duplicate path {path}')
            kinds.add(path.split('/')[1]);union.add(path)
        _assert(kinds == {'docs','tools','tests'}, f'incomplete tool/test/doc R{round_id}')
        previous = sha
    _assert(len(union) == 41, f'aggregate file count changed: {len(union)}')
    return {'chain_stages': 12, 'expected_added_files': 41, 'last_review_commit': previous,
            'release': 'DRAFT_HOLD', 'publication_allowed': False, 'independent_qd': 'NOT_APPROVED'}

def git(repo: Path, *args: str) -> str:
    p = subprocess.run(['git', '-C', str(repo), *args], text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45)
    if p.returncode:
        raise Hold('git verification unavailable/failure (' + ' '.join(args[:3]) + '): ' + p.stderr.strip()[:220])
    return p.stdout

def _diff(repo: Path, old: str, new: str) -> dict[str,str]:
    result = {}
    for line in git(repo,'diff','--name-status','--no-renames',old,new,'--','preparedness/').splitlines():
        parts=line.split('\t')
        _assert(len(parts)==2 and parts[0]=='A' and parts[1] not in result,
                f'modified/deleted/renamed review file: {line}')
        result[parts[1]]=parts[0]
    return result

def inspect_checkout(root: Path, manifest: dict) -> dict:
    report = validate_plan(manifest)
    _assert(git(root,'rev-parse','--is-inside-work-tree').strip() == 'true', 'not a checkout')
    head=git(root,'rev-parse','HEAD').strip()
    _assert(SHA.fullmatch(head) is not None, 'invalid checkout HEAD')
    git(root,'merge-base','--is-ancestor',EXPECTED_HEADS[-1],head)
    union=set()
    for row in manifest['chain']:
        expected=set(row['files'])
        observed=set(_diff(root,row['parent'],row['head']))
        _assert(observed==expected, f'R{row["round"]}: actual Git file set differs from frozen review inventory')
        union.update(observed)
    observed=set(_diff(root,ANCHOR,EXPECTED_HEADS[-1]))
    _assert(observed==union, 'complete additive-only Git diff does not match all twelve PRs')
    _assert(git(root,'rev-parse',f'{EXPECTED_HEADS[-1]}:{LOCK_PATH}').strip()==R133_LOCK_BLOB,
            'R133 immutable article/source list itself was altered')
    locked=json.loads(git(root,'show',f'{EXPECTED_HEADS[-1]}:{LOCK_PATH}'))
    _assert(locked.get('source_release_candidate')==FROZEN_RC and locked.get('candidate_parent')==ANCHOR,
            'R133 lock identity changed')
    _assert(locked.get('expected_citation_occurrences')==2000, 'R133 citation count mismatch')
    for flag in ('qd_pass','may_publish','medical_safety_verified','merchant_offer_verified'):
        _assert(locked.get(flag) is False, f'R133 {flag} improperly approved')
    files=locked.get('files')
    _assert(isinstance(files,list) and len(files)==80,'R133 source-custody file count changed')
    slug_meta={}; slugs=set(); total_citations=0; source_relations=0
    for row in files:
        p=row.get('path','')
        s=row.get('blob_sha','')
        _assert(isinstance(p,str) and p.startswith('preparedness/') and '..' not in p and SHA.fullmatch(s),
                'malformed locked-file entry')
        _assert(git(root,'rev-parse',f'{EXPECTED_HEADS[-1]}:{p}').strip()==s,
                f'original article or evidence blob changed: {p}')
        if p.endswith('.meta.json') and '/articles/' in p:
            meta=json.loads(git(root,'show',f'{EXPECTED_HEADS[-1]}:{p}'))
            slug=meta.get('slug')
            _assert(isinstance(slug,str) and re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',slug), f'bad slug {p}')
            _assert(slug not in slugs, f'duplicate article URL slug {slug}')
            slugs.add(slug);slug_meta[slug]=meta
            _assert(meta.get('status',{}).get('publish')=='draft',f'published article {slug}')
            _assert(meta.get('safety_review',{}).get('state') in {'pending','approved','not-required'},
                    f'unknown safety state {slug}')
            _assert(isinstance(meta.get('source_use'),dict) and meta['source_use'],f'missing author source-use {slug}')
            source_relations+=len(meta['source_use'])
    _assert(len(slugs)==35, f'incomplete article metadata {len(slugs)}')
    for row in files:
        p=row.get('path','')
        if p.endswith('.body.html') and '/articles/' in p:
            slug=Path(p).name.removesuffix('.body.html')
            _assert(slug in slug_meta,f'orphan article body {slug}')
            body=git(root,'show',f'{EXPECTED_HEADS[-1]}:{p}')
            cites=CITE.findall(body)
            _assert(len(cites)==len(BAD_CITE.findall(body)),f'malformed citation token in {slug}')
            _assert(set(cites)==set(slug_meta[slug]['source_use']), f'citation/source-use mismatch {slug}')
            total_citations+=len(cites)
    _assert(total_citations==2000,f'citation occurrences changed: {total_citations}')
    report.update({'verified_lock_blobs':80, 'verified_article_bodies':35,
                   'verified_article_metadata':35, 'source_use_relationships':source_relations,
                   'verified_citation_occurrences':total_citations,'working_head':head,
                   'status':'STRUCTURAL_CHECKS_PASS_RELEASE_HOLD'})
    return report

def run_native_snapshot(root: Path, head: str) -> list[dict]:
    """Run actual native checks only in extracted temporary snapshot, no CMS/network writes."""
    completed=[]
    with tempfile.TemporaryDirectory(prefix='fv-prep-r145-') as temp:
        staging=Path(temp)/'checkout'; staging.mkdir()
        archive=subprocess.run(['git','-C',str(root),'archive','--format=tar',head,'preparedness'],capture_output=True,timeout=90)
        if archive.returncode:
            raise Hold('git archive failed: '+archive.stderr.decode('utf8','replace')[:160])
        with tarfile.open(fileobj=io.BytesIO(archive.stdout),mode='r:') as tf:
            members=tf.getmembers()
            _assert(len(members)<12000 and all(
                (member.isfile() or member.isdir()) and not member.name.startswith('/')
                and '..' not in Path(member.name).parts and not member.issym() for member in members),
                'unsafe snapshot archive entry')
            tf.extractall(staging, filter='data')
        commands=(
          [sys.executable,'-I','preparedness/tools/validate.py'],
          [sys.executable,'-I','preparedness/tools/build.py'],
          [sys.executable,'-I','-m','unittest','discover','-s','preparedness/tests','-v'],
        )
        for command in commands:
            p=subprocess.run(command,cwd=staging,capture_output=True,text=True,timeout=180)
            completed.append({'command':' '.join(command[1:]),'exit_code':p.returncode,
                              'stdout_tail':p.stdout[-1000:],'stderr_tail':p.stderr[-1000:]})
            if p.returncode:
                break
    return completed

def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--repo',type=Path,default=Path('.'))
    parser.add_argument('--native',action='store_true',help='run native checks in isolated temporary archive only')
    args=parser.parse_args(argv)
    status=2
    output={'schema':'FV-PREP-R145-RESULT-1','release':'DRAFT_HOLD',
            'automatic_merge':False,'publication_allowed':False,'qualified_medical_review':'REQUIRED',
            'independent_qd':'NOT_APPROVED','paid_offer_verified':False}
    try:
        manifest=json.loads(args.manifest.read_text(encoding='utf8'))
        output.update(inspect_checkout(args.repo,manifest))
        if args.native:
            output['native_tests']=run_native_snapshot(args.repo,output['working_head'])
            _assert(all(x['exit_code']==0 for x in output['native_tests']) and len(output['native_tests'])==3,
                    'native validation/build/tests did not all pass')
        status=0
    except (OSError,UnicodeError,ValueError,subprocess.SubprocessError,tarfile.TarError,TypeError) as exc:
        output['status']='HOLD';output['error']=str(exc)
    print(json.dumps(output,indent=2,sort_keys=True))
    return status
if __name__=='__main__':
    raise SystemExit(main())
