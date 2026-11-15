'use strict';
const fs = require('node:fs');
function validate(a) {
  const errors=[];
  const reject=(ok,reason)=>{if(!ok)errors.push(reason)};
  const safeUrl=(s)=>{try{return new URL(s)}catch{return null}};
  reject(a?.schema==='fv-432-7-same-accession-20261113-v1','schema');
  reject(a?.site_qa?.pr===154 && a?.site_qa?.do_not_duplicate_collector===true,'siteqa_boundary');
  reject(a?.source_ledger?.git_blob==='c0ec93d75ff6c7d1b655ea1ea1b42bc9c429106f','immutable_source_blob');
  reject(a?.policy?.mark==='Creative Commons Public Domain Mark 1.0 (not a license)' && a?.policy?.production_permission===false,'pdm_not_license');
  reject(Array.isArray(a?.rows) && a.rows.length===7,'seven_rows');
  const seen=new Set();
  for (const r of a?.rows||[]) {
    reject(!seen.has(r.slot),'duplicate_slot:'+r.slot);seen.add(r.slot);
    const old=safeUrl(r.original_published_src), next=safeUrl(r.conditional_apex_host_src), item=safeUrl(r.official_item_url);
    reject(/^432:[0-6]$/.test(r.slot),'invalid_slot:'+r.slot);
    reject(old?.protocol==='https:' && old.hostname==='www.floridamemory.com','original_host:'+r.slot);
    reject(next?.protocol==='https:' && next.hostname==='floridamemory.com','candidate_host:'+r.slot);
    reject(item?.hostname==='floridamemory.com' && /^\/items\/show\/[0-9]+$/.test(item.pathname),'item_url:'+r.slot);
    reject(old && next && old.pathname===next.pathname && old.pathname===r.official_catalog_image_path,'same_catalog_path:'+r.slot);
    reject(r.original_published_src!==r.conditional_apex_host_src,'must_not_confuse_host_alias:'+r.slot);
    reject(r.match_level==='OFFICIAL_CATALOG_SAME_ACCESSION_AND_IMAGE_PATH_NOT_BINARY_MATCH','identity_limit:'+r.slot);
    reject(r.official_item_page_direct_open_retriever_wrapper===403 && r.actual_origin_status===null && r.guest_browser_status===null,'status_provenance:'+r.slot);
    reject(r.native_dimensions_px===null && r.verified_binary_sha256===null && r.measured_transfer_bytes===null,'binary_not_measured:'+r.slot);
    reject(r.output_width_ceiling_px===960 && r.conditional_derivative_dimensions_px===null && r.no_upscale===true,'no_upscale:'+r.slot);
    reject(r.reuse_mark==='PDM_1_0_REPORTED_BY_FLORIDA_MEMORY_SITEWIDE_FAQ' && r.credit_review_pending===true,'rights_hold:'+r.slot);
    reject(r.wordpress_cached_or_hosted===false && r.wordpress_rewrite_authorized===false && r.editorial_scene_signoff===false && r.actual_photo_pixel_parity_proven===false && r.disposition==='HOLD_UNTIL_GUEST_AND_BINARY_RIGHTS_VISUAL_REVIEW','release_hold:'+r.slot);
    reject(typeof r.archive_accession==='string' && r.required_credit.includes(r.archive_accession),'credit:'+r.slot);
  }
  reject(seen.size===7 && [...Array(7)].every((_,i)=>seen.has('432:'+i)),'complete_slots');
  const late=a?.rows?.find(r=>r.slot==='432:6');reject(late?.catalog_date==='2001' && late?.scene_identity.includes('NOT a 1928'),'retrospective_photo_chronology');
  const health=a?.rows?.find(r=>r.slot==='432:3');reject(health?.scene_identity.includes('not established'),'health_response_not_proven');
  reject(a?.performance?.claimed_76pct_wire_reduction_measured===false && a?.performance?.actual_transfer_byte_totals===null,'no_fabricated_byte_saving');
  reject(a?.release?.all_seven_hold===true && a?.release?.wordpress_writes===0 && a?.release?.asset_downloads===0 && a?.release?.subscriptions_spend_usd===0,'no_production_changes');
  return {ok:errors.length===0,errors,checked_rows:Array.isArray(a?.rows)?a.rows.length:0};
}
if(require.main===module){const p=process.argv[2]; if(!p){console.error('Usage: node validate_florida_432_catalog_contract.cjs <audit.json>');process.exit(2)}const r=validate(JSON.parse(fs.readFileSync(p,'utf8')));console.log(JSON.stringify(r,null,2));if(!r.ok)process.exitCode=1;}
module.exports={validate};
