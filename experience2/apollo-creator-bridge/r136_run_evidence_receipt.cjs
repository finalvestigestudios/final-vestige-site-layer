#!/usr/bin/env node
'use strict';
/**
 * R136: read-only deterministic gate receipt built from actual GitHub source.
 * No external calls, CMS writes, marketing SDKs, emails, or paid-order invention.
 * node experience2/apollo-creator-bridge/r136_run_evidence_receipt.cjs --out /tmp/apollo-r136
 */
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const {auditRoute}=require('./r129_creator_route_gate.cjs');
const {auditMediaLedger}=require('./r130_nasa_media_custody_gate.cjs');
const {audit: auditResearch}=require('./r132_research_desk_source_role_gate.cjs');
const {assess}=require('./r136_conversion_evidence_gate.cjs');
const dir=__dirname;
const SHA=x=>crypto.createHash('sha256').update(x).digest('hex');
function run({root=dir,outDir=null}={}){
 const inputNames=['landing-preview.html','r130_nasa_media_custody.json',
   'r132_research_desk_source_role_review.html'];
 const contents=inputNames.map(x=>fs.readFileSync(path.join(root,x),'utf8'));
 const landing=contents[0],media=JSON.parse(contents[1]),desk=contents[2];
 const route=auditRoute(landing);
 const mediaAudit=auditMediaLedger(media,landing);
 const deskAudit=auditResearch(desk);
 const report=assess({landingHtml:landing,routeAudit:route,
  mediaAudit,researchAudit:deskAudit,offer:null,campaign:null,
  browserReceipt:null,merchantReceipts:null});
 const checks={route:route.status,media:mediaAudit.status,
  research_desk:deskAudit.status,editorial_custody:report.editorial_custody,
  browser:'NOT_EXECUTED',commercial:'NOT_ACTIVATED'};
 // This receipt never upgrades a source test into a release gate.
 const receipt={schema:'fv.apollo.r136.deterministic-evidence-receipt.v1',
  source_inputs:Object.fromEntries(inputNames.map((name,i)=>[name,SHA(contents[i])])),
  checks,conversion_evidence:report,
  qa:{playwright:'NOT_RUN',axe:'NOT_RUN',lcp_cls:'NOT_MEASURED',
   screenshots:'NOT_GENERATED',source_tests:'EXECUTED_NATIVE_NODE'},
  release:'STAGING_HOLD',no_wordpress_writes:true,
  independent_merchant_verification:false};
 let artifact=null;
 if(outDir){
  fs.mkdirSync(outDir,{recursive:true});
  const payload=JSON.stringify(receipt,null,2)+'\n';
  artifact=path.join(outDir,'r136-evidence-to-offer-receipt.json');
  fs.writeFileSync(artifact,payload);
  fs.writeFileSync(path.join(outDir,'r136-evidence-to-offer-manifest.json'),
   JSON.stringify({schema:'fv.apollo.r136.manifest.v1',
    artifact_sha256:SHA(payload),source_inputs:receipt.source_inputs,
    release:'STAGING_HOLD'},null,2)+'\n');
 }
 return {receipt,artifact};
}
if(require.main===module){
 let outDir=null;
 if(process.argv.length>2){
  if(process.argv.length!==4||process.argv[2]!=='--out')
   throw Error('usage: node r136_run_evidence_receipt.cjs [--out directory]');
  outDir=path.resolve(process.argv[3]);
 }
 try{
  const r=run({outDir});
  process.stdout.write(JSON.stringify(r.receipt,null,2)+'\n');
  if(r.receipt.checks.editorial_custody!=='SOURCE_GATE_PASS_ONLY')
   process.exitCode=2;
  // Even a passing source gate NEVER means production or commerce authorization.
 }catch(e){process.stderr.write('R136_SOURCE_AUDIT_BLOCKED: '+e.message+'\n');process.exitCode=2;}
}
module.exports={run};
