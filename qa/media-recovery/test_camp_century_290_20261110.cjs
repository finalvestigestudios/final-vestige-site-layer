"use strict";
// Run with: node qa/media-recovery/test_camp_century_290_20261110.cjs
// Deterministic, offline regression; requires no browser, login, network or image downloads.
function runTests(previous,audit,current,auditBlobSha,validate) {
  const failures=[];let checks=0;
  function check(name,fn) {checks++;try{if(!fn())failures.push(name);}catch(e){failures.push(name+": "+e.message);}}
  const copy=x=>JSON.parse(JSON.stringify(x));
  const baseline=()=>validate(previous,audit,current,auditBlobSha).ok;
  check("valid baseline",baseline);
  check("61-post census untouched",()=>current.frozen_source.posts===61);
  check("355 inline refs untouched",()=>current.frozen_source.inline_images===355);
  check("288 external positions",()=>current.rows.length===288);
  check("269 researched",()=>current.rows.filter(x=>x.evidence.length).length===269);
  check("19 pending",()=>current.rows.filter(x=>!x.evidence.length).length===19);
  check("six original URLs exactly match",()=>audit.rows.every(x=>previous.rows.find(r=>r.slot===x.slot)?.stored_url===x.original_url));
  check("six live ALTs captured",()=>audit.rows.every(x=>x.live_alt.length>10));
  check("one inaccessible image NOT guest 404",()=>audit.rows[5].web_retriever_wrapper_code==="DisabledError"&&audit.rows[5].guest_http_status===null);
  check("NASA composite alt provenance",()=>audit.rows[0].proposed_alt.includes("radar")&&audit.rows[0].proposed_alt.includes("wing"));
  check("Army 1960-63 diagram not photographed steel",()=>audit.rows[2].proposed_alt.includes("cross-sections")&&audit.rows[2].diagram_label_legibility_hold);
  check("map legibility hold",()=>audit.rows[3].diagram_label_legibility_hold);
  check("commercial press-only archive gated",()=>audit.rows[4].rights_review.includes("NOT commercial")&&!audit.rows[4].rights_cleared);
  check("2017 research chart license gated",()=>audit.rows[5].rights_review.includes("unverified")&&!audit.rows[5].cache_authorized);
  check("NASA candidate width 960",()=>audit.rows[0].conditional_max960_px[0]===960);
  check("original Army cross-section 1573",()=>audit.rows[2].candidate_native_px[0]===1573);
  check("no arbitrary upscaling",()=>audit.rows.every(x=>!x.candidate_native_px || x.conditional_max960_px[0]<=Math.min(960,x.candidate_native_px[0])));
  check("no WP rights granted",()=>audit.rows.every(x=>!x.wordpress_media_upload_authorized&&!x.post_rewrite_authorized));
  check("unchanged external-p0 queue",()=>JSON.stringify(previous.original_six_p0_guest_queue)===JSON.stringify(current.original_six_p0_guest_queue));
  const mustFail=(name,mutate)=>check(name,()=>{const p=copy(previous),a=copy(audit),c=copy(current);mutate(p,a,c);return !validate(p,a,c,auditBlobSha).ok;});
  mustFail("reject altered original URL",(p,a)=>{a.rows[0].original_url="https://invalid.example.com/fake.jpg"});
  mustFail("reject altered current URL",(p,a,c)=>{c.rows.find(x=>x.slot==="290:0").stored_url="https://invalid.example.com/a.jpg"});
  mustFail("reject fabricated HTTP status",(p,a)=>{a.rows[5].guest_http_status=404});
  mustFail("reject fabricated transferred bytes",(p,a)=>{a.rows[0].guest_wire_bytes=500});
  mustFail("reject cache consent",(p,a)=>{a.rows[1].cache_authorized=true});
  mustFail("reject rights clearance",(p,a)=>{a.rows[4].rights_cleared=true});
  mustFail("reject production overwrite consent",(p,a)=>{a.rows[0].post_rewrite_authorized=true});
  mustFail("reject wrong audit SHA",(p,a,c)=>{c.rows.find(x=>x.slot==="290:0").evidence[0].blob_sha="fake"});
  mustFail("reject changed unrelated row",(p,a,c)=>{c.rows.find(x=>x.slot==="101:1").origin_host="evil.example"});
  mustFail("reject image enlargement",(p,a)=>{a.rows[2].conditional_max960_px=[1200,864]});
  mustFail("reject guest failure count claim",(p,a,c)=>{c.counts.guest_browser_confirmed_broken=1});
  mustFail("reject publication authorization",(p,a)=>{a.publication_authorized=true});
  mustFail("reject altered P0 queue",(p,a,c)=>{c.original_six_p0_guest_queue.reverse()});
  return {passed:checks-failures.length,total:checks,failures};
}
module.exports = {runTests};
if (require.main === module) {
  const fs=require("node:fs");
  const dir=__dirname, root=dir+"/";
  const base=JSON.parse(fs.readFileSync(root+"coverage_263_exact_pr1703_20261110.json","utf8"));
  const audit=JSON.parse(fs.readFileSync(root+"camp_century_290_six_nasa_usace_geus_20261110.json","utf8"));
  const curr=JSON.parse(fs.readFileSync(root+"coverage_269_exact_pr1703_20261110.json","utf8"));
  const {validate}=require("./validate_camp_century_290_20261110.cjs");
  const crypto=require("node:crypto");
  const content=fs.readFileSync(root+"camp_century_290_six_nasa_usace_geus_20261110.json");
  const sha=crypto.createHash("sha1").update(Buffer.concat([Buffer.from("blob "+content.length+"\0"),content])).digest("hex");
  const r=runTests(base,audit,curr,sha,validate);
  console.log(JSON.stringify(r)); if(r.failures.length) process.exitCode=1;
}
