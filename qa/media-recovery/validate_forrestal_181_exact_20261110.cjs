"use strict";
const slots=["289:0","289:1","289:2","289:3","289:4","289:5"], P0=["285:5","285:2","287:5","418:1","418:2","407:1"];
const dims=[[960,763],null,null,null,[960,639],[960,1446]];
function validateBatch(a,inv){
 const e=[],original=(inv?.images||[]).filter(x=>x.post_id===289);
 if(a?.schema!=="fv-forrestal-289-six-evidence-v1"||a?.rows?.length!==6||original.length!==6)e.push("bad_shape");
 if(a?.inventory?.blob_sha!=="49183f66f880f7c4dfd363acca906876877f2e5e"||a?.observation_totals?.image_rendered!==5||a?.observation_totals?.retriever_403!==1||a?.observation_totals?.confirmed_visitor_broken!==0||a?.observation_totals?.confirmed_visitor_loaded!==0)e.push("bad_evidence_totals");
 if(a?.site_writes!==0||a?.downloaded_binaries!==0||a?.spend_usd!==0)e.push("nonzero_changes");
 for(let k=0;k<6;k++){
  const r=a?.rows?.[k],o=original.find(x=>x.key===slots[k]);
  if(!r||r.slot!==slots[k]||!o){e.push("slot_"+k);continue;}
  if(r.stored_url!==o.source_url||r.stored_alt!==o.alt||r.post_url!==o.post_url||r.host!==o.source_host)e.push("source_"+k);
  const q=r.retrieval||{}, expected=k===4?"WEB_RETRIEVER_403":"IMAGE_RENDERED";
  if(q.method!=="web.open_independent_image_retriever"||q.outcome!==expected||q.retriever_http_code!==(k===4?403:null))e.push("tool_result_"+k);
  for(const f of ["guest_http_status","guest_broken","guest_current_src","guest_decoded_px","guest_wire_bytes","final_origin_redirects"])if(q[f]!==null)e.push("invented_guest_"+k+"_"+f);
  if(q.uncached_guest_verified!==false)e.push("unsupported_cache_"+k);
  const c=r.candidate||{};
  if(!c.catalog_url?.startsWith("https://")||!c.catalog_id||!c.rights_observation||!c.chronology_note||c.exact_binary_match_sha256!==null||c.rights_cleared!==false||c.editorial_match_approved!==false)e.push("unsafe_candidate_"+k);
  if(JSON.stringify(c.conditional_960px)!==JSON.stringify(dims[k]))e.push("wrong_geometry_"+k);
  if(c.catalog_intrinsic_px&&((c.conditional_960px?.[0]||0)>c.catalog_intrinsic_px[0]||(c.conditional_960px?.[1]||0)>c.catalog_intrinsic_px[1]))e.push("upscale_"+k);
  for(const f of ["download","mirror","cache","wordpress_upload","post_block_edit","caption_edit"])if(r.permissions?.[f]!==false)e.push("release_bypass_"+k+"_"+f);
 }
 if(a?.rows?.[4]?.candidate?.catalog_id!=="DVIDS 6947585 / VIRIN 210811-N-SG189-1105"||!a.rows[4].candidate.chronology_note.includes("2021"))e.push("training_misdated");
 if(a?.rows?.[5]?.candidate?.catalog_id!=="DVIDS 985674 / VIRIN 130726-N-ST310-007"||!a.rows[5].candidate.chronology_note.includes("2013"))e.push("memorial_misdated");
 if(a?.rows?.[1]?.candidate?.relationship!=="DIFFERENT_PHOTO_EDITORIAL_ALTERNATIVE"||a?.rows?.[2]?.candidate?.relationship!=="UNIDENTIFIED_ARCHIVE_CANDIDATE")e.push("false_photo_identity");
 return e;
}
function validateCoverage(n,a,old){
 const e=[],c=n?.counts||{};
 if(n?.schema!=="fv-media-exact-coverage-181-v1"||n?.rows?.length!==288||old?.rows?.length!==288)e.push("shape");
 if(c.researched_unique!==181||c.unresearched!==107||c.total_external!==288||c.total_evidence_records!==186||c.new_research_source_rows!==90||c.unique_research_increase!==88)e.push("counts");
 if(c.guest_browser_confirmed_broken!==0||c.guest_browser_confirmed_loaded!==0||c.wire_reduction_76_percent_measured!==false||c.reported_42_broken_browser_confirmed!==false||c.oversized_wp_originals_gt_1500000!==15||c.oversized_stored_original_bytes!==47096779)e.push("unverified_claim");
 if(JSON.stringify(n?.original_six_p0_guest_queue)!==JSON.stringify(P0))e.push("P0_changed");
 if(n?.previous_175_register?.blob_sha!=="ef3c35dcbfc2834d8b7547e5a72a0625428a259e"||n?.batch_sources?.find(x=>x.file==="qa/media-recovery/forrestal_289_six_retriever_dvids_20261110.json")?.blob_sha!=="a12e3b9ce0aab87c17cc7525c86d1482cb0d62f8")e.push("bad_pin");
 const keys=new Set();let researched=0,evidence=0;
 for(let j=0;j<(n?.rows||[]).length;j++){
  const r=n.rows[j],o=old.rows[j];if(keys.has(r.slot))e.push("duplicate_key");keys.add(r.slot);
  if(!o||r.slot!==o.slot||r.stored_url!==o.stored_url||r.post_url!==o.post_url||r.origin_host!==o.origin_host)e.push("source_drift");
  if(r.post_id!==289&&JSON.stringify(r)!==JSON.stringify(o))e.push("old_row_changed");
  if(r.evidence?.length)researched++;evidence+=r.evidence?.length||0;
  if(r.post_id===289){
   const b=a.rows.find(x=>x.slot===r.slot);
   if(!b||r.evidence?.length!==1||r.evidence[0].blob_sha!=="a12e3b9ce0aab87c17cc7525c86d1482cb0d62f8"||r.evidence[0].retriever_only_observation!==b.retrieval.outcome||r.candidate_sources?.[0]?.catalog_url!==b.candidate.catalog_url||r.candidate_sources?.[0]?.item_rights_cleared!==false)e.push("new_provenance_"+r.slot);
  }
  for(const f of ["guest_http_status","guest_current_src","guest_decoded_px","guest_wire_bytes","guest_broken"])if(r[f]!==null)e.push("invented_browser_"+f);
  for(const f of ["rights_cleared","exact_pixel_match_verified","download_authorized","cache_authorized","wordpress_media_upload_authorized","post_rewrite_authorized"])if(r[f]!==false)e.push("unsafe_gate_"+f);
 }
 if(keys.size!==288||researched!==181||evidence!==186)e.push("computed_counts");
 return e;
}
module.exports={validateBatch,validateCoverage};
if(require.main===module){
const fs=require("node:fs"),path=require("node:path");
const read=p=>JSON.parse(fs.readFileSync(path.join(__dirname,p),"utf8"));
const errors=[...validateBatch(read("forrestal_289_six_retriever_dvids_20261110.json"),read("forrestal_289_exact_source_fixture_20261110.json")),...validateCoverage(read("coverage_181_exact_pr1703_20261110.json"),read("forrestal_289_six_retriever_dvids_20261110.json"),read("coverage_175_exact_pr1703_20261110.json"))];
if(errors.length){console.error(errors);process.exitCode=1;}else console.log("PASS six source records and 181/288 ledger; no unsupported guest facts");
}
