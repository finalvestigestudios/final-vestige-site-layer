'use strict';
// Read-only calculation. No browser, media retrieval, cache, WordPress or publication.
const SRC_SHA='925fadb52b873af7e30f48f586f8e743c0a4c10c';
const CSS=[320,390,480,640,768,960],DPR=[1,2,3],W=[480,768,960,1170,1280,1536,1920];
const pos=n=>Number.isSafeInteger(n)&&n>0;
function sourceOK(s){
 if(!s||s.rows?.length!==15||s.counts?.original_bytes_total!==47096779||
    s.counts?.inline_exposed_originals!==11||
    s.counts?.original_bytes_for_five_no_subsizes!==13267538)return false;
 let sum=0,inline=0,missing=0;const ids=new Set();
 for(const r of s.rows){
  if(!pos(r.media_id)||ids.has(r.media_id)||!/^https:\/\/finalvestige\.com\//.test(r.original_url)||
    !pos(r.stored_original_bytes)||r.stored_original_bytes<=1500000||
    r.native_px?.length!==2||!r.native_px.every(pos)||
    !Number.isSafeInteger(r.generated_wp_subsize_count)||
    !Array.isArray(r.published_inline_post_ids)||!Array.isArray(r.published_inline_source_urls)||
    r.actual_guest_wire_bytes!==null||r.actual_guest_http_status!==null||
    r.commercial_reuse_cleared!==false||r.production_edit_allowed!==false)return false;
  ids.add(r.media_id);sum+=r.stored_original_bytes;
  if(r.published_inline_post_ids.length){inline++;if(r.generated_wp_subsize_count===0)missing++;}
 }
 return sum===47096779&&inline===11&&missing===5;
}
function plan(source){
 if(!sourceOK(source))throw Error('FROZEN_SOURCE_INTEGRITY_FAILED');
 const rows=source.rows.map(r=>{
  const [nw,nh]=r.native_px;
  const widths=[...new Set([...W.filter(w=>w<=nw),Math.min(nw,1920)])].sort((a,b)=>a-b);
  const variants=widths.map(w=>[w,Math.min(nh,Math.max(1,Math.round(w*nh/nw)))]);
  const cases=[];
  for(const css_width_px of CSS)for(const dpr of DPR){
   const required_physical_width_px=css_width_px*dpr, native_can_support=required_physical_width_px<=nw;
   const variant=variants.find(v=>v[0]>=required_physical_width_px)||null;
   cases.push({css_width_px,dpr,required_physical_width_px,
    static_960w_sufficient:required_physical_width_px<=Math.min(960,nw),
    native_can_support,proposed_variant_px:variant,
    reason:!native_can_support?'NATIVE_CANNOT_MEET_DPR':
     !variant?'GT_1920_VARIANT_OR_ORIGINAL_REQUIRED':
     required_physical_width_px>960?'PROPOSE_GT_960_VARIANT':'960_GEOMETRY_SUFFICIENT'});
  }
  return {media_id:r.media_id,original_url:r.original_url,stored_original_bytes:r.stored_original_bytes,
   native_px:[nw,nh],wp_registered_subsize_count:r.generated_wp_subsize_count,
   published_inline_post_ids:[...r.published_inline_post_ids],
   published_inline_src:[...r.published_inline_source_urls],
   html_width_hint_px:r.html_width_attribute_hint_px,
   item_rights_review:r.item_rights_review,proposed_variant_dimensions_px:variants,
   geometry_cases:cases,actual_rendered_css_width_px:null,actual_current_src:null,
   actual_guest_http_status:null,actual_guest_wire_bytes:null,
   licensed_for_rehost:false,binaries_created:false,wp_change_allowed:false};
 });
 const missing=rows.filter(r=>r.wp_registered_subsize_count===0&&r.published_inline_post_ids.length);
 const cs=rows.flatMap(r=>r.geometry_cases);
 return {schema:'fv-p1-15-responsive-dpr-matrix-v1',date:'2026-11-12',
  source:{path:'qa/media-recovery/p1_15_responsive_960_feasibility_20261111.json',
   git_blob_sha:SRC_SHA,worklist_pr:183,site_qa_pr:154,media_recovery_pr:1703},
  counts:{originals:15,stored_original_bytes:47096779,published_inline:11,
   other_4_not_proven_unused:4,inline_without_registered_subsizes:5,
   five_png_stored_original_bytes:13267538,conditional_geometry_cases:cs.length,
   cases_960_insufficient:cs.filter(c=>!c.static_960w_sufficient).length,
   cases_native_insufficient:cs.filter(c=>!c.native_can_support).length,
   cases_need_gt1920_or_native:cs.filter(c=>c.reason==='GT_1920_VARIANT_OR_ORIGINAL_REQUIRED').length,
   five_png_native_cannot_meet_css960_dpr2:missing.filter(r=>r.geometry_cases.some(c=>
    c.css_width_px===960&&c.dpr===2&&!c.native_can_support)).length},
  method:{hypothetical_css_widths_px:[...CSS],device_pixel_ratios:[...DPR],
   proposed_widths_px:[...W],maximum_proposed_variant_width_px:1920,
   sizing:'physical width needed = painted CSS width × DPR, bounded by original native width',
   actual_css_and_dpr_unknown:true},
  policy:{p0_six_qa_browser_first:true,all_rights_pending:true,
   no_binaries_generated:true,no_external_media_cached:true,no_wp_writes:true,
   no_deployment:true,actual_76_percent_network_reduction_measured:false,
   reported_42_broken_browser_verified:false},
  rows};
}
function verify(result,source){
 try{return JSON.stringify(result)===JSON.stringify(plan(source))}catch{return false}
}
module.exports={sourceOK,plan,verify,SRC_SHA,CSS,DPR};
