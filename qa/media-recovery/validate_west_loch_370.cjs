"use strict";
// Closed-world validator; all observations unavailable in guest browser remain null.
const IDS=Object.freeze(["80-G-276907","80-G-202485","SC 185701","80-G-276940","SC 427947","80-G-276945","SC 276944",null]);
const EXTERNAL=new Set([0,1,3,4]);
function validate(data,census){
 const errors=[];const err=(s)=>errors.push(s);
 if(!data||data.schema_version!==1||data.post_id!==370||!Array.isArray(data.records)||data.records.length!==8)return ["invalid_batch"];
 const f=(census?.images||[]).filter(x=>x.post_id===370).sort((a,b)=>a.slot-b.slot);
 if(f.length!==8)err("missing_frozen_census");
 const site=data.prior_sitewide_inventory||{},check=data.wp_readonly_source_matches||{};
 if(site.posts!==61||site.images!==355||site.offsite!==288||site.oversized_originals!==13||site.reported_42_broken_browser_verified!==false||site.reported_76pct_savings_measured!==false)err("sitewide_claim_unverified");
 if(check.images!==8||check.src!==8||check.full_alt!==8)err("editor_readback_incomplete");
 const seen=new Set();
 for(const [i,r] of data.records.entries()){
  const x=f[i],key="370:"+i,external=EXTERNAL.has(i);
  if(!r||r.key!==key||r.slot!==i||r.post_id!==370||seen.has(r.key))err("slot_"+i);
  seen.add(r?.key);
  if(!x||r.source_url!==x.source_url||r.alt!==x.alt||r.source_host!==x.source_host||r.source_kind!==x.source_kind||r.post_url!==x.post_url)err("source_mismatch_"+i);
  if(r.catalog_id!==IDS[i])err("catalog_id_"+i);
  if(external){
   if(r.source_host!=="www.history.navy.mil"||r.source_kind!=="external"||r.catalog_match!=="exact_id_in_source")err("external_identity_"+i);
   const q=r.source_url?.match(/[?&]image=([^&]+)/)?.[1]||"";
   let path="";try{path=decodeURIComponent(q)}catch(e){err("invalid_image_url_"+i)}
   if(!path.endsWith("/"+IDS[i].replaceAll(" ","-")))err("photo_id_absent_in_src_"+i);
   if(!r.authoritative_record_url?.startsWith("https://www.history.navy.mil/")||!r.authoritative_record_url?.includes(IDS[i].replaceAll(" ","-")))err("official_record_invalid_"+i);
  }else{
   if(r.source_host!=="finalvestige.com"||r.source_kind!=="first_party"||r.catalog_match==="exact_id_in_source")err("firstparty_overclaim_"+i);
   if(i===7&&(r.authoritative_record_url!==null||r.attribution_candidate!==null||r.catalog_match!=="unmatched"))err("invented_headstone_source");
  }
  if(r.rights_review!=="HOLD_item_level"||r.asset_sha256!==null||r.asset_copied!==false||r.wp_upload_authorized!==false||r.post_rewrite_authorized!==false)err("rights_or_release_"+i);
  if(r.rights_policy_urls?.length!==2||!r.rights_policy_urls?.some(u=>u.startsWith("https://www.archives.gov/")))err("rights_policy_"+i);
  for(const k of ["visitor_current_src","visitor_http_status","visitor_content_type","visitor_encoded_bytes","visitor_natural_width","visitor_broken","derivative_dimensions_px"]){if(r[k]!==null)err("invented_"+k+"_"+i)}
  if(r.max_width_px!==960)err("960_width_limit_"+i);
  const p=r.conditional_960_derivative;
  if(p!==null&&(!Number.isInteger(p?.catalog_master_w)||!Number.isInteger(p?.catalog_master_h)||p.catalog_master_w<960||p.catalog_master_h<1||p.conditional_w!==960||p.conditional_h!==Math.round(p.catalog_master_h*960/p.catalog_master_w)||p.basis!=="NHHC_high_TIFF_metadata_only_not_binary_verified"))err("unsafe_conditional_size_"+i);
  if(typeof r.historical_note!=="string"||r.historical_note.length<36)err("historical_caveat_"+i);
 }
 if(!data.records[1].historical_note.includes("NOT a May 1944 West Loch fire image"))err("historic_date_misrepresented");
 if(!data.records[4].historical_note.includes("probably"))err("uncertain_uscg_identity_misrepresented");
 return errors;
}
module.exports={validate};
