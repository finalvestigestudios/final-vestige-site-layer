'use strict';
/** R136 native Node integration checks. Requires complete source checkout. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const os=require('node:os');
const crypto=require('node:crypto');
const {run}=require('./r136_run_evidence_receipt.cjs');
const SHA=x=>crypto.createHash('sha256').update(x).digest('hex');
test('actual landing + six-record NASA custody produces deterministic source receipt',()=>{
 const a=run().receipt,b=run().receipt;
 assert.deepEqual(a,b);
 assert.equal(a.checks.route,'PASS');
 assert.equal(a.checks.media,'PASS_SOURCE_CUSTODY_ONLY');
 assert.equal(a.checks.research_desk,'PASS');
 assert.equal(a.checks.editorial_custody,'SOURCE_GATE_PASS_ONLY');
});
test('source checks never claim live browsers, merchant verification or sales',()=>{
 const a=run().receipt;
 assert.equal(a.release,'STAGING_HOLD');
 assert.equal(a.qa.playwright,'NOT_RUN');
 assert.equal(a.qa.axe,'NOT_RUN');
 assert.equal(a.independent_merchant_verification,false);
 assert.equal(a.conversion_evidence.paid_cta_insertion_authorized,false);
 assert.equal(a.conversion_evidence.measurement.net_revenue_per_1000_qualified_sessions,'NOT_COMPUTABLE');
});
test('real-branch source receipts have matching deterministic manifest SHA256',()=>{
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'fv-r136-'));
 try{
  const x=run({outDir:path.join(tmp,'A')});
  const y=run({outDir:path.join(tmp,'B')});
  const a=fs.readFileSync(x.artifact,'utf8');
  const b=fs.readFileSync(y.artifact,'utf8');
  assert.equal(a,b);
  const manifest=JSON.parse(fs.readFileSync(path.join(tmp,'A','r136-evidence-to-offer-manifest.json'),'utf8'));
  assert.equal(manifest.artifact_sha256,SHA(a));
  assert.equal(manifest.release,'STAGING_HOLD');
  assert.equal(Object.keys(manifest.source_inputs).length,3);
 }finally{fs.rmSync(tmp,{recursive:true,force:true});}
});
test('no tracking, payment, WordPress or network code in local receipt',()=>{
 const src=fs.readFileSync(path.join(__dirname,'r136_run_evidence_receipt.cjs'),'utf8');
 assert.doesNotMatch(src,/\brequire\(['"](?:https?|axios|node:child_process|playwright)['"]\)/);
 assert.doesNotMatch(src,/\b(?:fetch|sendBeacon|postMessage|write_post|wp_insert_post|payhip_api|trackEvent)\s*\(/);
 assert.equal(run().receipt.no_wordpress_writes,true);
});
