'use strict';
/** Offline incremental 2026-11-01 image-viewer evidence check. Complements existing validate_prinsendam_292.cjs. */
const EXPECTED = ['IMAGE_RENDERED','IMAGE_RENDERED','IMAGE_RENDERED','TIMEOUT_NO_HTTP','IMAGE_RENDERED','WRAPPER_403_NOT_GUEST_BROWSER'];
const NULL_BROWSER = ['current_src','image_get_status','final_url','mime_type','natural_width','natural_height','encoded_transfer_bytes','visibly_broken'];
const FALSE_RELEASE = ['exact_binary_identity_verified','legal_release_confirmed','cache_approved','wordpress_media_upload_approved','post_edit_approved','production_changed'];
function validateRecheck(d, sourceCensus, baseline) {
 const e=[],check=(ok,msg)=>{if(!ok)e.push(msg)};
 check(d?.schema_version===1&&d?.post_id===292&&d?.image_count===6&&d?.external_count===6,'wrong scope');
 check(d?.inventory_blob_sha==='48e1ebf07207e948ba5802e714eb39659d2e1c1d','unknown census SHA');
 check(d?.inventory_trust==='frozen_authenticated_WP_source_census_not_fresh_CMS_readback','invented live CMS verification');
 check(d?.claimed_broken_42_verified===false && d?.claimed_transfer_savings_76_percent_measured===false&&d?.production_repairs===0,'unsupported site-wide claim');
 check(d?.site_qa_browser_ownership==='PR #154','wrong independent QA owner');
 const original=(sourceCensus?.images||[]).filter(x=>x.post_id===292).sort((a,b)=>a.slot-b.slot);
 check(original.length===6&&baseline?.images?.length===6,'missing baseline slots');
 if(!Array.isArray(d?.records)||d.records.length!==6)return [...e,'six records required'];
 const seen=new Set();
 for(let i=0;i<6;i++){
   const r=d.records[i],s=original[i],b=baseline.images[i],p='292:'+i+':';
   check(r?.image_key===p.slice(0,-1)&&r?.slot===i&&!seen.has(r?.image_key),p+'wrong key');seen.add(r?.image_key);
   check(s&&r?.stored_src===s.source_url&&r?.stored_alt===s.alt&&r?.post_url===s.post_url,p+'census mismatch');
   check(b&&b.image_key===r.image_key&&b.stored_url===r.stored_src&&b.stored_alt===r.stored_alt,p+'previous verified source changed');
   check(r?.cms_readback_this_sprint===false,p+'false CMS claim');
   const v=r?.source_retriever||{};
   check(v.method==='web_open_image_renderer_not_guest_browser'&&v.result===EXPECTED[i]&&v.observed_date==='2026-11-01',p+'viewer evidence rewritten');
   check(v.reported_wrapper_code===(i===5?403:null)&&v.origin_http_status===null&&v.guest_browser_http_status===null&&v.encoded_bytes===null,p+'status confusion');
   const a=r?.archive||{},g=r?.geometry||{},guest=r?.guest_browser||{},release=r?.release||{};
   check(a.rights_review==='HOLD'&&a.original_binary_hash===null&&typeof a.identifier==='string'&&a.identifier.length>10,p+'rights/catalog gate');
   check(typeof a.official_record_url==='string'&&a.official_record_url.startsWith('https://')&&typeof a.candidate_catalog_url==='string'&&a.candidate_catalog_url.startsWith('https://'),p+'primary record links');
   check(g.do_not_upscale===true&&g.source==='catalog_metadata_not_current_browser_or_downloaded_binary',p+'geometry evidence provenance');
   const w=g.catalog_candidate_width_px,h=g.catalog_candidate_height_px;
   if(w===null||h===null)check(w===null&&h===null&&g.conditional_target_width_px===null&&g.conditional_target_height_px===null,p+'invented geometry');
   else check(Number.isSafeInteger(w)&&w>0&&Number.isSafeInteger(h)&&h>0&&g.conditional_target_width_px===Math.min(960,w)&&g.conditional_target_height_px===Math.round(h*Math.min(960,w)/w),p+'bad max-960 derivative');
   for(const k of NULL_BROWSER)check(guest[k]===null,p+'invented guest '+k);
   for(const k of FALSE_RELEASE)check(release[k]===false,p+'unauthorized release '+k);
 }
 check(d.records[0].geometry.published_crop_warning.includes('900x675'),'cropped original provenance lost');
 check(d.records[2].archive.relationship==='different_launch_sequence_frame_authoritative_alternative_not_exact','archive candidate misrepresented as exact');
 check(d.records[2].visual_risk.includes('NOT same image'),'published launch vs candidate frame mismatch lost');
 check(d.records[3].archive.official_record_url.includes('File:MS_Prisendam_sinking'),'CG official alternative confused with original photo');
 check(d.records[5].archive.rights_rationale.includes('artist copyright'),'artwork copyright assumption');
 check(Array.isArray(d.visual_comparisons)&&d.visual_comparisons.length===1&&d.visual_comparisons[0].same_image===false&&d.visual_comparisons[0].binary_identity_checked===false&&d.visual_comparisons[0].production_edit_allowed===false,'visual non-identity or false hash assertion');
 return e;
}
module.exports={validateRecheck};
