"use strict";
const old=require("./coverage_167_exact_pr1703_20261110.json");
const batch=require("./courrieres_425_eight_catalog_20261110.json");
const EXPECTED_P0=["285:5","285:2","287:5","418:1","418:2","407:1"];
function validate(a) {
 const e=[];
 if(a?.schema!=="fv-media-exact-coverage-175-v1"||a?.previous_167_register?.blob_sha!=="d2337c38aa15903b11b4aae02a2a1f09534cb752")e.push("header_or_prior_sha");
 if(!Array.isArray(a?.rows)||a.rows.length!==288)return e.concat("exactly_288_rows_required");
 const oldMap=new Map(old.rows.map(r=>[r.slot,r])),batchMap=new Map(batch.rows.map(r=>[r.slot,r]));
 const seen=new Set();let researched=0,evidence=0,updated=0;
 for(const r of a.rows){
  if(seen.has(r.slot))e.push("duplicate_slot_"+r.slot);seen.add(r.slot);
  const p=oldMap.get(r.slot),b=batchMap.get(r.slot);
  if(!p||r.stored_url!==p.stored_url||r.post_id!==p.post_id||r.post_url!==p.post_url||r.origin_host!==p.origin_host)e.push("source_identity_"+r.slot);
  if(r.guest_http_status!==null||r.guest_current_src!==null||r.guest_decoded_px!==null||r.guest_wire_bytes!==null||r.guest_broken!==null)e.push("fake_guest_evidence_"+r.slot);
  for(const k of ["rights_cleared","exact_pixel_match_verified","download_authorized","cache_authorized","wordpress_media_upload_authorized","post_rewrite_authorized"])if(r[k]!==false)e.push("unsafe_release_"+r.slot+"_"+k);
  if(b){
   updated++;
   if(p.evidence.length!==0||p.candidate_sources.length!==0||r.evidence.length!==1||r.candidate_sources.length!==1)e.push("new_batch_overlap_"+r.slot);
   const ev=r.evidence[0],c=r.candidate_sources[0];
   if(ev?.blob_sha!=="15d8642626ec509bdba7c1f4812f664cc3eff584"||ev?.path!=="qa/media-recovery/courrieres_425_eight_catalog_20261110.json"||ev?.retriever_only_observation!=="TOOL_INACCESSIBLE_NOT_ORIGIN_HTTP")e.push("batch_evidence_"+r.slot);
   if(c?.catalog_url!==b.catalog.file_page_url||JSON.stringify(c?.conditional_960px)!==JSON.stringify(b.conditional_sizing.target_px)||c?.exact_image_match_verified!==false||c?.item_rights_cleared!==false||c?.authoritative_primary_url!==b.catalog.primary_source_candidate)e.push("batch_rights_geometry_"+r.slot);
  }else if(JSON.stringify(r)!==JSON.stringify(p))e.push("prior_row_changed_"+r.slot);
  researched+=r.evidence.length>0?1:0;
  evidence+=r.evidence.length;
 }
 if(updated!==8||seen.size!==288)e.push("eight_new_only");
 const c=a.counts||{};
 if(researched!==175||evidence!==180||c.researched_unique!==175||c.unresearched!==113||c.total_external!==288||c.total_evidence_records!==180||c.new_research_source_rows!==84||c.duplicated_with_prior!==2||c.unique_research_increase!==82)e.push("count_mismatch");
 if(JSON.stringify(a.original_six_p0_guest_queue)!==JSON.stringify(EXPECTED_P0))e.push("p0_queue_changed");
 if(c.guest_browser_confirmed_broken!==0||c.guest_browser_confirmed_loaded!==0||c.reported_42_broken_browser_confirmed!==false||c.wire_reduction_76_percent_measured!==false||c.oversized_wp_originals_gt_1500000!==15||c.oversized_stored_original_bytes!==47096779)e.push("unsupported_outcome");
 const entry=a.batch_sources?.find(z=>z.file==="qa/media-recovery/courrieres_425_eight_catalog_20261110.json");
 if(!entry||entry.blob_sha!=="15d8642626ec509bdba7c1f4812f664cc3eff584"||entry.source_records!==8)e.push("batch_source_pin");
 return e;
}
module.exports={validate};
if(require.main===module){const fs=require("node:fs"),path=require("node:path");const a=JSON.parse(fs.readFileSync(path.join(__dirname,"coverage_175_exact_pr1703_20261110.json"),"utf8"));const e=validate(a);if(e.length){console.error(e);process.exit(1);}console.log("PASS: 175/288 exact source research, 113 pending, no false broken/transfer claims");}
