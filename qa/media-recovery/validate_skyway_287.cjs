"use strict";
const STRICT_NULL_FIELDS=["current_src","final_image_url","http_status","content_type","natural_width_px","natural_height_px","encoded_transfer_bytes","visibly_broken","screenshot_evidence_url"];
const EXACT_RELOCATION="https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg";
function validateSkyway(ledger,sourceRows){
 const errors=[];
 const fail=(condition,message)=>{if(!condition)errors.push(message);};
 fail(ledger&&ledger.schema_version===1,"schema");
 fail(ledger?.article?.post_id===287&&ledger?.article?.wp_source_and_alt_matches_frozen===6,"wp readback");
 fail(ledger?.article?.frozen_part_blob_sha==="49183f66f880f7c4dfd363acca906876877f2e5e","census blob identity");
 fail(Array.isArray(sourceRows)&&sourceRows.filter(x=>x.post_id===287).length===6,"frozen input");
 fail(Array.isArray(ledger?.rows)&&ledger.rows.length===6,"row count");
 const rows=Array.isArray(ledger?.rows)?ledger.rows:[];
 const base=Array.isArray(sourceRows)?sourceRows.filter(x=>x.post_id===287).sort((a,b)=>a.slot-b.slot):[];
 const seen=new Set();
 for(let i=0;i<6;i++){
  const r=rows[i]||{},f=base[i]||{};
  fail(r.key===`287:${i}`&&r.key===f.key&&!seen.has(r.key),`key ${i}`);seen.add(r.key);
  fail(r.post_id===287&&r.slot===i,`location ${i}`);
  fail(r.current_published_source_url===f.source_url&&r.source_retriever?.exact_url_checked===f.source_url,`original source URL ${i}`);
  fail(r.current_published_alt===f.alt&&r.live_cms_source_and_alt_verified===true,`original alt ${i}`);
  fail(r.source_retriever?.method==="independent_web_retriever_NOT_guest_browser",`source methodology ${i}`);
  fail(r.source_retriever?.result===(i===5?"RETRIEVER_FETCH_404":"RETRIEVER_IMAGE_DISPLAYED"),`retriever result ${i}`);
  fail(r.source_retriever?.retriever_wrapper_error_code===(i===5?404:null),`retriever wrapper code ${i}`);
  for(let key of ["origin_http_status","visitor_http_status","measured_transfer_bytes","content_type","decoded_original_dimensions"])fail(r.source_retriever?.[key]===null,`unobserved source evidence ${i}.${key}`);
  for(let key of STRICT_NULL_FIELDS)fail(r.guest_browser?.[key]===null,`unobserved browser evidence ${i}.${key}`);
  fail(r.candidate?.proven_binary_same_as_published===false&&r.candidate?.master_sha256===null,`candidate identity ${i}`);
  fail(typeof r.candidate?.primary_record_url==="string"&&r.candidate.primary_record_url.startsWith("https://"),`primary source ${i}`);
  fail(r.rights?.reproduction_clearance==="HOLD"&&r.rights?.caching_clearance==="HOLD",`rights hold ${i}`);
  fail(r.release?.replacement_ready===false&&r.release?.wordpress_media_upload_authorized===false&&r.release?.wordpress_post_edit_authorized===false&&r.release?.homepage_design_changed===false,`release hold ${i}`);
  const g=r.geometry||{};
  fail(g.no_upscale===true&&g.preserve_aspect_ratio===true&&g.target_width_limit_px===960,`size safety ${i}`);
  fail(g.original_master_width_px===null&&g.original_master_height_px===null,`no fabricated original pixels ${i}`);
  fail(g.stored_html_width_px===(f.width_px??null)&&g.stored_html_height_px===(f.height_px??null),`stored html geometry ${i}`);
  fail(g.conditional_target_width_px===null||(Number.isInteger(g.conditional_target_width_px)&&g.conditional_target_width_px>0&&g.conditional_target_width_px<=960),`target width ${i}`);
  fail(g.conditional_target_height_px===null||(Number.isInteger(g.conditional_target_height_px)&&g.conditional_target_height_px>0),`target height ${i}`);
  if(i===0)fail(g.conditional_target_width_px===960&&g.conditional_target_height_px===630&&g.conditional_basis==="stored_html_1024x672_NOT_decoded_master",`conditional geometry ${i}`);
  else fail(g.conditional_target_width_px===null&&g.conditional_target_height_px===null&&g.conditional_basis==="master_dimensions_unknown",`unknown geometry ${i}`);
  if(i===5){
   fail(r.candidate?.asset_url===EXACT_RELOCATION&&r.candidate?.source_relationship==="same_publisher_relocated_same_basename_scene_no_binary_hash","exact relocated publisher candidate");
   fail(r.candidate?.candidate_web_retriever?.method==="independent_web_retriever_NOT_guest_browser"&&r.candidate?.candidate_web_retriever?.result==="RETRIEVER_IMAGE_DISPLAYED"&&r.candidate?.candidate_web_retriever?.origin_http_status===null,"candidate retriever qualification");
   fail(r.visual_integrity?.review_required===true&&/replacement/i.test(r.visual_integrity.note),"later bridge claim review");
   fail(/University Press of Florida/.test(r.rights?.basis||""),"photo credit restriction");
  }else fail(r.candidate?.asset_url===null&&r.candidate?.candidate_web_retriever===null,`no invented asset ${i}`);
  if(i===2)fail(/St. Petersburg Times/.test(r.rights?.basis||""),"graphic copyright source");
  if(i===3)fail(/visually distinct/.test(r.visual_integrity?.note||""),"two distinct photos not deduplicated");
  if(i===4)fail(r.visual_integrity?.review_required===true&&/Venture/.test(r.visual_integrity?.note||""),"court image vessel identification gate");
 }
 const c=ledger?.site_wide_context||{};
 fail(c.published_posts===61&&c.inline_image_slots===355&&c.offsite_image_slots===288&&c.wordpress_originals_over_1_5_mib===13,"census assertions");
 fail(c.originals_over_1_5_mib_total_stored_bytes===43522829&&c.visitor_transfer_bytes===null,"storage is not transfer");
 fail(c.broken_images_reported_42_browser_verified===false&&c.verified_broken_count===null,"false 42 broken");
 fail(c.claimed_76_percent_reduction_measured===false&&c.measured_reduction_percent===null,"false 76 percent");
 fail(c.production_images_repaired===0,"false repairs");
 fail(ledger?.source_retriever_provenance?.method==="web_open_original_url_2026_11_01","retriever provenance");
 fail(ledger?.authoritative_related_records?.some(x=>x.record_id?.includes("DCA80AM050"))===true,"NTSB primary record");
 return {ok:errors.length===0,errors};
}
module.exports={validateSkyway};
if(require.main===module){const path=require("node:path");const data=require("./skyway_287_source_relocation_20261101.json");const source=require("./parts/03.json");const result=validateSkyway(data,source.images);console.log(JSON.stringify(result));process.exitCode=result.ok?0:1;}
