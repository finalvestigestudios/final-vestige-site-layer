'use strict';
// Offline custody check for read-only GitHub content-api observations. NOT a test-runner or browser collector.
const fs=require('node:fs');
const assert=require('node:assert/strict');
const SCHEMA='fv-media-remote-git-custody-v1';
const EXPECTED={
  'hebgen-twin-usgs-originals':35,
  'uscg-scotch-cap-rights':21,
  'p0-official-source-candidates':17,
  'wordpress-oversized-surfaces':17,
  'cold-wire-76-percent-proof':33
};
function hold(s){throw new Error('HOLD: '+s);}
function validate(d){
  if(!d||d.schema!==SCHEMA||d.repository!=='finalvestigestudios/final-vestige-site-layer')hold('schema/repository');
  if(!/^[0-9a-f]{40}$/.test(d.inspected_commit||''))hold('inspected commit');
  if(d.method!=='read-only GitHub fetch_file at exact ref' || d.browser_capture_performed!==false ||
     d.native_node_suites_executed!==false || d.wordpress_writes!==0 || d.media_downloads!==0 ||
     d.subscription_spend_usd!==0 || d.actual_http_statuses_collected!==false ||
     d.confirmed_broken_image_count!==null || d.visitor_bandwidth_savings_percent!==null)hold('unsupported execution/evidence claim');
  if(!Array.isArray(d.suites)||d.suites.length!==5)hold('suite count');
  const names=new Set(), ids=new Set();let expected=0, observedFiles=0;
  for(const suite of d.suites){
    if(!Object.hasOwn(EXPECTED,suite.id)||ids.has(suite.id)||suite.expected_tests!==EXPECTED[suite.id])hold('unknown suite/test count');
    ids.add(suite.id);expected+=suite.expected_tests;
    if(!Array.isArray(suite.files)||suite.files.length<2||suite.files.length>3||suite.files.filter(f=>f.role==='test').length!==1)hold('suite files');
    for(const f of suite.files){
      if(!/^(?:test_|validate_|assess_|hebgen_|uscg_|official_|wp66_)[a-z0-9_-]+\.(?:cjs|json)$/.test(f.name||'') || names.has(f.name))hold('unsafe or duplicate filename');
      names.add(f.name);observedFiles++;
      if(!['test','dependency'].includes(f.role)||!Number.isSafeInteger(f.file_chars)||f.file_chars<100 ||
        !/^[0-9a-f]{40}$/.test(f.git_blob_sha||'') || f.git_blob_sha!==f.fetched_blob_sha || f.match!==true)hold('blob identity mismatch');
    }
  }
  if(expected!==123||observedFiles!==14||d.pinned_files_verified!==14||d.declared_tests_pending!==123)hold('aggregate totals');
  if(d.gate!=='REMOTE_BLOB_IDENTITIES_MATCH__NATIVE_SUITE_NOT_RUN')hold('premature gate');
  return {gate:d.gate,remote_blobs_verified:observedFiles,declared_tests_pending:expected,
    visitor_http_status:null,production_writes:0};
}
if(require.main===module){
  try{const p=process.argv[2];if(!p)hold('usage: node verify_remote_pins_20261116.cjs path.json');
    console.log(JSON.stringify(validate(JSON.parse(fs.readFileSync(p,'utf8'))),null,2));}
  catch(e){console.error(e.message);process.exitCode=2;}
}
module.exports={validate,EXPECTED,SCHEMA};
