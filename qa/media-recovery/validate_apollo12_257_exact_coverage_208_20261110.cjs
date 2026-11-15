"use strict";
/* Draft-only, offline, read-only. Never classifies a retriever error as a browser failure. */
const fs = require("node:fs");
const path = require("node:path");
const slots = Array.from({length:7},(_,i)=>"257:"+i);
const fail = (why)=>{ throw Error("MEDIA_HOLD: "+why); };
const eq = (a,b,label)=>{if(a!==b) fail(label);};
const same = (a,b)=>JSON.stringify(a)===JSON.stringify(b);
function validate(audit, current, previous) {
  eq(audit.schema,"fv-media-apollo12-seven-v1","audit schema");
  eq(current.schema,"fv-media-exact-coverage-208-v1","register schema");
  eq(previous.schema,"fv-media-exact-coverage-201-v1","previous register schema");
  eq(audit.rows.length,7,"seven rows");
  eq(current.rows.length,288,"register 288 slots");
  eq(previous.rows.length,288,"prior 288 slots");
  eq(current.frozen_source.blob_sha,previous.frozen_source.blob_sha,"frozen source identity");
  eq(audit.claimed_42_broken_verified,false,"42 not confirmed");
  eq(audit.claimed_76_percent_wire_savings_measured,false,"76 percent not measured");
  eq(current.counts.researched_unique,208,"researched count");
  eq(current.counts.unresearched,80,"pending count");
  eq(current.counts.total_external,288,"total count");
  eq(current.counts.total_evidence_records,213,"evidence count");
  eq(current.counts.guest_browser_confirmed_broken,0,"guest broken unverified");
  eq(current.counts.guest_browser_confirmed_loaded,0,"guest loaded unverified");
  eq(current.counts.wire_reduction_76_percent_measured,false,"no wire savings claim");
  eq(current.counts.oversized_wp_originals_gt_1500000,15,"large originals");
  eq(current.counts.oversized_stored_original_bytes,47096779,"stored bytes, not transferred");
  const map=new Map(audit.rows.map(r=>[r.slot,r]));
  eq(map.size,7,"unique audit slots");
  let changes=0, researched=0, evidence=0;
  for(let i=0;i<current.rows.length;i++){
    const now=current.rows[i],old=previous.rows[i],r=map.get(now.slot);
    eq(now.slot,old.slot,"stable ordering");
    if(!r) {if(!same(now,old))fail("non-target source changed: "+now.slot);}
    else {
      changes++;
      if(!slots.includes(now.slot)) fail("unexpected target");
      eq(old.evidence.length,0,"source must previously be pending");
      eq(now.stored_url,old.stored_url,"immutable original URL");
      eq(r.published_src,old.stored_url,"audit source binding");
      eq(r.post_url,old.post_url,"post URL binding");
      eq(r.post_id,257,"post ID");
      eq(r.catalog_retriever,"HTML_ACCESSIBLE","catalog method");
      eq(r.original_source_retriever,"TEXT_RETRIEVER_INACCESSIBLE_NOT_HTTP","retriever method");
      const [w,h]=r.original_catalog_px,[ow,oh]=r.conditional_max_960_px;
      if(!Number.isInteger(w)||w<1||!Number.isInteger(h)||h<1) fail("catalog dimensions");
      if(!Number.isInteger(ow)||!Number.isInteger(oh)||ow>960||ow>w||oh>h||Math.abs(oh-(h*ow/w))>0.51) fail("960px/no-upscale geometry");
      if(now.slot==="257:6" && (w!==800||ow!==800||h!==800||oh!==800))fail("LRO 800px original is never enlarged");
      if(now.slot==="257:4" && !r.visual_integrity_notes.includes("legibility"))fail("diagram text gate");
      if(now.slot==="257:6" && !r.archival_context.includes("2009"))fail("LRO chronological gate");
      if(now.slot==="257:0" && !r.visual_integrity_notes.includes("not proven literal channel contact"))fail("unverified pad contact");
      for(const key of ["origin_http_status","guest_browser_http_status","guest_current_src","guest_decoded_px","guest_wire_bytes","guest_broken"])if(r[key]!==null)fail("invented image visitor evidence: "+now.slot+":"+key);
      for(const key of ["license_clearance","download_authorized","cache_authorized","wordpress_upload_authorized","post_block_rewrite_authorized","archive_exact_binary_identity_verified"])if(r[key]!==false)fail("unapproved release or identity: "+now.slot+":"+key);
      if(now.evidence.length!==1||now.candidate_sources.length!==1)fail("exactly one new catalog record");
      eq(now.evidence[0].retriever_only_observation,r.original_source_retriever,"status semantics");
      eq(now.candidate_sources[0].catalog_url,r.catalog_url,"catalog parity");
      eq(now.candidate_sources[0].exact_image_match_verified,false,"no binary match");
      eq(now.candidate_sources[0].item_rights_cleared,false,"no rights");
    }
    evidence+=now.evidence.length;
    if(now.evidence.length)researched++;
    for(const key of ["guest_http_status","guest_current_src","guest_decoded_px","guest_wire_bytes","guest_broken"])if(now[key]!==null)fail("register visitor evidence invented "+now.slot);
    for(const key of ["rights_cleared","exact_pixel_match_verified","download_authorized","cache_authorized","wordpress_media_upload_authorized","post_rewrite_authorized"])if(now[key]!==false)fail("register release gate "+now.slot);
  }
  eq(changes,7,"exact seven source changes");
  eq(researched,208,"recount unique investigated");
  eq(evidence,213,"recount research evidence");
  return {changed:changes,researched,pending:288-researched,evidence_rows:evidence,validated:true};
}
module.exports={validate};
if(require.main===module){
 const dir=__dirname;
 const audit=JSON.parse(fs.readFileSync(path.join(dir,"apollo12_257_seven_nasa_20261110.json"),"utf8"));
 const next=JSON.parse(fs.readFileSync(path.join(dir,"coverage_208_exact_pr1703_20261110.json"),"utf8"));
 const prior=JSON.parse(fs.readFileSync(path.join(dir,"coverage_201_exact_pr1703_20261110.json"),"utf8"));
 console.log(JSON.stringify(validate(audit,next,prior)));
}
