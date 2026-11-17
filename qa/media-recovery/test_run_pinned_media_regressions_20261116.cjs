'use strict';
const test=require('node:test');const assert=require('node:assert/strict');
const fs=require('node:fs');const os=require('node:os');const path=require('node:path');
const {gitBlob,validateManifest,parseTap,execute,SCHEMA}=require('./run_pinned_media_regressions_20261116.cjs');
const copy=x=>JSON.parse(JSON.stringify(x));
function fixture(){
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'fv-media-offline-'));
 const suites=[];
 for(let i=1;i<=5;i++){
  const name='test_synthetic_'+i+'.cjs',dep='validate_synthetic_'+i+'.cjs';
  const data="'use strict';\nconst test=require('node:test');test('synthetic suite "+i+"',()=>{});\n";
  const depData='module.exports={fixture:'+i+'};\n';
  fs.writeFileSync(path.join(dir,name),data);fs.writeFileSync(path.join(dir,dep),depData);
  suites.push({id:'synthetic-'+i,expected_tests:1,files:[{role:'test',name,git_blob_sha:gitBlob(Buffer.from(data))},{role:'dependency',name:dep,git_blob_sha:gitBlob(Buffer.from(depData))}]});
 }
 const manifest={schema:SCHEMA,network_access:false,production_write_authorized:false,browser_evidence_collected:false,actual_savings_measured:false,suites};
 return {dir,manifest,close:()=>fs.rmSync(dir,{recursive:true,force:true})};
}
test('five pinned synthetic suites run under native node with exact counts',()=>{const f=fixture();try{const r=execute(f.manifest,f.dir);assert.equal(r.status,'PASS');assert.equal(r.passed_tests,5);assert.equal(r.suites.length,5);assert.equal(r.guest_browser_status_observed,false);assert.equal(r.wordpress_writes,0);}finally{f.close();}});
test('modified file blocks all tests before spawning',()=>{const f=fixture();try{fs.appendFileSync(path.join(f.dir,f.manifest.suites[4].files[1].name),' ');let ran=false;assert.throws(()=>execute(f.manifest,f.dir,{spawn:()=>{ran=true;}}),/HOLD: blob mismatch/);assert.equal(ran,false);}finally{f.close();}});
test('claims of browser evidence are rejected',()=>{const f=fixture();try{f.manifest.browser_evidence_collected=true;assert.throws(()=>validateManifest(f.manifest,f.dir),/HOLD:/);}finally{f.close();}});
test('measured savings may not be fabricated',()=>{const f=fixture();try{f.manifest.actual_savings_measured=true;assert.throws(()=>validateManifest(f.manifest,f.dir),/HOLD:/);}finally{f.close();}});
test('production writes cannot be authorized',()=>{const f=fixture();try{f.manifest.production_write_authorized=true;assert.throws(()=>validateManifest(f.manifest,f.dir),/HOLD:/);}finally{f.close();}});
test('network access may not be authorized',()=>{const f=fixture();try{f.manifest.network_access=true;assert.throws(()=>validateManifest(f.manifest,f.dir),/HOLD:/);}finally{f.close();}});
test('path traversal rejected',()=>{const f=fixture();try{f.manifest.suites[0].files[0].name='../test_rogue.cjs';assert.throws(()=>validateManifest(f.manifest,f.dir),/HOLD:/);}finally{f.close();}});
test('duplicate test file rejected',()=>{const f=fixture();try{f.manifest.suites[1].files[0]=copy(f.manifest.suites[0].files[0]);assert.throws(()=>validateManifest(f.manifest,f.dir),/HOLD:/);}finally{f.close();}});
test('wrong expected test count fails closed',()=>{const f=fixture();try{f.manifest.suites[0].expected_tests=42;const r=execute(f.manifest,f.dir);assert.equal(r.status,'FAIL_CLOSED');assert.equal(r.suites[0].status,'FAIL_CLOSED');}finally{f.close();}});
test('nonzero subprocess status fails closed',()=>{const f=fixture();try{const r=execute(f.manifest,f.dir,{spawn:()=>({status:2,stdout:'# tests 1\n# pass 1\n# fail 0\n# skipped 0\n# cancelled 0\n',stderr:''})});assert.equal(r.status,'FAIL_CLOSED');}finally{f.close();}});
test('skipped tests fail closed even on exit zero',()=>{const f=fixture();try{const r=execute(f.manifest,f.dir,{spawn:()=>({status:0,stdout:'# tests 1\n# pass 1\n# fail 0\n# skipped 1\n# cancelled 0\n',stderr:''})});assert.equal(r.status,'FAIL_CLOSED');}finally{f.close();}});
test('TAP parsing does not trust synthetic status alone',()=>{assert.deepEqual(parseTap('hello'),{tests:null,pass:null,fail:null,skipped:null,cancelled:null});});
test('Git blob uses correct git object format',()=>{assert.equal(gitBlob(Buffer.from('hello\n')),'ce013625030ba8dba906f756967f9e9ca394464a');});
