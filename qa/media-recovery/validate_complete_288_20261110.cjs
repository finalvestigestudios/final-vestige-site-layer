"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const ROOT=path.resolve(__dirname,"../..");
const read=p=>JSON.parse(fs.readFileSync(path.join(ROOT,p),"utf8"));
const AUDIT="qa/media-recovery/remaining_14_all_primary_provenance_live_20261110.json", REG="qa/media-recovery/coverage_288_exact_pr1703_20261110.json", PRIOR="qa/media-recovery/coverage_274_exact_pr1703_20261110.json";
function validate(a=read(AUDIT),r=read(REG),p=read(PRIOR)){
 const errors=[], chk=(cond,msg)=>{if(!cond)errors.push(msg)};
 const priorMap=new Map(p.rows.map(x=>[x.slot,x]));
 const rows=a.rows, k=new Set(rows.map(x=>x.slot));
 chk(rows.length===14&&k.size===14,"final batch must contain exactly 14 unique rows");
 chk(r.rows.length===288&&new Set(r.rows.map(x=>x.slot)).size===288,"register requires 288 distinct positions");
 chk(r.counts.researched_unique===288&&r.counts.unresearched===0,"count must be 288/288");
 chk(r.counts.total_evidence_records===r.rows.reduce((n,x)=>n+x.evidence.length,0),"evidence count mismatch");
 chk(a.counts.displayed_in_retriever===rows.filter(x=>x.retriever_status==="IMAGE_DISPLAYED").length,"displayed count");
 chk(a.counts.unavailable_in_retriever===rows.filter(x=>x.retriever_status==="RETRIEVER_UNAVAILABLE").length,"unavailable count");
 for(const x of rows){
  const old=priorMap.get(x.slot), nr=r.rows.find(y=>y.slot===x.slot);
  chk(!!old&&old.evidence.length===0,"batch slot not previously unresearched "+x.slot);
  chk(!!nr&&nr.stored_url===x.original_url&&x.live_source_exact_frozen===true,"src drift "+x.slot);
  chk(!!nr&&nr.evidence.length===1&&nr.evidence[0].batch==="final14","missing evidence "+x.slot);
  chk(x.origin_http_status===null&&x.guest_http_status===null&&x.guest_wire_bytes===null&&x.guest_broken===null,"invented network result "+x.slot);
  chk(x.rights_cleared===false&&x.download_authorized===false&&x.cache_authorized===false&&x.wordpress_media_upload_authorized===false&&x.post_rewrite_authorized===false,"authorization changed "+x.slot);
  chk(x.candidate_exact_binary_match_verified===false,"binary match assertion "+x.slot);
  if(x.conditional_max960_px)chk(x.conditional_max960_px[0]<=960 && x.conditional_max960_px.every(Number.isInteger) && x.conditional_max960_px.every(n=>n>0),"invalid dimensions "+x.slot);
 }
 for(const old of p.rows)if(old.evidence.length)chk(JSON.stringify(old)===JSON.stringify(r.rows.find(x=>x.slot===old.slot)),"non-batch altered "+old.slot);
 chk(r.rows.every(x=>x.evidence.length>0),"unresearched positions remain");
 chk(a.rows.some(x=>x.slot==="288:5"&&x.scene_and_visual_finding.includes("NOT an aerial")),"288:5 integrity finding lost");
 chk(a.rows.some(x=>x.slot==="431:4"&&x.scene_and_visual_finding.includes("1934")),"431:4 time-period integrity finding lost");
 return errors;
}
if(require.main===module){const errors=validate();if(errors.length){console.error(errors.join("\n"));process.exitCode=1;}else console.log("PASS: complete 288-slot archival coverage, no invented guest statuses, fail-closed authorization.");}
module.exports={validate};
