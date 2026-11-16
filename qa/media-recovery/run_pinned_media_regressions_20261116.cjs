'use strict';
// Offline Node-only QA for the existing recovery work. No requests, downloads, WP writes or browsers.
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const {spawnSync}=require('node:child_process');
const SCHEMA='fv-media-pinned-native-regression-v1';
const reject=(why)=>{throw new Error('HOLD: '+why);};
const shaPattern=/^[0-9a-f]{40}$/;
function gitBlob(buffer){return crypto.createHash('sha1').update('blob '+buffer.length+'\0').update(buffer).digest('hex');}
function validateManifest(manifest,dir){
  if(!manifest||manifest.schema!==SCHEMA||!Array.isArray(manifest.suites)||manifest.suites.length!==5)reject('exact five approved suites required');
  if(manifest.network_access!==false||manifest.production_write_authorized!==false||manifest.browser_evidence_collected!==false||manifest.actual_savings_measured!==false)reject('unsafe measurement/permissions claim');
  const ids=new Set(),paths=new Set(),out=[];
  for(const s of manifest.suites){
    if(typeof s.id!=='string'||!/^[-a-z0-9]+$/.test(s.id)||ids.has(s.id))reject('invalid/duplicate suite');ids.add(s.id);
    if(!Number.isSafeInteger(s.expected_tests)||s.expected_tests<1||s.expected_tests>1000)reject('invalid expected count '+s.id);
    if(!Array.isArray(s.files)||s.files.length<2||s.files.length>4)reject('invalid file inventory '+s.id);
    if(s.files.filter(f=>f.role==='test').length!==1)reject('exactly one pinned test per suite '+s.id);
    let testFile=null;const verified=[];
    for(const f of s.files){
      if(!f||typeof f.name!=='string'||!/^(?:test_|validate_|assess_|hebgen_|uscg_|official_|wp66_)[a-z0-9_-]+\.(?:cjs|json)$/.test(f.name)||f.name.includes('..')||paths.has(f.name)||!shaPattern.test(f.git_blob_sha)||!['test','dependency'].includes(f.role))reject('unsafe file record '+s.id);
      paths.add(f.name);
      if(f.role==='test'&&!/^test_[a-z0-9_-]+\.cjs$/.test(f.name))reject('unsafe test filename '+s.id);
      const filename=path.join(dir,f.name);
      if(!fs.existsSync(filename)||!fs.statSync(filename).isFile())reject('missing '+f.name);
      const actual=gitBlob(fs.readFileSync(filename));
      if(actual!==f.git_blob_sha)reject('blob mismatch '+f.name);
      if(f.role==='test')testFile=filename;
      verified.push({file:f.name,git_blob_sha:actual});
    }
    out.push({id:s.id,expected_tests:s.expected_tests,testFile,verified});
  }
  return out;
}
function parseTap(tap){
  const get=(key)=>{const m=tap.match(new RegExp('^# '+key+' (\\d+)$','m'));return m?Number(m[1]):null;};
  return {tests:get('tests'),pass:get('pass'),fail:get('fail'),skipped:get('skipped'),cancelled:get('cancelled')};
}
function execute(manifest,dir,{spawn=spawnSync}={}){
  const suites=validateManifest(manifest,dir); // hard gate: no child test runs before ALL SHA pins pass
  const results=[];
  for(const s of suites){
    const run=spawn(process.execPath,['--test','--test-reporter=tap',s.testFile],{
      cwd:dir,encoding:'utf8',timeout:45000,maxBuffer:2*1024*1024,
      env:{PATH:process.env.PATH||'',HOME:process.env.HOME||'',CI:'1',NODE_OPTIONS:''},shell:false
    });
    const tap=(run.stdout||'')+'\n'+(run.stderr||'');const counts=parseTap(tap);
    const pass=run.status===0&&!run.error&&counts.tests===s.expected_tests&&counts.pass===s.expected_tests&&counts.fail===0&&counts.skipped===0&&counts.cancelled===0;
    results.push({id:s.id,status:pass?'PASS':'FAIL_CLOSED',expected_tests:s.expected_tests,actual:counts,exit_code:run.status,spawn_error:run.error?String(run.error):null,verified_files:s.verified});
  }
  return {schema:SCHEMA,status:results.every(x=>x.status==='PASS')?'PASS':'FAIL_CLOSED',node_version:process.version,passed_tests:results.filter(x=>x.status==='PASS').reduce((n,x)=>n+x.expected_tests,0),suites:results,
    guest_browser_status_observed:false,claims_42_broken_proven:false,claims_76_percent_savings_measured:false,wordpress_writes:0,media_downloads:0};
}
if(require.main===module){
  try{const dir=__dirname;const file=path.join(dir,'pinned_media_regressions_20261116.json');const m=JSON.parse(fs.readFileSync(file,'utf8'));const result=execute(m,dir);process.stdout.write(JSON.stringify(result,null,2)+'\n');if(result.status!=='PASS')process.exitCode=2;}
  catch(e){process.stderr.write(JSON.stringify({schema:SCHEMA,status:'FAIL_CLOSED',error:String(e.message)})+'\n');process.exitCode=2;}
}
module.exports={gitBlob,validateManifest,parseTap,execute,SCHEMA};
