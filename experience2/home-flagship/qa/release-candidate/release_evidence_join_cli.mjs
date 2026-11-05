#!/usr/bin/env node
/** Read-only exact-head WordPress+guest evidence JOIN. Local developer only.
 *
 * Usage:
 * node experience2/home-flagship/qa/release-candidate/release_evidence_join_cli.mjs \
 *   --head "$(git rev-parse HEAD)" --stage /tmp/fv-ex2-stage-evidence \
 *   --guest /tmp/fv-focus-guest --out /tmp/fv-release-join.json
 *
 * Never uploads receipts or visitor data. Return code 0 means only that local
 * and guest test receipts are present; release state is ALWAYS HOLD.
 */
import {readFileSync, writeFileSync, lstatSync, statSync, realpathSync} from 'node:fs';
import {dirname, relative, resolve, sep} from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {classifyReleaseEvidence} from './release_evidence_join.mjs';

const REL='experience2/home-flagship/qa/release-candidate/';
function sameGitSource(repo,head,name){
  const file=resolve(repo,REL+name);
  if(!lstatSync(file).isFile()||relative(repo,realpathSync(file)).startsWith('..'))
    throw new Error('UNSAFE_LOCAL_QA_SOURCE');
  const saved=readFileSync(file);
  const committed=execFileSync('git',['-C',repo,'show',head+':'+REL+name],{maxBuffer:300000});
  if(!saved.equals(committed)) throw new Error('QA_SOURCE_NOT_EXACT_GIT_HEAD');
}
function readSmallJson(file){
  const st=lstatSync(file);
  if(!st.isFile()||st.size>3000000)throw new Error('MISSING_OR_UNSAFE_RECEIPT');
  return JSON.parse(readFileSync(file,'utf8'));
}
function argsFrom(argv){
  if(argv.length!==8)throw new Error('REQUIRE_EXACT_FOUR_FLAGS');
  const flags={};
  for(let i=0;i<argv.length;i+=2){
    const k=argv[i];
    if(!['--head','--stage','--guest','--out'].includes(k)||k in flags)
      throw new Error('UNKNOWN_OR_DUPLICATE_FLAG');
    flags[k]=argv[i+1];
  }
  if(Object.keys(flags).length!==4)throw new Error('REQUIRE_EXACT_FOUR_FLAGS');
  return flags;
}
export function main(argv=process.argv.slice(2)){
  const opt=argsFrom(argv);
  const repo=resolve(process.cwd());
  const actual=execFileSync('git',['-C',repo,'rev-parse','HEAD'],{encoding:'utf8'}).trim();
  if(actual!==opt['--head']||!/^[a-f0-9]{40}$/.test(actual))
    throw new Error('WORKTREE_HEAD_MISMATCH');
  for(const n of ['release_evidence_join.mjs','release_evidence_join_cli.mjs',
      'release_evidence_join.test.mjs'])sameGitSource(repo,actual,n);
  const stage=realpathSync(resolve(opt['--stage']));
  const guest=realpathSync(resolve(opt['--guest']));
  const out=resolve(opt['--out']);
  for(const p of [stage,guest,out]){
    const r=relative(repo,p);
    if(!r.startsWith('..'+sep)&&r!== '..')
      throw new Error('OUTPUT_AND_RECEIPTS_MUST_BE_OUTSIDE_REPO');
  }
  if(out===resolve(stage,'EPHEMERAL_WP_CI.json')||out===resolve(guest,'result.json'))
    throw new Error('OUTPUT_MUST_NOT_REPLACE_INPUT');
  const guestResultPath=resolve(guest,'result.json');
  const age=(Date.now()-statSync(guestResultPath).mtimeMs)/3600000;
  const pack={
    sha:actual,
    stage:readSmallJson(resolve(stage,'STAGING_ACCEPTANCE.json')),
    local:readSmallJson(resolve(stage,'EPHEMERAL_WP_CI.json')),
    lighthouse:readSmallJson(resolve(stage,'LIGHTHOUSE_PRIVATE_LAB.json')),
    usability:readSmallJson(resolve(stage,'PRIVATE_USABILITY.json')),
    guest:readSmallJson(guestResultPath),
    guestAgeHours:age
  };
  const result=classifyReleaseEvidence(pack);
  // Source URLs, timestamps, filenames, profile traces, cookies and email
  // values never enter the output; mode 0600, exclusive create, no overwrite.
  writeFileSync(out,JSON.stringify({...result,
    guest_freshness_basis:'LOCAL_RESULT_FILE_MTIME_NOT_CRYPTOGRAPHIC_PROVENANCE',
    captured_artifacts_not_transferred:true},null,2)+'\n',{flag:'wx',mode:0o600});
  process.stdout.write(JSON.stringify({
    classification:result.classification,failures:result.failure_codes,release:'HOLD'})+'\n');
  return result.lab_evidence_satisfied?0:2;
}
if(process.argv[1] && resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  try{process.exitCode=main()}catch(e){
    process.stderr.write('RELEASE_EVIDENCE_JOIN_HOLD: '+(
      e instanceof SyntaxError?'UNPARSEABLE_RECEIPT':
      e?.code==='ENOENT'?'REQUIRED_FILE_MISSING':e?.message||'UNKNOWN_FAILURE'
    ).toString().slice(0,80)+'\n');
    process.exitCode=2;
  }
}
